"""CareerOS AI — Streamlit front-end.

All business logic lives in the ``careeros`` package; this file is the
presentation layer only. Results are rendered from ``st.session_state`` so they
survive every rerun (button clicks, filter changes, pagination).
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import streamlit as st

from careeros import __version__
from careeros.ai import AIClient, MODELS
from careeros.export import applications_to_csv, jobs_to_csv, jobs_to_markdown
from careeros.matching import DIMENSION_MAX, priority_band
from careeros.profile import CEFR_ORDER, Profile
from careeros.salary import format_salary
from careeros.search import (
    CAREER_PRESETS,
    FilterOptions,
    SearchRequest,
    build_search_queries,
    run_search,
    score_and_filter,
)
from careeros.sources import PROVIDERS
from careeros.text import canonical_url, clean_html_text, safe_company_name, truncate
from careeros.tracker import STATUS_FLOW, ApplicationStore

st.set_page_config(
    page_title="CareerOS AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SECRETS (never crash when secrets.toml is absent)
# =========================================================
def get_secret(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, default) or default)
    except Exception:
        return default


SECRETS = {
    key: get_secret(key)
    for key in (
        "JOOBLE_API_KEY", "ADZUNA_APP_ID", "ADZUNA_APP_KEY",
        "CAREERJET_AFFID", "CLAUDE_API_KEY",
    )
}


# =========================================================
# SESSION STATE
# =========================================================
def init_session() -> None:
    defaults = {
        "results": [],            # scored + filtered jobs (rendered every rerun)
        "raw_jobs": [],           # deduplicated jobs before scoring
        "report": None,           # SearchReport of the last search
        "filter_stats": {},
        "visible_count": 10,
        "ai_cache": {},           # {(url, kind): text}
        "search_nonce": 0,        # bumped by "Force refresh" to bypass caching
        "last_search_at": "",
        "last_signature": None,
        "has_searched": False,
        "toast_queue": [],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    if "profile" not in st.session_state:
        st.session_state.profile = Profile()
    if "store" not in st.session_state:
        st.session_state.store = ApplicationStore.load()


init_session()

PROFILE: Profile = st.session_state.profile
STORE: ApplicationStore = st.session_state.store
AI = AIClient(SECRETS["CLAUDE_API_KEY"], st.session_state.get("ai_model", MODELS["Fast & cheap (Haiku 3.5)"]))


# =========================================================
# HELPERS
# =========================================================
def current_filters() -> FilterOptions:
    return FilterOptions(
        min_score=st.session_state.get("f_min_score", 20),
        location_filter=st.session_state.get("f_location", "All"),
        romanian_filter=st.session_state.get("f_romanian", "Any"),
        max_age_days=st.session_state.get("f_max_age", 0),
        only_with_salary=st.session_state.get("f_salary_only", False),
        hide_applied=st.session_state.get("f_hide_applied", False),
        applied_urls=STORE.urls(),
        sort_by=st.session_state.get("f_sort", "Best match"),
    )


def filter_signature() -> tuple:
    """Everything that can change the result list without a new API call."""
    options = current_filters()
    return (
        id(st.session_state.raw_jobs),
        len(st.session_state.raw_jobs),
        options.min_score, options.location_filter, options.romanian_filter,
        options.max_age_days, options.only_with_salary, options.sort_by,
        options.hide_applied, len(STORE) if options.hide_applied else 0,
        PROFILE.target_salary_min, PROFILE.target_salary_max,
        PROFILE.romanian_level, PROFILE.location,
        PROFILE.experience_years, PROFILE.open_to_relocation,
    )


def rescore_results(force: bool = False) -> None:
    """Re-apply scoring and filters to the last raw results (no network call).

    Driven by a signature comparison rather than widget callbacks alone, so the
    list stays correct however the state was changed.
    """
    if not st.session_state.raw_jobs:
        st.session_state.results = []
        return
    signature = filter_signature()
    if not force and signature == st.session_state.get("last_signature"):
        return
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
    st.session_state.results = jobs
    st.session_state.filter_stats = stats
    st.session_state.last_signature = signature
    st.session_state.visible_count = max(10, min(st.session_state.get("visible_count", 10), len(jobs) or 10))


def run_new_search(request: SearchRequest) -> None:
    with st.status("Searching across sources…", expanded=True) as status:
        st.write(f"Queries: {', '.join(request.resolved_queries())}")
        report = run_search(request)
        st.session_state.report = report
        st.session_state.raw_jobs = report.jobs
        st.session_state.has_searched = True
        st.session_state.visible_count = 10
        st.session_state.last_search_at = datetime.now().strftime("%H:%M:%S")

        counts = report.counts_by_source
        if counts:
            summary = " | ".join(f"{name}: {count}" for name, count in sorted(counts.items()))
            status.update(label=f"✅ {summary}", state="complete")
        else:
            status.update(label="⚠️ No source returned results", state="error")

    rescore_results(force=True)


def ai_key(url: str, kind: str) -> str:
    return f"{kind}::{canonical_url(url) or url}"


def run_ai(kind: str, job: Dict, match, label: str) -> None:
    """Run an AI helper and cache the result so reruns keep showing it."""
    key = ai_key(job.get("redirect_url", ""), kind)
    with st.spinner(f"{label}…"):
        if kind == "analysis":
            result = AI.analyze_job(job, match, PROFILE)
        elif kind == "cover":
            result = AI.cover_letter(job, match, PROFILE)
        elif kind == "cv":
            result = AI.cv_bullets(job, match, PROFILE)
        else:
            result = AI.interview_prep(job, match, PROFILE)
    st.session_state.ai_cache[key] = result.text if result.ok else f"❌ {result.error}"


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("🎯 CareerOS AI")
    st.caption(f"v{__version__}")

    st.subheader("🎯 Search strategy")
    preset = st.radio(
        "Career track",
        list(CAREER_PRESETS.keys()),
        index=0,
        help="A preset runs several related queries at once. Pick 'Custom keywords' to type your own.",
    )
    is_custom = "Custom" in preset
    keywords = st.text_input(
        "Keywords" if is_custom else "Keywords (override the preset)",
        value="customer support" if is_custom else "",
        placeholder="e.g. accounts payable",
    )
    location = st.text_input("📍 Location", value=PROFILE.location)
    limit_per_source = st.slider("Results per source", 5, 50, 20, 5)
    expand_queries = st.checkbox(
        "🔄 Expand keywords automatically", value=True,
        help="Adds related search terms, e.g. 'customer support' → 'client support'.",
    )

    st.divider()
    st.subheader("🔗 Sources")
    selected_sources: List[str] = []
    for key, spec in PROVIDERS.items():
        missing = [k for k in spec.needs_keys if not SECRETS.get(k)]
        disabled = bool(missing)
        label = spec.label + (" 🔒" if disabled else "")
        checked = st.checkbox(
            label,
            value=spec.default_on and not disabled,
            disabled=disabled,
            help=(f"Needs: {', '.join(missing)}" if missing else spec.help_text),
            key=f"src_{key}",
        )
        if checked and not disabled:
            selected_sources.append(key)

    st.divider()
    st.subheader("📌 Filters")
    st.caption("Filters re-apply instantly — no new API calls.")
    st.slider("Minimum match %", 0, 100, 20, 5, key="f_min_score", on_change=rescore_results)
    st.selectbox(
        "Location filter", ["All", "Timișoara", "Romania", "Remote", "Europe"],
        key="f_location", on_change=rescore_results,
    )
    st.radio(
        "Romanian requirement",
        ["Any", "Exclude Romanian-required", "Beginner-friendly only"],
        key="f_romanian", on_change=rescore_results,
    )
    st.select_slider(
        "Maximum age", options=[0, 3, 7, 14, 30, 60],
        value=0, format_func=lambda d: "Any age" if d == 0 else f"≤ {d} days",
        key="f_max_age", on_change=rescore_results,
    )
    st.checkbox("💰 Only jobs with a published salary", key="f_salary_only", on_change=rescore_results)
    st.checkbox("🙈 Hide jobs I already applied to", key="f_hide_applied", on_change=rescore_results)
    st.selectbox(
        "Sort by", ["Best match", "Newest first", "Highest salary"],
        key="f_sort", on_change=rescore_results,
    )

    st.divider()
    st.subheader("👤 Profile")
    with st.expander("Edit your profile"):
        with st.form("profile_form"):
            p_location = st.text_input("Base city", PROFILE.location)
            p_exp = st.number_input("Years of experience", 0, 50, PROFILE.experience_years)
            p_rom = st.selectbox(
                "Romanian level", CEFR_ORDER,
                index=CEFR_ORDER.index(PROFILE.romanian_level) if PROFILE.romanian_level in CEFR_ORDER else 1,
            )
            p_eng = st.selectbox(
                "English level", CEFR_ORDER,
                index=CEFR_ORDER.index(PROFILE.english_level) if PROFILE.english_level in CEFR_ORDER else 4,
            )
            p_min = st.number_input("Min salary (RON/month)", 0, 100_000, PROFILE.target_salary_min, step=500)
            p_max = st.number_input("Max salary (RON/month)", 0, 100_000, PROFILE.target_salary_max, step=500)
            p_remote = st.checkbox("Open to remote work", PROFILE.open_to_remote)
            p_reloc = st.checkbox("Open to relocation", PROFILE.open_to_relocation)
            if st.form_submit_button("💾 Save profile", use_container_width=True):
                PROFILE.location = p_location
                PROFILE.experience_years = int(p_exp)
                PROFILE.romanian_level = p_rom
                PROFILE.english_level = p_eng
                PROFILE.target_salary_min = int(p_min)
                PROFILE.target_salary_max = int(max(p_max, p_min))
                PROFILE.open_to_remote = p_remote
                PROFILE.open_to_relocation = p_reloc
                st.session_state.profile = PROFILE
                rescore_results()
                st.success("Profile saved — results re-scored.")

    st.divider()
    st.subheader("🤖 AI assistant")
    model_label = st.selectbox("Claude model", list(MODELS.keys()), index=0)
    st.session_state.ai_model = MODELS[model_label]
    if not AI.enabled:
        st.caption("⚪ Add `CLAUDE_API_KEY` to Secrets to unlock AI features.")

    st.divider()
    with st.expander("🔐 API status"):
        for key, spec in PROVIDERS.items():
            missing = [k for k in spec.needs_keys if not SECRETS.get(k)]
            if not spec.needs_keys:
                st.write(f"{spec.label}: ✅ free")
            elif missing:
                st.write(f"{spec.label}: ⚪ needs {', '.join(missing)}")
            else:
                st.write(f"{spec.label}: ✅ configured")
        st.write(f"Claude: {'✅ configured' if AI.enabled else '⚪ optional'}")
        if not STORE.persistent:
            st.warning("Storage is read-only here — applications persist for this session only. Export the CSV to keep them.")


# =========================================================
# HEADER + SEARCH BAR
# =========================================================
st.title("🎯 CareerOS AI")
st.caption("Multi-source job search, profile-aware ranking, and application tracking for the Romanian & EU market.")

search_col, refresh_col, clear_col = st.columns([3, 1, 1])
with search_col:
    do_search = st.button("🔎 Search jobs", type="primary", use_container_width=True)
with refresh_col:
    do_refresh = st.button("🔄 Force refresh", use_container_width=True,
                           help="Bypass cached responses and re-query every source.")
with clear_col:
    if st.button("🧹 Clear", use_container_width=True, help="Clear the current results."):
        st.session_state.results = []
        st.session_state.raw_jobs = []
        st.session_state.report = None
        st.session_state.has_searched = False
        st.rerun()

if do_refresh:
    st.session_state.search_nonce += 1
    st.cache_data.clear()
    do_search = True

if do_search:
    if not selected_sources:
        st.error("Select at least one source in the sidebar.")
    else:
        active_preset = "" if (is_custom or keywords.strip()) else preset
        run_new_search(SearchRequest(
            keywords=keywords.strip(),
            location=location.strip() or PROFILE.location,
            preset=active_preset,
            limit_per_source=limit_per_source,
            sources=selected_sources,
            expand_queries=expand_queries,
            secrets=SECRETS,
        ))


# =========================================================
# SEARCH DIAGNOSTICS
# =========================================================
report = st.session_state.report
if report is not None:
    errors = report.errors
    blocking = [e for e in errors if "skipped" not in e.lower()]
    if blocking:
        with st.expander(f"⚠️ {len(blocking)} source issue(s)", expanded=not report.jobs):
            for err in blocking:
                st.warning(err)

    if report.jobs:
        with st.expander("📡 Source report"):
            cols = st.columns(max(1, len(report.counts_by_source) or 1))
            for col, (name, count) in zip(cols, sorted(report.counts_by_source.items())):
                col.metric(name, count, help=f"{report.timings.get(name, 0)} ms")
            st.caption(
                f"{report.raw_count} raw results · {report.duplicates_removed} duplicates merged · "
                f"queries: {', '.join(report.queries)} · last run {st.session_state.last_search_at}"
            )


# =========================================================
# RESULTS
# =========================================================
# Keep the rendered list in sync with state on every rerun. This is what makes
# results survive button clicks, pagination and profile edits.
rescore_results()

results: List[Dict] = st.session_state.results
stats: Dict[str, int] = st.session_state.filter_stats or {}


def render_job_card(index: int, job: Dict) -> None:
    match = job["_match"]
    url = job.get("redirect_url", "")
    title = job.get("title", "Untitled")
    company = safe_company_name(job.get("company"))
    job_location = (job.get("location") or {}).get("display_name", "Not specified")
    label, _band = priority_band(match.score, match.confidence)
    is_applied = url in STORE

    with st.container(border=True):
        head, badge = st.columns([5, 2])
        with head:
            st.markdown(f"### {index}. {title}")
            st.markdown(f"**{company}** · 📍 {job_location}")
        with badge:
            st.metric("Match", f"{match.score}%", label)
            if is_applied:
                st.success("✅ Applied", icon="✅")

        st.progress(match.score / 100)

        meta = []
        meta.append(f"🌐 {job.get('source', 'n/a')}")
        age = job.get("age_days")
        if isinstance(age, (int, float)):
            meta.append("🆕 today" if age == 0 else f"📅 {int(age)}d ago")
        salary_display = format_salary(match.salary) if match.salary else "Not specified"
        meta.append(f"💰 {salary_display}")
        confidence_icon = {"high": "🎯 high confidence", "medium": "🔍 medium confidence", "low": "❓ short listing"}
        meta.append(confidence_icon.get(match.confidence, ""))
        if job.get("duplicate_count", 1) > 1:
            meta.append(f"🔁 seen on {job['duplicate_count']} boards")
        if job.get("variant_count", 1) > 1:
            locations = ", ".join(job.get("variant_locations", [])[:4])
            extra = f" ({locations})" if locations else ""
            meta.append(f"🌍 same role posted for {job['variant_count']} countries{extra}")
        st.caption(" · ".join(m for m in meta if m))

        if match.warnings:
            st.warning(" · ".join(match.warnings[:2]))

        tab_why, tab_score, tab_desc, tab_ai = st.tabs(
            ["✅ Why it matches", "📊 Breakdown", "📄 Description", "🤖 AI tools"]
        )

        with tab_why:
            if match.reasons:
                for reason in match.reasons:
                    st.markdown(f"- {reason}")
            else:
                st.info("No strong positive signals found — this is a low-evidence match.")
            if match.warnings:
                st.markdown("**Check before applying**")
                for warning in match.warnings:
                    st.markdown(f"- {warning}")

        with tab_score:
            dim_labels = {
                "location": "📍 Location", "skills": "💼 Skills", "arabic": "🗣️ Arabic",
                "english": "🇬🇧 English", "experience": "🧑‍💼 Experience",
                "salary": "💰 Salary", "education": "🎓 Education", "relevance": "🌐 Relevance",
            }
            cols = st.columns(4)
            for i, (dim, value) in enumerate(match.dimensions.items()):
                cols[i % 4].metric(dim_labels.get(dim, dim), f"{value}/{DIMENSION_MAX.get(dim, 10)}")
            if match.adjustments:
                st.caption("Adjustments: " + ", ".join(f"{name} ({value:+d})" for name, value in match.adjustments))

        with tab_desc:
            description = clean_html_text(job.get("description", ""))
            if description:
                st.write(truncate(description, 2500))
            else:
                st.info("This source only provides a short snippet. Open the listing for the full text.")

        with tab_ai:
            if not AI.enabled:
                st.info("Add `CLAUDE_API_KEY` to Streamlit Secrets to enable AI analysis, cover letters and CV tailoring.")
            else:
                ai_cols = st.columns(4)
                actions = [
                    ("analysis", "🤖 Analyse fit", "Analysing the role"),
                    ("cover", "✍️ Cover letter", "Writing the cover letter"),
                    ("cv", "📝 Tailor CV", "Tailoring CV bullets"),
                    ("interview", "🎤 Interview prep", "Preparing interview notes"),
                ]
                for col, (kind, btn_label, spinner) in zip(ai_cols, actions):
                    if col.button(btn_label, key=f"{kind}_{index}_{canonical_url(url)}", use_container_width=True):
                        run_ai(kind, job, match, spinner)
                for kind, btn_label, _ in actions:
                    cached = st.session_state.ai_cache.get(ai_key(url, kind))
                    if cached:
                        with st.expander(f"{btn_label} — result", expanded=True):
                            st.markdown(cached)
                            st.download_button(
                                "⬇️ Download",
                                cached,
                                file_name=f"{kind}_{company[:20].replace(' ', '_')}.md",
                                key=f"dl_{kind}_{index}_{canonical_url(url)}",
                            )

        action_1, action_2, action_3 = st.columns([1, 1, 2])
        with action_1:
            if url:
                st.link_button("📩 View & apply", url, use_container_width=True)
        with action_2:
            if is_applied:
                if st.button("↩️ Untrack", key=f"untrack_{index}_{canonical_url(url)}", use_container_width=True):
                    STORE.remove(url)
                    st.rerun()
            else:
                if st.button("✅ Mark applied", key=f"apply_{index}_{canonical_url(url)}",
                             type="secondary", use_container_width=True):
                    STORE.add(
                        url=url, title=title, company=company, location=job_location,
                        source=job.get("source", ""), match_score=match.score,
                    )
                    st.toast(f"Tracked: {title}", icon="✅")
                    st.rerun()
        with action_3:
            if is_applied:
                app = STORE.get(url)
                new_status = st.selectbox(
                    "Status", STATUS_FLOW,
                    index=STATUS_FLOW.index(app.status) if app and app.status in STATUS_FLOW else 0,
                    key=f"status_{index}_{canonical_url(url)}",
                    label_visibility="collapsed",
                )
                if app and new_status != app.status:
                    STORE.update(url, status=new_status)
                    st.rerun()


if results:
    high = sum(1 for j in results if j["_match"].score >= 70)
    medium = sum(1 for j in results if 45 <= j["_match"].score < 70)
    fresh = sum(1 for j in results if isinstance(j.get("age_days"), (int, float)) and j["age_days"] <= 7)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Matches", len(results))
    m2.metric("🔥 High priority", high)
    m3.metric("🟡 Worth a look", medium)
    m4.metric("🆕 Posted this week", fresh)
    m5.metric("📋 Tracked", len(STORE))

    filtered_out = sum(stats.values())
    if filtered_out:
        st.caption(
            f"Filtered out {filtered_out}: "
            f"{stats.get('rejected_hard', 0)} wrong track/language · "
            f"{stats.get('below_score', 0)} below {st.session_state.get('f_min_score', 20)}% · "
            f"{stats.get('filtered_location', 0)} location · "
            f"{stats.get('filtered_romanian', 0)} Romanian · "
            f"{stats.get('filtered_age', 0)} too old · "
            f"{stats.get('filtered_salary', 0)} no salary · "
            f"{stats.get('filtered_applied', 0)} already applied"
        )

    exp1, exp2, exp3 = st.columns(3)
    exp1.download_button(
        "📥 Results CSV", jobs_to_csv(results, STORE.urls()),
        f"careeros_results_{datetime.now():%Y%m%d}.csv", "text/csv", use_container_width=True,
    )
    exp2.download_button(
        "📄 Shortlist (Markdown)", jobs_to_markdown(results),
        f"careeros_shortlist_{datetime.now():%Y%m%d}.md", "text/markdown", use_container_width=True,
    )
    if len(STORE):
        exp3.download_button(
            "📋 Applications CSV", applications_to_csv(STORE.all()),
            f"careeros_applications_{datetime.now():%Y%m%d}.csv", "text/csv", use_container_width=True,
        )

    st.divider()
    st.subheader("🎯 Recommended jobs")

    visible = min(st.session_state.visible_count, len(results))
    for position, job in enumerate(results[:visible], start=1):
        render_job_card(position, job)

    if visible < len(results):
        if st.button(f"📄 Load more ({len(results) - visible} remaining)", use_container_width=True):
            st.session_state.visible_count += 10
            st.rerun()
    st.caption(f"Showing {visible} of {len(results)} matches.")

elif st.session_state.has_searched:
    st.warning("No jobs passed your filters.")
    st.markdown(
        "**Try this:**\n"
        f"- Lower *Minimum match %* (currently {st.session_state.get('f_min_score', 20)}%)\n"
        "- Set *Location filter* to **All**\n"
        "- Set *Romanian requirement* to **Any**\n"
        "- Enable more sources in the sidebar\n"
        "- Use broader keywords, e.g. `support` instead of `arabic customer support`"
    )
else:
    st.info("👈 Pick a career track and press **Search jobs** to begin.")
    with st.expander("How the matching works", expanded=True):
        st.markdown(
            """
Each job is scored out of 100 from **positive evidence only** — a missing detail
scores zero rather than granting free points:

| Dimension | Max | What earns points |
|---|---|---|
| 📍 Location | 20 | Your city > Romania > EU-eligible remote |
| 💼 Skills | 25 | Operations, finance/compliance, logistics, tools |
| 🗣️ Arabic | 15 | Required > preferred > a plus > mentioned |
| 🇬🇧 English | 10 | Required > preferred > mentioned |
| 🧑‍💼 Experience | 10 | Seniority in the title vs. years requested |
| 💰 Salary | 10 | Parsed and converted to RON/month |
| 🎓 Education | 5 | Law/legal or degree requirements |
| 🌐 Relevance | 5 | BPO, shared services, MENA exposure |

Jobs requiring advanced Romanian, or remote roles restricted to another region,
are rejected before scoring. Fresh postings get a small boost; listings older
than 45 days are penalised.
            """
        )


# =========================================================
# APPLICATION TRACKER
# =========================================================
st.divider()
st.subheader("📋 Application tracker")

if not len(STORE):
    st.caption("No applications tracked yet — press **Mark applied** on any job.")
else:
    tracker_stats = STORE.stats()
    cols = st.columns(6)
    cols[0].metric("Total", tracker_stats.get("Total", 0))
    cols[1].metric("Active", tracker_stats.get("Active", 0))
    for col, status in zip(cols[2:], ["Screening", "Interview", "Offer", "Rejected"]):
        col.metric(status, tracker_stats.get(status, 0))

    status_filter = st.multiselect("Filter by status", STATUS_FLOW, default=[])
    for app in STORE.all():
        if status_filter and app.status not in status_filter:
            continue
        with st.container(border=True):
            info, status_col, remove_col = st.columns([4, 2, 1])
            with info:
                st.markdown(f"**{app.title or 'Untitled'}** — {app.company}")
                st.caption(
                    f"📅 applied {app.applied_at or 'n/a'} · 🎯 {app.match_score}% · "
                    f"🌐 {app.source or 'n/a'}" + (f" · 📍 {app.location}" if app.location else "")
                )
                if app.url:
                    st.markdown(f"[Open listing]({app.url})")
            with status_col:
                new_status = st.selectbox(
                    "Status", STATUS_FLOW,
                    index=STATUS_FLOW.index(app.status) if app.status in STATUS_FLOW else 0,
                    key=f"tracker_status_{canonical_url(app.url)}",
                    label_visibility="collapsed",
                )
                if new_status != app.status:
                    STORE.update(app.url, status=new_status)
                    st.rerun()
            with remove_col:
                if st.button("🗑️", key=f"del_{canonical_url(app.url)}", help="Remove"):
                    STORE.remove(app.url)
                    st.rerun()

            notes = st.text_area(
                "Notes", value=app.notes, key=f"notes_{canonical_url(app.url)}",
                placeholder="Recruiter name, interview date, follow-up reminder…",
                height=70, label_visibility="collapsed",
            )
            if notes != app.notes:
                STORE.update(app.url, notes=notes)


# =========================================================
# FOOTER
# =========================================================
st.divider()
with st.expander("🎯 Your profile summary"):
    left, right = st.columns(2)
    with left:
        st.write(f"**Candidate:** {PROFILE.name}")
        st.write(f"📍 **Base:** {PROFILE.location}, {PROFILE.country}")
        st.write(f"🎓 **Education:** {PROFILE.education}")
        st.write(f"💼 **Experience:** {PROFILE.experience_years}+ years")
    with right:
        st.write(f"🗣️ **Arabic:** {PROFILE.arabic_level}")
        st.write(f"🇬🇧 **English:** {PROFILE.english_level}")
        st.write(f"🇷🇴 **Romanian:** {PROFILE.romanian_level}")
        st.write(f"💰 **Target:** {PROFILE.target_salary_min:,}–{PROFILE.target_salary_max:,} RON/month")

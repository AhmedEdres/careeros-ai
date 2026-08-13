from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, List

import streamlit as st

from careeros_v3_engine import (
    PROFILE,
    CAREER_FAMILIES,
    JoobleAdapter,
    RemotiveAdapter,
    canonical_url,
    clean_text,
    rank_jobs,
)

st.set_page_config(page_title="CareerOS AI v3", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")


def init_state():
    defaults = {
        "jobs": [],
        "rejected": [],
        "stats": {},
        "searched": False,
        "applied": {},
        "last_search": "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


init_state()

st.title("🎯 CareerOS AI")
st.caption("v3 — source adapters → normalization → deduplication → hard eligibility → career-family intelligence → ranking")

with st.sidebar:
    st.header("🎯 Search strategy")
    track = st.radio("Career track", ["Full Career Scan"] + list(CAREER_FAMILIES.keys()), index=0)
    custom = st.text_input("Keywords", value="" if track == "Full Career Scan" else track)
    location = st.text_input("📍 Location", value=PROFILE["location"])
    limit = st.slider("Results per source / query", 5, 30, 15, 5)
    expand = st.checkbox("Expand related queries", True)

    st.divider()
    st.header("🔗 Sources")
    use_jooble = st.checkbox("🇷🇴 Jooble", bool(os.getenv("JOOBLE_API_KEY")))
    use_remotive = st.checkbox("🌍 Remotive", True)

    st.divider()
    st.header("📌 Ranking filters")
    min_score = st.slider("Minimum match %", 0, 100, 45, 5)
    only_salary = st.checkbox("💰 Published salary only", False)
    hide_low_conf = st.checkbox("Hide low-confidence matches", True)
    recommended_only = st.checkbox("🎯 Show actionable matches only", True)

    st.divider()
    st.header("👤 Candidate")
    st.write(f"**Location:** {PROFILE['location']}, {PROFILE['country']}")
    st.write(f"**Experience:** {PROFILE['experience_years']}+ years")
    st.write(f"**Education:** {PROFILE['education']}")
    st.write("**Languages:** Arabic · English · Romanian (Beginner)")
    st.write(f"**Target:** {PROFILE['target_salary_min']:,}–{PROFILE['target_salary_max']:,} RON/month")


def queries_for_track() -> List[str]:
    if custom.strip():
        base = custom.strip()
    elif track == "Full Career Scan":
        return [
            "arabic customer support", "arabic operations", "operations specialist",
            "operations coordinator", "back office", "financial operations",
            "compliance", "accounting", "tax", "banking", "logistics coordinator",
            "warehouse", "quality control", "administration",
        ]
    else:
        cfg = CAREER_FAMILIES[track]
        base = cfg["strong"][0]
        if not expand:
            return [base]
        return [base] + cfg["strong"][1:5]


def run_search():
    queries = queries_for_track()
    raw = []
    errors = []
    source_counts: Dict[str, int] = {}
    jooble = JoobleAdapter(os.getenv("JOOBLE_API_KEY", ""))
    remotive = RemotiveAdapter()

    with st.status("Searching and ranking…", expanded=True) as status:
        st.write("Queries: " + ", ".join(queries))
        for q in queries:
            if use_jooble:
                rows, err = jooble.search(q, f"{location}, Romania" if location else "Timisoara, Romania", limit)
                if err:
                    errors.append(f"Jooble / {q}: {err}")
                else:
                    raw.extend(rows)
                    source_counts["Jooble"] = source_counts.get("Jooble", 0) + len(rows)
            if use_remotive:
                rows, err = remotive.search(q, location, limit)
                if err:
                    errors.append(f"Remotive / {q}: {err}")
                else:
                    raw.extend(rows)
                    source_counts["Remotive"] = source_counts.get("Remotive", 0) + len(rows)

        result = rank_jobs(raw, PROFILE)
        st.session_state.jobs = result["jobs"]
        st.session_state.rejected = result["rejected"]
        st.session_state.stats = result["stats"]
        st.session_state.searched = True
        st.session_state.last_search = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status.update(label=f"✅ {len(result['jobs'])} eligible ranked jobs from {len(raw)} raw results", state="complete")

    st.session_state.source_counts = source_counts
    st.session_state.search_errors = errors


col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🔎 Search jobs", type="primary", use_container_width=True):
        run_search()
with col2:
    if st.button("🧹 Clear", use_container_width=True):
        for key in ["jobs", "rejected", "stats"]:
            st.session_state[key] = [] if key != "stats" else {}
        st.session_state.searched = False
        st.rerun()

if st.session_state.get("searched"):
    stats = st.session_state.stats
    jobs = [j for j in st.session_state.jobs if j.score >= min_score]
    if recommended_only:
        jobs = [j for j in jobs if j.match_tier in {"strong", "good", "possible"}]
    if only_salary:
        jobs = [j for j in jobs if j.salary_min is not None or j.salary_max is not None or j.salary_text]
    if hide_low_conf:
        jobs = [j for j in jobs if j.confidence != "low"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Eligible", len(jobs))
    c2.metric("Best match", f"{jobs[0].score}%" if jobs else "—")
    c3.metric("Duplicates merged", stats.get("duplicates_removed", 0))
    c4.metric("Hard rejected", stats.get("rejected_hard", 0))
    c5.metric("Last run", st.session_state.last_search[-8:] if st.session_state.last_search else "—")

    counts = getattr(st.session_state, "source_counts", {})
    if counts:
        st.caption("Sources: " + " · ".join(f"{k}: {v}" for k, v in counts.items()))
    for err in getattr(st.session_state, "search_errors", []):
        st.warning(err)

    if not use_jooble:
        st.info("Jooble is disabled or has no API key. For Romania coverage, enable a Romanian job source/API; Remotive alone is remote-focused.")

    st.divider()
    st.subheader("🎯 Recommended jobs")

    if not jobs:
        st.warning("No jobs passed the current threshold. Lower the minimum match or broaden the track.")

    for i, job in enumerate(jobs, 1):
        applied = canonical_url(job.url) in st.session_state.applied
        with st.container(border=True):
            h1, h2 = st.columns([5, 1])
            with h1:
                st.markdown(f"### {i}. {job.title}")
                st.caption(f"**{job.company}** · 📍 {job.location or 'Not specified'} · 🌐 {job.source}")
            with h2:
                st.metric("CareerOS match", f"{job.score}%")
                st.caption(f"{job.match_tier.upper()} · {job.confidence} confidence")
            st.progress(job.score / 100)
            st.info(job.score_note) if job.match_tier in {"possible", "weak"} else None

            meta = [f"🎯 {job.career_family}", f"Family fit {job.family_fit}%"]
            if job.salary_text:
                meta.append(f"💰 {job.salary_text}")
            elif job.salary_min is not None or job.salary_max is not None:
                meta.append(f"💰 {job.salary_min or ''}–{job.salary_max or ''} RON")
            else:
                meta.append("💰 Salary not published")
            if job.duplicate_count > 1:
                meta.append(f"🔁 {job.duplicate_count} sources")
            st.caption(" · ".join(meta))

            tabs = st.tabs(["✅ Why it matches", "📊 Breakdown", "📄 Description", "⚠️ Checks"])
            with tabs[0]:
                for reason in job.reasons[:8]:
                    st.markdown(f"- {reason}")
                if not job.reasons:
                    st.info("No strong positive evidence beyond the baseline.")
            with tabs[1]:
                cols = st.columns(4)
                labels = {
                    "location": "Location", "skills": "Skills", "arabic": "Arabic", "english": "English",
                    "experience": "Experience", "salary": "Salary", "education": "Education", "relevance": "Relevance",
                }
                for idx, (dim, value) in enumerate(job.dimensions.items()):
                    maxv = {"location":20,"skills":25,"arabic":15,"english":10,"experience":10,"salary":10,"education":5,"relevance":5}[dim]
                    cols[idx % 4].metric(labels[dim], f"{value}/{maxv}")
            with tabs[2]:
                st.write(clean_text(job.description)[:2500] or "Description not available from this source.")
            with tabs[3]:
                if job.warnings:
                    for warning in job.warnings:
                        st.warning(warning)
                else:
                    st.success("No additional warning detected.")

            a1, a2 = st.columns([1, 1])
            with a1:
                if job.url:
                    st.link_button("📩 View & apply", job.url, use_container_width=True)
            with a2:
                key = canonical_url(job.url)
                if not applied:
                    if st.button("✅ Mark applied", key=f"apply_{i}_{key}", use_container_width=True):
                        st.session_state.applied[key] = {"title": job.title, "company": job.company, "score": job.score}
                        st.rerun()
                else:
                    st.success("Applied")

    with st.expander("🧪 Hard-filter audit", expanded=False):
        for job in st.session_state.rejected[:30]:
            st.write(f"**{job.title}** — {job.company}")
            for reason in job.hard_reject_reasons:
                st.write("- " + reason)

else:
    st.info("👈 Choose a career track and press **Search jobs**.")
    with st.expander("How v3 differs from the previous matcher", expanded=True):
        st.markdown(
            """
            **Search → Normalize → Deduplicate → Hard Eligibility → Career Family → Dimensional Score → Career Fit Guardrail → Rank**

            The key change is that generic matches such as *English + operations + support* can no longer make a technically unrelated role rank as a top recommendation. Direct career-family evidence and transferability now control the final ranking.
            """
        )

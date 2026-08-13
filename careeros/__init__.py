"""CareerOS AI — job search, matching and application assistant."""

from __future__ import annotations

import hashlib
from pathlib import Path

__version__ = "4.3.4"

# Stable fingerprint of the matching package. Keep this visible in the UI so
# an open Streamlit tab can be compared with the deployed code after changes.
def _engine_version() -> str:
    digest = hashlib.md5()
    root = Path(__file__).parent
    for path in sorted(root.rglob("*.py")):
        try:
            digest.update(path.read_bytes())
        except OSError:
            continue
    return digest.hexdigest()[:12]


__engine_version__ = _engine_version()

from .profile import DEFAULT_PROFILE, Profile
from . import matching as _matching
from .matching import MatchResult, calculate_match as _calculate_match_v4, hard_filter_job as _hard_filter_job_v4, priority_band
from .matching import blend_scores
from .role_intelligence import wrap_matching
from .quality import calibrate_result, deduplicate_display_jobs

# Defensive compatibility guard: older deployments/custom profile states may
# omit one of the seniority buckets. The matcher must never crash because a
# taxonomy bucket is absent; an absent bucket simply behaves as empty.
_matching.SENIORITY_PATTERNS = dict(getattr(_matching, "SENIORITY_PATTERNS", {}) or {})
_matching.SENIORITY_PATTERNS.setdefault("leadership", ["manager", "director", "head of", "head", "lead", "chief", "vp", "vice president"])
_matching.SENIORITY_PATTERNS.setdefault("senior", ["senior", "sr.", "sr ", "expert", "principal", "specialist senior"])
_matching.SENIORITY_PATTERNS.setdefault("mid", ["specialist", "coordinator", "officer", "analyst", "administrator", "associate", "executive"])
_matching.SENIORITY_PATTERNS.setdefault("junior", ["junior", "jr.", "jr ", "entry level", "entry-level", "intern", "trainee", "graduate"])

_matching.ENGLISH_ABOVE_B2 = [
    "english c1 required", "english c2 required",
    "c1 english required", "c2 english required",
    "english required c1", "english required c2",
    "c1 level english required", "c2 level english required",
    "english at c1 level required", "english at c2 level required",
    "english proficiency c1 required", "english proficiency c2 required",
    "english c1 proficiency required", "english c2 proficiency required",
    "native english required", "native-level english required",
    "native level english required", "english mother tongue required",
    "english c1 mandatory", "english c2 mandatory",
    "c1 english mandatory", "c2 english mandatory",
]

# The UI/profile policy is explicit: Ahmed speaks Arabic (native), English
# (B2), and beginner Romanian. The legacy Profile.other_languages list used to
# mean "languages considered by the matcher" rather than "languages Ahmed
# speaks", which made German/French/etc. postings leak through the language
# hard filter. Keep the legacy field for compatibility, but derive the actual
# candidate language set from the level fields.
_CANDIDATE_LANGUAGE_LEVELS = {
    "arabic": "native",
    "english": "b2",
    "romanian": "a1",
    "romana": "a1",
}
_FOREIGN_LANGUAGE_NAMES = (
    "german", "french", "dutch", "italian", "spanish", "portuguese",
    "polish", "czech", "hungarian", "greek", "turkish", "russian",
    "swedish", "norwegian", "danish", "finnish", "hebrew", "chinese",
    "japanese", "korean", "bulgarian", "serbian", "croatian", "ukrainian",
)


def _required_foreign_languages(full, profile):
    """Return required languages that Ahmed actually does not speak."""
    blocked = []
    for language in _FOREIGN_LANGUAGE_NAMES:
        if _matching.classify_language_mention(full, language) == "required":
            blocked.append(language)
    return blocked


_matching.required_foreign_languages = _required_foreign_languages

_base_hard_filter, _calculate_match_wrapped = wrap_matching(
    _hard_filter_job_v4, _calculate_match_v4, blend_scores
)


def _safe_job_for_matching(job):
    """Normalize nullable source fields before entering the strict matcher."""
    if not isinstance(job, dict):
        return job
    safe_job = dict(job)
    safe_job["title"] = str(safe_job.get("title") or "")
    safe_job["description"] = str(safe_job.get("description") or "")
    safe_job["company"] = safe_job.get("company") or ""
    safe_job["location"] = safe_job.get("location") or ""
    safe_job["category"] = safe_job.get("category") or ""
    return safe_job


def _base_calculate_match(job, profile, track=""):
    safe_job = _safe_job_for_matching(job)
    result = _calculate_match_wrapped(safe_job, profile, track)
    return calibrate_result(result, job=safe_job, profile=profile)


from . import driving as _driving

# Hard vehicle/licence gate. Category B is a useful fallback, but it does not
# qualify someone for C/C+E truck, D/D1 bus, or other heavy-vehicle roles.
_HEAVY_DRIVER_PATTERNS = (
    "c+e", "c e", "cat c", "categoria c", "category c", "categoria ce",
    "category ce", "c/e", "truck driver", "sofer camion", "șofer camion",
    "camion", "tir driver", "tīr driver", "autobuz", "bus driver",
    "categoria d", "category d", "d+e", "d e", "cat d", "permis d",
)


def _is_heavy_driver_role(job):
    title = str(job.get("title", "") or "").lower()
    description = str(job.get("description", "") or "").lower()
    text = f"{title} {description}"
    import re
    if re.search(r"\bc\s*\+\s*e\b|\bc\s*/\s*e\b|\bcategoria\s+c\b|\bcategory\s+c\b", text):
        return True
    if any(token in text for token in _HEAVY_DRIVER_PATTERNS):
        return True
    return False


def hard_filter_job(job, profile, track=""):
    """Apply strict eligibility first, then preserve the Category B fallback."""
    if _is_heavy_driver_role(job) and not getattr(profile, "has_heavy_vehicle_license", False):
        return False, "🔴 Requires C/C+E or D-class heavy-vehicle licence — profile has Category B only"

    keep, reason = _base_hard_filter(job, profile, track)
    if keep:
        return True, ""
    if "Different career track" in reason and _driving.should_keep_despite_negative_title(job, profile, track):
        # Category B fallback is valid only for actual B-compatible driver or
        # hybrid field roles; heavy-driver roles were already rejected above.
        return True, ""
    return False, reason


def calculate_match(job, profile, track=""):
    """Normal v4 score plus conservative Category B fallback enrichment."""
    result = _base_calculate_match(job, profile, track)
    return _driving.enrich_match_result(job, result, profile, track)


_matching.hard_filter_job = hard_filter_job
_matching.calculate_match = calculate_match

from .tracks import (
    ALL_TRACKS, DEFAULT_TRACK, TRACK_ARABIC, TRACK_CUSTOM, TRACK_FINANCE,
    TRACK_FULL, TRACK_LOGISTICS, TRACK_OPERATIONS, TRACK_SUPPORT,
)
from .salary import SalaryInfo, format_salary, parse_salary
from .search import (
    CAREER_PRESETS, SearchReport, SearchRequest, build_search_queries,
    deduplicate_jobs, run_search as _run_search_raw, score_and_filter,
)

_driving.configure_search_presets(CAREER_PRESETS)


def run_search(request, max_workers=8):
    report = _run_search_raw(request, max_workers=max_workers)
    report.jobs, extra_removed = deduplicate_display_jobs(report.jobs)
    report.duplicates_removed += extra_removed
    return report

from .tracker import Application, ApplicationStore, STATUS_FLOW


def _install_version_marker() -> None:
    try:
        import streamlit as st
        if getattr(st.title, "_careeros_version_marker", False):
            return
        original_title = st.title

        def versioned_title(*args, **kwargs):
            result = original_title(*args, **kwargs)
            if args and args[0] == "🎯 CareerOS AI":
                st.caption(f"v{__version__} · engine {__engine_version__}")
            return result

        versioned_title._careeros_version_marker = True
        st.title = versioned_title
    except Exception:
        return


_install_version_marker()

__all__ = [
    "__version__", "__engine_version__", "Profile", "DEFAULT_PROFILE", "MatchResult",
    "calculate_match", "hard_filter_job", "priority_band", "SalaryInfo",
    "parse_salary", "format_salary", "CAREER_PRESETS", "SearchRequest",
    "SearchReport", "build_search_queries", "deduplicate_jobs", "run_search",
    "score_and_filter", "Application", "ApplicationStore", "STATUS_FLOW",
    "ALL_TRACKS", "DEFAULT_TRACK", "TRACK_FULL", "TRACK_OPERATIONS",
    "TRACK_SUPPORT", "TRACK_ARABIC", "TRACK_FINANCE", "TRACK_LOGISTICS",
    "TRACK_CUSTOM",
]

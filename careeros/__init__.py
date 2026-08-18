"""CareerOS AI — job search, matching and application assistant."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

__version__ = "4.3.10"

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
from .text import normalize_text
from . import matching as _matching
from .matching import MatchResult, calculate_match as _calculate_match_v4, hard_filter_job as _hard_filter_job_v4, priority_band
from .matching import blend_scores
from .role_intelligence import wrap_matching
from .quality import calibrate_result, deduplicate_display_jobs
from .ranking_calibration import calibrate_ahmed_ranking

_matching.SENIORITY_PATTERNS = dict(getattr(_matching, "SENIORITY_PATTERNS", {}) or {})
_matching.SENIORITY_PATTERNS.setdefault("leadership", ["manager", "director", "head of", "head", "lead", "chief", "vp", "vice president"])
_matching.SENIORITY_PATTERNS.setdefault("senior", ["senior", "sr.", "sr ", "expert", "principal", "specialist senior"])
_matching.SENIORITY_PATTERNS.setdefault("mid", ["specialist", "coordinator", "officer", "analyst", "administrator", "associate", "executive"])
_matching.SENIORITY_PATTERNS.setdefault("junior", ["junior", "jr.", "jr ", "entry level", "entry-level", "intern", "trainee", "graduate"])

_matching.ENGLISH_ABOVE_B2 = [
    "english c1 required", "english c2 required", "c1 english required", "c2 english required",
    "english required c1", "english required c2", "c1 level english required", "c2 level english required",
    "english at c1 level required", "english at c2 level required", "english proficiency c1 required",
    "english proficiency c2 required", "english c1 proficiency required", "english c2 proficiency required",
    "native english required", "native-level english required", "native level english required",
    "english mother tongue required", "english c1 mandatory", "english c2 mandatory",
    "c1 english mandatory", "c2 english mandatory",
]

_base_hard_filter, _calculate_match_wrapped = wrap_matching(
    _hard_filter_job_v4, _calculate_match_v4, blend_scores
)


def _safe_job_for_matching(job):
    if not isinstance(job, dict):
        return job
    safe_job = dict(job)
    safe_job["title"] = str(safe_job.get("title") or "")
    safe_job["description"] = str(safe_job.get("description") or "")
    safe_job["company"] = safe_job.get("company") or ""
    safe_job["location"] = safe_job.get("location") or ""
    safe_job["category"] = safe_job.get("category") or ""
    return safe_job

_FOREIGN_TITLE_MARKETS = {
    "olanda": "Netherlands", "netherlands": "Netherlands", "nederland": "Netherlands",
    "germania": "Germany", "germany": "Germany", "deutschland": "Germany",
    "franta": "France", "franța": "France", "france": "France",
    "anglia": "UK", "regatul unit": "UK", "united kingdom": "UK", "marea britanie": "UK", "britain": "UK",
    "belgia": "Belgium", "belgium": "Belgium", "spania": "Spain", "spain": "Spain",
    "italia": "Italy", "italy": "Italy", "portugalia": "Portugal", "portugal": "Portugal",
    "elvetia": "Switzerland", "switzerland": "Switzerland",
    "polonia": "Poland", "poland": "Poland", "polska": "Poland", "grecia": "Greece", "greece": "Greece",
    "cehia": "Czechia", "czechia": "Czechia", "ungaria": "Hungary", "hungary": "Hungary",
    "suedia": "Sweden", "sweden": "Sweden", "danemarca": "Denmark", "denmark": "Denmark",
    "norvegia": "Norway", "norway": "Norway", "finlanda": "Finland", "finland": "Finland",
    "irlanda": "Ireland", "ireland": "Ireland", "austria": "Austria",
}

_TECHNICAL_TITLE_BLOCKS = (
    "software engineer", "software developer", "frontend developer", "backend developer",
    "full stack developer", "full-stack developer", "devops engineer", "cloud engineer",
    "network engineer", "network administrator", "cyber security", "cybersecurity",
    "security engineer", "data scientist", "machine learning engineer", "it governance",
    "it infrastructure", "systems engineer", "system administrator", "database administrator",
)

_AHMED_HEAVY_TITLE_RE = re.compile(
    r"\b(?:c\s*[＋+&/]\s*e|c\s*e\b|categoria\s+c(?:e|\+e)?|category\s+c(?:e|\+e)?|cat\.?\s*c(?:e|\+e)?|"
    r"categoria\s+d|category\s+d|cat\.?\s*d|d\s*[＋+&/]\s*e|permis\s+(?:c|ce|c\+e|d|de)\b|"
    r"sofer\s+camion|șofer\s+camion|truck\s+driver|tir(?:\s+driver)?|sofer\s+autobuz|șofer\s+autobuz|"
    r"bus\s+driver|coach\s+driver|camion|autobuz|autocar)\b", re.IGNORECASE)

_AHMED_HEAVY_LICENCE_RE = re.compile(
    r"(?:permis|licence|license|categoria|category|cat\.?)\s*(?:c\s*[＋+&/]\s*e|c\s*e|ce|c\b|d\b|d\s*[＋+&/]\s*e)", re.IGNORECASE)

def _is_heavy_driver_role(job) -> bool:
    title = normalize_text(str(job.get("title", "") or ""))
    desc = normalize_text(str(job.get("description", "") or ""))[:800]
    if _AHMED_HEAVY_TITLE_RE.search(title):
        return True
    if _AHMED_HEAVY_LICENCE_RE.search(f"{title} {desc}"):
        if re.search(r"(?:categoria|category|cat\.?|permis)\s*b\b", f"{title} {desc}") and not re.search(r"(?:c\s*[＋+&/]\s*e|categoria\s+c|category\s+c|cat\.?\s*c|permis\s+c|categoria\s+d|category\s+d)", f"{title} {desc}"):
            return False
        return True
    return False


def _title_foreign_market(job) -> str:
    title = str(job.get("title") or "").lower()
    loc = job.get("location") or ""
    if isinstance(loc, dict):
        loc = loc.get("display_name", "")
    text = f"{title} {str(loc).lower()}"
    for phrase, market in sorted(_FOREIGN_TITLE_MARKETS.items(), key=lambda x: len(x[0]), reverse=True):
        if re.search(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", text):
            return market
    return ""


def _base_calculate_match(job, profile, track=""):
    safe_job = _safe_job_for_matching(job)
    result = _calculate_match_wrapped(safe_job, profile, track)
    result = calibrate_result(result, job=safe_job, profile=profile)
    title_n = normalize_text(safe_job.get("title", ""))
    desc_n = normalize_text(safe_job.get("description", ""))
    management_title = bool(re.search(r"\b(?:manager|head|director|supervisor)\b", title_n))
    management_evidence = any(phrase in desc_n for phrase in (
        "managed a team", "managed team", "team of", "direct reports", "people management",
        "staff management", "supervised staff", "supervised a team", "led a team",
        "led teams", "team leadership", "hiring and performance", "performance reviews",
        "workforce management", "p&l responsibility", "p&l ownership", "budget ownership",
        "budget management", "department head", "managed employees", "managed staff",
    ))
    if management_title and not management_evidence:
        result.reasons = [r for r in result.reasons if "Leadership role — fits" not in r]
        result.warnings.append("⚠️ Management scope is not demonstrated in the documented profile")
        result.score = max(0, int(result.score) - 1)
        if result.verdict in {"apply", "strong"} and result.score < 70:
            result.verdict_label, result.verdict = priority_band(result.score, result.confidence)
    result = calibrate_ahmed_ranking(result, safe_job, profile)
    return result

from . import driving as _driving

def hard_filter_job(job, profile, track=""):
    if _is_heavy_driver_role(job):
        return False, "🔴 Heavy-vehicle driver role requires C/C+E/D/TIR licence"
    market = _title_foreign_market(job)
    if market and not getattr(profile, "open_to_relocation", False):
        return False, f"🔴 Job is tied to the {market} labour market, not Romania"
    title = str(job.get("title") or "").lower()
    if any(phrase in title for phrase in _TECHNICAL_TITLE_BLOCKS) and "it" not in str(track or "").lower():
        return False, "🔴 Technical IT role outside the documented career track"
    keep, reason = _base_hard_filter(job, profile, track)
    if keep:
        return True, ""
    if "Different career track" in reason and _driving.should_keep_despite_negative_title(job, profile, track):
        return True, ""
    return False, reason


def calculate_match(job, profile, track=""):
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
from .ahmed_recall import apply_ahmed_recall_patches

apply_ahmed_recall_patches()
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
        st.session_state.setdefault("f_min_score", 35)
        st.session_state.setdefault("f_location", "Romania")
        st.session_state.setdefault("f_hide_lang", True)
        st.session_state.setdefault("f_salary_only", True)
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

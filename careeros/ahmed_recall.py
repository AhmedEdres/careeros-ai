"""Ahmed-specific recall and source-normalisation patches.

This module is deliberately small: it does not rewrite the matching engine.
It widens the Full Career Scan with high-value role synonyms, including the
Romanian titles used by local boards, repairs Hipo card fields at the provider
boundary, and closes a narrow IT-title gap found in the live scan.
"""

from __future__ import annotations

import re
from typing import Dict

from .salary import parse_salary
from .text import normalize_text


# Retrieval terms only. Downstream hard gates and scoring remain authoritative.
# Romanian terms are intentional: local boards often publish the same roles in
# Romanian and an English-only query misses them before matching even starts.
FULL_SCAN_RECALL_QUERIES = [
    "operations coordinator",
    "operations specialist",
    "financial operations",
    "back office",
    "order management",
    "customer support",
    "customer service",
    "arabic customer support",
    "compliance officer",
    "tax compliance",
    "tax specialist",
    "logistics coordinator",
    "specialist conformitate",
    "specialist fiscal",
    "coordonator operatiuni",
    "specialist back office",
    "coordonator logistica",
    "suport clienti",
    "serviciu clienti",
    "specialist administrativ",
]

_HIPO_CITY_RE = re.compile(
    r"(?<![a-z])(?:timișoara|timisoara|bucuresti|bucharest|cluj|iasi|iași|brasov|brașov|arad|sibiu|oradea|constanta|constanța)(?![a-z])",
    re.IGNORECASE,
)
_HIPO_DATE_RE = re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b")
_HIPO_HEADING_RE = re.compile(r"\s+Jobs from Hipo.*$", re.IGNORECASE)
_HIPO_EMPLOYER_MARKER_RE = re.compile(r"Employer:\s*\S")
_HIPO_RELATED_JOBS_MARKER_RE = re.compile(
    r"Job-uri similare care te-ar putea interesa|Locuri de munca similare", re.IGNORECASE
)


def _display_name(value) -> str:
    if isinstance(value, dict):
        return str(value.get("display_name", "") or "")
    return str(value or "")


def _company_from_hipo(job: Dict) -> str:
    title = str(job.get("title", "") or "")
    company = _display_name(job.get("company"))
    match = re.search(r"@\s*([^|]+?)(?:\s+Jobs from Hipo.*)?$", title, re.IGNORECASE)
    if match:
        return match.group(1).strip(" -–—")
    if company and "jobs from hipo" not in normalize_text(company):
        return company.strip()
    blob = " ".join(str(job.get(key, "") or "") for key in ("description", "description_text"))
    match = re.search(r"@\s*([^|]+?)\s+Jobs from Hipo\b", blob, re.IGNORECASE)
    return match.group(1).strip(" -–—") if match else ""


def _clean_title(title: str) -> str:
    title = _HIPO_HEADING_RE.sub("", title or "")
    title = _HIPO_DATE_RE.sub("", title).strip(" -–—|")
    return title


def _clean_location(job: Dict) -> str:
    location = _display_name(job.get("location"))
    polluted = normalize_text(location)
    if location and "jobs from hipo" not in polluted and not _HIPO_DATE_RE.search(location):
        if len(location) <= 80 and not normalize_text(job.get("title", "")) in polluted:
            return location.strip()

    haystack = " ".join(str(job.get(key, "") or "") for key in ("description", "description_text", "location"))
    city = _HIPO_CITY_RE.search(haystack)
    if city:
        pretty = city.group(0)
        if normalize_text(pretty) in {"timisoara", "timișoara"}:
            pretty = "Timisoara"
        if "hybrid" in normalize_text(location) or "hybrid" in normalize_text(haystack[:500]):
            return f"Hybrid / {pretty}"
        if "remote" in normalize_text(location):
            return f"Remote / {pretty}"
        return pretty
    return "Timisoara" if not location or "jobs from hipo" in polluted else location[:80].strip()


def _clean_salary(job: Dict) -> str:
    raw = str(job.get("salary_text", "") or "").strip()
    if not raw:
        return ""
    return raw if parse_salary(raw).has_value else ""


def _clean_description(job: Dict) -> str:
    """Strip Hipo's page navigation and "related jobs" boilerplate.

    Some Hipo scrapes capture the whole page rather than just the posting:
    roughly 2500 characters of site navigation and a rotating "Company News"
    sidebar widget, prepended before the actual structured job content, and
    a "Job-uri similare care te-ar putea interesa" (related jobs) block plus
    site footer appended after it. That real content reliably starts at
    "Employer:" (Hipo's own metadata line, with the job title repeated
    immediately before it) and ends where the related-jobs block begins.
    This boilerplate is strong enough on its own to make role_intelligence
    misclassify the posting — an incidental "recruiter" mention in a news
    blurb, or an unrelated "HR Business Partner" job named in the related-
    jobs suggestions, can tip an unrelated role into the "HR" family and
    hard-reject it. Descriptions without the "Employer:" marker (already
    clean/short, or a Hipo promo/event page rather than a real job) are
    left untouched — the leading-boilerplate case is what makes those
    reliably identifiable, so no separate check is needed for the trailer
    alone.
    """
    desc = str(job.get("description", "") or "")
    match = _HIPO_EMPLOYER_MARKER_RE.search(desc)
    if not match:
        return desc
    title = str(job.get("title", "") or "")
    start = desc.rfind(title, 0, match.start()) if title else -1
    if start == -1:
        # Title text didn't line up exactly — fall back to a small look-back
        # so the repeated-title line right before "Employer:" is still kept
        # where possible, rather than losing it entirely.
        start = max(0, match.start() - 120)
    body = desc[start:]
    end_match = _HIPO_RELATED_JOBS_MARKER_RE.search(body)
    if end_match:
        body = body[: end_match.start()]
    return body.strip()


def _normalise_hipo_job(job: Dict) -> Dict:
    cleaned = dict(job)
    cleaned["title"] = _clean_title(str(cleaned.get("title", "") or ""))
    cleaned["company"] = {"display_name": _company_from_hipo(cleaned)}
    cleaned["location"] = {"display_name": _clean_location(cleaned)}
    cleaned["salary_text"] = _clean_salary(cleaned)
    if not cleaned["salary_text"]:
        cleaned["salary_min"] = None
        cleaned["salary_max"] = None
        cleaned["salary_currency"] = None
    cleaned["description"] = _clean_description(cleaned)
    return cleaned


def _patch_hipo_provider() -> None:
    from .sources import PROVIDERS
    spec = PROVIDERS.get("hipo")
    if spec is None or getattr(spec.fetch, "_ahmed_normalised", False):
        return
    original = spec.fetch
    def wrapped_fetch(*args, **kwargs):
        result = original(*args, **kwargs)
        result.jobs = [_normalise_hipo_job(job) for job in result.jobs]
        return result
    wrapped_fetch._ahmed_normalised = True
    spec.fetch = wrapped_fetch


def _patch_it_title_gap() -> None:
    """Close IT titles where the token appears after the service/function."""
    from . import role_intelligence as _role
    extra = (
        "tehnician service it",
        "technician service it",
        "it service technician",
        "it technician",
        "technical service it",
        "service it technician",
    )
    current = tuple(getattr(_role, "IT_TITLE", ()) or ())
    _role.IT_TITLE = tuple(dict.fromkeys(current + extra))


def apply_ahmed_recall_patches() -> None:
    """Install narrow, idempotent patches after the normal provider imports."""
    from . import search as _search
    _search.MAX_QUERIES = max(int(getattr(_search, "MAX_QUERIES", 6)), len(FULL_SCAN_RECALL_QUERIES))
    _search.CAREER_PRESETS["🔥 Full Career Scan (recommended)"] = list(FULL_SCAN_RECALL_QUERIES)
    _patch_it_title_gap()
    _patch_hipo_provider()


__all__ = ["FULL_SCAN_RECALL_QUERIES", "apply_ahmed_recall_patches"]

"""Ahmed-specific recall and source-normalisation patches.

This module is deliberately small: it does not rewrite the matching engine.
It widens the Full Career Scan with high-value role synonyms and repairs the
Hipo card fields at the provider boundary when board markup leaks headings into
company/location/salary fields.
"""

from __future__ import annotations

import re
from typing import Dict

from .salary import parse_salary
from .text import normalize_text


# Keep the full scan broad enough to recover Ahmed's actual target families,
# while leaving the hard eligibility gates untouched downstream.
FULL_SCAN_RECALL_QUERIES = [
    "operations coordinator",
    "operations specialist",
    "financial operations",
    "back office",
    "customer support",
    "customer service",
    "compliance officer",
    "arabic customer support",
]

_HIPO_CITY_RE = re.compile(
    r"(?<![a-z])(?:timișoara|timisoara|bucuresti|bucharest|cluj|iasi|iași|brasov|brașov|arad|sibiu|oradea|constanta|constanța)(?![a-z])",
    re.IGNORECASE,
)
_HIPO_DATE_RE = re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b")
_HIPO_HEADING_RE = re.compile(r"\s+Jobs from Hipo.*$", re.IGNORECASE)


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
    blob = " ".join(
        str(job.get(key, "") or "") for key in ("description", "description_text")
    )
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

    haystack = " ".join(
        str(job.get(key, "") or "") for key in ("description", "description_text", "location")
    )
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


def apply_ahmed_recall_patches() -> None:
    """Install narrow, idempotent patches after the normal provider imports."""
    from . import search as _search

    # The production search layer historically capped every preset at six.
    # Full Career Scan now intentionally has eight high-value Ahmed queries;
    # make the cap agree with the policy instead of relying on import order or
    # a stale runtime constant.
    _search.MAX_QUERIES = max(int(getattr(_search, "MAX_QUERIES", 6)), len(FULL_SCAN_RECALL_QUERIES))
    _search.CAREER_PRESETS["🔥 Full Career Scan (recommended)"] = list(FULL_SCAN_RECALL_QUERIES)
    _patch_hipo_provider()


__all__ = ["FULL_SCAN_RECALL_QUERIES", "apply_ahmed_recall_patches"]

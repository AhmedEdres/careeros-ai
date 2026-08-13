"""ANOFM / Mediere public job source.

ANOFM exposes its public job-posting view through a JSON endpoint used by the
Romanian job-mediation platform. This adapter treats ANOFM as a candidate-
discovery source: it pulls a bounded window of current public postings, keeps
the candidate's requested geography, and preserves structured requirements
that the matching engine needs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from ..text import contains_any, normalize_location, normalize_text
from .base import DEFAULT_TIMEOUT, SourceResult, make_job
from .providers import _keyword_filter

ANOFM_ENDPOINTS = (
    "https://www.anofm.ro/api/entity/vw_public_job_posting",
    "https://mediere.anofm.ro/api/entity/vw_public_job_posting",
)
ANOFM_JOB_URL = "https://mediere.anofm.ro/app/module/mediere/job/{id}"
ANOFM_PAGE_SIZE = 250
ANOFM_MAX_PAGES = 6
_TIMISOARA_TERMS = ("timisoara", "timis", "timisoara county")


def _first(item: Dict[str, Any], *names: str, default: Any = "") -> Any:
    for name in names:
        value = item.get(name)
        if value not in (None, "", []):
            return value
    return default


def _text(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ", ".join(_text(v) for v in value if v not in (None, ""))
    if isinstance(value, dict):
        for key in ("label", "name", "display_name", "value", "description"):
            if value.get(key) not in (None, ""):
                return _text(value[key])
        return ", ".join(f"{k}: {_text(v)}" for k, v in value.items() if v not in (None, ""))
    return str(value or "").strip()


def _rows(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("rows", "data", "results", "items", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return [r for r in value if isinstance(r, dict)]
    for key in ("result", "payload"):
        nested = payload.get(key)
        if isinstance(nested, dict):
            found = _rows(nested)
            if found:
                return found
    return []


def _location_text(item: Dict[str, Any]) -> str:
    county = _text(_first(item, "county_name", "county", "judet_name", "judet"))
    city = _text(_first(item, "city_name", "locality_name", "localitate_name", "city", "locality"))
    locality = _text(_first(item, "town_name", "municipality_name", "municipality", "town"))
    parts: List[str] = []
    for value in (county, city, locality):
        if value and value not in parts:
            parts.append(value)
    return " > ".join(parts)


def _matches_location(location: str, requested: str) -> bool:
    requested_norm = normalize_text(normalize_location(requested))
    if not requested_norm or requested_norm in {"romania", "ro", "all"}:
        return True
    loc_norm = normalize_text(location)
    if not loc_norm:
        return True
    if "timisoara" in requested_norm or "timis" in requested_norm:
        return contains_any(loc_norm, _TIMISOARA_TERMS)
    tokens = [t for t in requested_norm.split() if len(t) >= 4]
    return any(token in loc_norm for token in tokens)


def _build_description(item: Dict[str, Any]) -> str:
    fields = [
        ("COR", _first(item, "cor", "cor_code", "occupation_code")),
        ("Domeniu", _first(item, "domain_name", "domain", "activity_domain")),
        ("Educație", _first(item, "education_level", "education", "studies")),
        ("Experiență", _first(item, "experience", "experience_level", "professional_experience")),
        ("Limbi străine", _first(item, "languages", "foreign_languages", "language_requirements")),
        ("Permis", _first(item, "driving_license", "driving_licence", "license")),
        ("Cetățeni UE", _first(item, "valid_for_eu", "valid_for_eu_citizens", "eu_citizens")),
        ("Contract", _first(item, "contract_type", "type_contract")),
        ("Normă", _first(item, "work_schedule", "norm_type", "type_norm")),
        ("Regim", _first(item, "work_regime", "work_mode", "regime")),
        ("Beneficii", _first(item, "benefits", "beneficiile")),
        ("Responsabilități", _first(item, "responsibilities", "description", "job_description")),
    ]
    parts = [f"{label}: {_text(value)}" for label, value in fields if _text(value)]
    return " | ".join(parts)


def _parse_job(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    job_id = _first(item, "id", "job_id", "offer_id", "job_posting_id")
    title = _first(item, "title", "occupation_name", "job_title", "occupation")
    if not job_id or not title:
        return None
    company = _first(item, "employer_name", "company_name", "employer", "company")
    location = _location_text(item) or _text(_first(item, "location", "work_location"))
    description = _build_description(item)
    valid_until = _first(item, "valid_until", "validity_end", "offer_valid_until", "date_valid_until")
    created_at = _first(item, "created_at", "posted_at", "date_posted", "publication_date")
    salary_min = _first(item, "salary_min", "min_salary", "minimum_salary", default=None)
    salary_max = _first(item, "salary_max", "max_salary", "maximum_salary", default=None)
    salary_text = _text(_first(item, "salary", "salary_text"))
    if not salary_text and (salary_min not in (None, "") or salary_max not in (None, "")):
        salary_text = f"{salary_min or ''} - {salary_max or ''} RON".strip(" -")

    def _number(value: Any) -> Optional[float]:
        try:
            return float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return None

    return make_job(
        title=_text(title),
        company=company,
        location=location,
        description=description,
        url=ANOFM_JOB_URL.format(id=job_id),
        source="ANOFM / Mediere",
        salary_text=salary_text,
        salary_min=_number(salary_min),
        salary_max=_number(salary_max),
        salary_currency="ron",
        category=_text(_first(item, "domain_name", "domain", "activity_domain")),
        posted_at=created_at,
        extra={
            "anofm_id": str(job_id),
            "anofm_cor": _text(_first(item, "cor", "cor_code", "occupation_code")),
            "anofm_valid_until": _text(valid_until),
            "anofm_eu_eligible": _text(_first(item, "valid_for_eu", "valid_for_eu_citizens", "eu_citizens")),
            "anofm_contact_email": _text(_first(item, "contact_email", "email")),
            "anofm_contact_phone": _text(_first(item, "contact_phone", "phone")),
        },
    )


def fetch_anofm(
    keywords: str,
    location: str = "Timisoara",
    limit: int = 20,
    phrases: Optional[List[str]] = None,
    session: Optional[requests.Session] = None,
    **_,
) -> SourceResult:
    """Fetch recent ANOFM postings once, then filter locally."""
    source = "ANOFM / Mediere"
    session = session or requests.Session()
    session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
    requested_phrases = [p for p in (phrases or []) if p and p.strip()]
    if not requested_phrases and keywords.strip():
        requested_phrases = [keywords.strip()]

    jobs: List[Dict[str, Any]] = []
    seen_ids = set()
    last_error: Optional[str] = None

    for endpoint in ANOFM_ENDPOINTS:
        endpoint_jobs: List[Dict[str, Any]] = []
        try:
            for page in range(1, ANOFM_MAX_PAGES + 1):
                payload = {
                    "current": page,
                    "rowCount": ANOFM_PAGE_SIZE,
                    "sort": {"created_at": "desc"},
                }
                response = session.post(endpoint, json=payload, timeout=DEFAULT_TIMEOUT)
                if response.status_code != 200:
                    last_error = f"{source}: HTTP {response.status_code}"
                    break
                rows = _rows(response.json())
                if not rows:
                    break

                for item in rows:
                    job = _parse_job(item)
                    if not job:
                        continue
                    job_id = job.get("anofm_id")
                    if job_id in seen_ids:
                        continue
                    if not _matches_location(job["location"]["display_name"], location):
                        continue
                    blob = " ".join([
                        job["title"],
                        job["company"]["display_name"],
                        job["description_text"],
                    ])
                    if requested_phrases and not _keyword_filter(blob, " ".join(requested_phrases), requested_phrases):
                        continue
                    seen_ids.add(job_id)
                    endpoint_jobs.append(job)
                    if len(endpoint_jobs) >= limit:
                        break

                if len(endpoint_jobs) >= limit or len(rows) < ANOFM_PAGE_SIZE:
                    break
        except requests.exceptions.RequestException as exc:
            last_error = f"{source}: request failed — {exc}"

        if endpoint_jobs:
            jobs.extend(endpoint_jobs)
            break

    if not jobs and last_error:
        return SourceResult(source=source, error=last_error)
    return SourceResult(source=source, jobs=jobs[:limit])


__all__ = ["fetch_anofm", "ANOFM_ENDPOINTS", "ANOFM_JOB_URL"]

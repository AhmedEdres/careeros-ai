"""Concrete job source adapters.

Every provider returns a :class:`SourceResult`; none of them raise. Adding a
provider means writing one function and registering it in ``PROVIDERS``.
"""

from __future__ import annotations

import time
from functools import lru_cache
from typing import Callable, Dict, List, Optional

import requests

from ..text import normalize_location, normalize_text, contains_any, contains_phrase
from .base import (
    DEFAULT_TIMEOUT,
    SourceResult,
    build_session,
    http_error_message,
    make_job,
)

__all__ = ["PROVIDERS", "ProviderSpec", "fetch_source"]


class ProviderSpec:
    """Metadata describing a source so the UI can render it generically."""

    def __init__(
        self,
        key: str,
        label: str,
        short_name: str,
        fetch: Callable[..., SourceResult],
        needs_keys: Optional[List[str]] = None,
        default_on: bool = True,
        help_text: str = "",
        supports_location: bool = True,
        client_side_filter: bool = False,
    ):
        self.key = key
        self.label = label
        self.short_name = short_name
        self.fetch = fetch
        self.needs_keys = needs_keys or []
        self.default_on = default_on
        self.help_text = help_text
        self.supports_location = supports_location
        # True when the provider downloads a whole board and filters locally:
        # such sources must be queried ONCE with all keywords combined.
        self.client_side_filter = client_side_filter


def _timed(source: str, func, *args, **kwargs) -> SourceResult:
    start = time.perf_counter()
    try:
        result = func(*args, **kwargs)
    except requests.exceptions.Timeout:
        result = SourceResult(source=source, error=f"{source}: request timed out — try again or reduce results")
    except requests.exceptions.SSLError as exc:
        result = SourceResult(source=source, error=f"{source}: TLS error — {exc}")
    except requests.exceptions.ConnectionError:
        result = SourceResult(source=source, error=f"{source}: could not connect (network or DNS issue)")
    except requests.exceptions.RequestException as exc:
        result = SourceResult(source=source, error=f"{source}: connection error — {exc}")
    except ValueError:
        result = SourceResult(source=source, error=f"{source}: returned malformed JSON")
    except Exception as exc:  # pragma: no cover - defensive
        result = SourceResult(source=source, error=f"{source}: unexpected error — {exc}")
    result.elapsed_ms = int((time.perf_counter() - start) * 1000)
    return result


@lru_cache(maxsize=1)
def _domain_anchors() -> tuple:
    """Distinctive terms from the skill taxonomy used to keep relevant jobs.

    Generic words ("support", "office", "client") are excluded: on their own
    they let through "Office Cleaner" or "IT Support". Multi-word entries are
    already specific enough to keep.
    """
    from ..profile import SKILL_GROUPS

    too_generic = {
        # Words that appear in unrelated jobs just as often as in relevant ones.
        "support", "office", "client", "customer", "service", "warehouse",
        "administration", "administrator", "coordinator", "risk", "credit",
        "bank", "legal", "import", "export", "transport", "inventory",
        "purchasing", "distribution", "shipping", "excel", "sql", "erp",
        "oracle", "jira", "sharepoint", "salesforce", "arabic", "multilingual",
        "bilingual", "uae", "saudi", "egypt", "gulf", "mena", "levant", "gcc",
        "middle east", "case management", "data entry", "advisor", "partner",
    }
    # Terms specific enough to justify keeping a job on their own, even though
    # the taxonomy alone would not surface them. Short acronyms are listed
    # explicitly because the length guard below would otherwise drop them.
    extra_anchors = {
        "operations", "operational", "back office", "backoffice",
        "aml", "kyc", "sap", "o2c", "p2p", "r2r", "bpo",
    }

    anchors = set(extra_anchors)
    for group in SKILL_GROUPS.values():
        for word in group["words"]:
            normalized = normalize_text(word)
            if normalized in too_generic or len(normalized) < 4:
                continue
            anchors.add(normalized)
            if " " not in normalized:
                anchors.update(_word_variants(normalized))
    return tuple(sorted(anchors))


def _word_variants(word: str) -> List[str]:
    """Cheap morphological variants so 'accounting' also matches 'accountant'.

    A real stemmer would be overkill here; job titles use a small, predictable
    set of endings.
    """
    word = normalize_text(word)
    if len(word) < 4:
        return []
    variants = {word + "s", word + "es"}
    stem = word
    for suffix in ("ing", "ance", "ence", "ment", "ions", "ion", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            stem = word[: -len(suffix)]
            break
    if stem != word:
        variants.update({stem, stem + "s", stem + "ant", stem + "ants",
                         stem + "ent", stem + "er", stem + "ers", stem + "or", stem + "ors"})
    else:
        variants.update({word + "ant", word + "ants", word + "er", word + "ers"})
    return sorted(v for v in variants if v != word and len(v) >= 4)


def _keyword_filter(text_fields: str, keywords: str, phrases: Optional[List[str]] = None) -> bool:
    """Client-side keyword filter for sources without a search parameter.

    Matching whole *phrases* rather than loose words is what keeps the quality
    up: a bag-of-words filter accepts "Office Cleaner" for the query
    "back office", because the single word "office" appears. Callers pass the
    original query list so each phrase is tested as a unit.
    """
    haystack = normalize_text(text_fields)
    candidates = [p for p in (phrases or []) if p and p.strip()]

    if not candidates:
        text = normalize_text(keywords).strip()
        if not text:
            return True
        candidates = [text]

    # 1. Exact phrase — the strongest signal ("back office", "accounts payable").
    if contains_any(haystack, candidates):
        return True

    # 2. Domain anchors: distinctive terms that indicate the right career
    #    track on their own. These are derived from the skill taxonomy the
    #    scoring engine already uses, so the fetch filter and the ranking stay
    #    consistent — a job the engine would rate highly is never dropped here.
    #    This keeps titles like "Head of Operations", "Senior Accountant" or
    #    "Payroll Officer" that an exact-phrase-only filter would discard.
    if contains_any(haystack, _domain_anchors()):
        return True

    # 3. Two-word queries also match when both words appear anywhere
    #    ("customer support" → "support agent for customers").
    for phrase in candidates:
        words = [w for w in normalize_text(phrase).split() if len(w) >= 4]
        if len(words) < 2:
            continue
        if all(
            contains_phrase(haystack, w) or contains_any(haystack, _word_variants(w))
            for w in words
        ):
            return True

    return False


# ---------------------------------------------------------------------------
# Jooble — main Romanian aggregator (POST API, needs a key)
# ---------------------------------------------------------------------------
def fetch_jooble(
    keywords: str,
    location: str,
    limit: int = 20,
    pages: int = 2,
    api_key: str = "",
    session: Optional[requests.Session] = None,
    **_,
) -> SourceResult:
    source = "Jooble"
    if not api_key:
        return SourceResult(source=source, skipped=True,
                            error="Jooble: API key missing (add JOOBLE_API_KEY to Secrets)")

    session = session or build_session()
    url = f"https://jooble.org/api/{api_key}"
    search_location = normalize_location(location)
    jobs: List[Dict] = []

    for page in range(1, max(1, pages) + 1):
        payload = {
            "keywords": keywords.strip(),
            "location": search_location,
            "radius": "50",
            "page": str(page),
            "ResultOnPage": str(min(limit, 50)),
            "companysearch": "false",
        }
        response = session.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            if jobs:
                break
            return SourceResult(source=source,
                                error=http_error_message(source, response.status_code, response.text))

        payload_json = response.json()
        page_jobs = payload_json.get("jobs") or []
        if not isinstance(page_jobs, list) or not page_jobs:
            break

        for item in page_jobs:
            if not isinstance(item, dict):
                continue
            jobs.append(make_job(
                title=item.get("title", ""),
                company=item.get("company", ""),
                location=item.get("location") or search_location,
                description=item.get("snippet", ""),
                url=item.get("link", ""),
                source=f"Jooble{' / ' + str(item.get('source')) if item.get('source') else ''}",
                salary_text=item.get("salary", ""),
                salary_currency="ron",
                category=item.get("type", ""),
                posted_at=item.get("updated"),
            ))
        if len(jobs) >= limit * pages:
            break

    return SourceResult(source=source, jobs=jobs)


# ---------------------------------------------------------------------------
# Remotive — remote jobs (free, supports server-side search)
# ---------------------------------------------------------------------------
def fetch_remotive(
    keywords: str,
    limit: int = 20,
    session: Optional[requests.Session] = None,
    **_,
) -> SourceResult:
    source = "Remotive"
    session = session or build_session()
    response = session.get(
        "https://remotive.com/api/remote-jobs",
        params={"search": keywords.strip(), "limit": max(limit * 2, 40)},
        timeout=DEFAULT_TIMEOUT,
    )
    if response.status_code != 200:
        return SourceResult(source=source,
                            error=http_error_message(source, response.status_code, response.text))

    items = response.json().get("jobs") or []
    jobs: List[Dict] = []
    for item in items:
        if not isinstance(item, dict) or len(jobs) >= limit:
            continue
        region = item.get("candidate_required_location") or "Worldwide"
        jobs.append(make_job(
            title=item.get("title", ""),
            company=item.get("company_name", ""),
            location=f"Remote — {region}",
            description=item.get("description", ""),
            url=item.get("url", ""),
            source=source,
            salary_text=item.get("salary", ""),
            category=item.get("category", ""),
            posted_at=item.get("publication_date"),
            remote=True,
        ))
    return SourceResult(source=source, jobs=jobs)


# ---------------------------------------------------------------------------
# Arbeitnow — free EU job board (no key)
# ---------------------------------------------------------------------------
def fetch_arbeitnow(
    keywords: str,
    limit: int = 20,
    session: Optional[requests.Session] = None,
    phrases: Optional[List[str]] = None,
    **_,
) -> SourceResult:
    source = "Arbeitnow"
    session = session or build_session()
    jobs: List[Dict] = []

    for page in (1, 2):
        response = session.get(
            "https://www.arbeitnow.com/api/job-board-api",
            params={"page": page},
            timeout=DEFAULT_TIMEOUT,
        )
        if response.status_code != 200:
            if jobs:
                break
            return SourceResult(source=source,
                                error=http_error_message(source, response.status_code, response.text))

        items = response.json().get("data") or []
        if not isinstance(items, list) or not items:
            break

        for item in items:
            if not isinstance(item, dict) or len(jobs) >= limit:
                break
            tags = item.get("tags") or []
            blob = f"{item.get('title','')} {item.get('company_name','')} {item.get('description','')} {' '.join(map(str, tags))}"
            if not _keyword_filter(blob, keywords, phrases):
                continue
            is_remote = bool(item.get("remote"))
            loc = str(item.get("location") or "").strip()
            jobs.append(make_job(
                title=item.get("title", ""),
                company=item.get("company_name", ""),
                location=(f"Remote — {loc}" if is_remote and loc else ("Remote" if is_remote else loc)),
                description=item.get("description", ""),
                url=item.get("url", ""),
                source=source,
                category=", ".join(str(t) for t in tags[:3]),
                posted_at=item.get("created_at"),
                remote=is_remote,
            ))
        if len(jobs) >= limit:
            break

    return SourceResult(source=source, jobs=jobs)


# ---------------------------------------------------------------------------
# Jobicy — free remote board with geo filtering (no key)
# ---------------------------------------------------------------------------
def fetch_jobicy(
    keywords: str,
    limit: int = 20,
    session: Optional[requests.Session] = None,
    phrases: Optional[List[str]] = None,
    **_,
) -> SourceResult:
    source = "Jobicy"
    session = session or build_session()
    jobs: List[Dict] = []

    for geo in ("europe", "anywhere"):
        response = session.get(
            "https://jobicy.com/api/v2/remote-jobs",
            params={"count": min(max(limit, 10), 50), "geo": geo},
            timeout=DEFAULT_TIMEOUT,
        )
        if response.status_code != 200:
            if jobs:
                break
            return SourceResult(source=source,
                                error=http_error_message(source, response.status_code, response.text))

        items = response.json().get("jobs") or []
        for item in items:
            if not isinstance(item, dict) or len(jobs) >= limit:
                break
            blob = f"{item.get('jobTitle','')} {item.get('companyName','')} {item.get('jobExcerpt','')} {item.get('jobDescription','')}"
            if not _keyword_filter(blob, keywords, phrases):
                continue
            geo_label = item.get("jobGeo") or "Worldwide"
            salary_min = item.get("annualSalaryMin")
            salary_max = item.get("annualSalaryMax")
            salary_text = ""
            if salary_min or salary_max:
                currency = item.get("salaryCurrency") or "USD"
                salary_text = f"{salary_min or ''}-{salary_max or ''} {currency} per year".strip("- ")
            jobs.append(make_job(
                title=item.get("jobTitle", ""),
                company=item.get("companyName", ""),
                location=f"Remote — {geo_label}",
                description=item.get("jobDescription") or item.get("jobExcerpt", ""),
                url=item.get("url", ""),
                source=source,
                salary_text=salary_text,
                salary_currency=str(item.get("salaryCurrency") or "").lower() or None,
                category=", ".join(item.get("jobIndustry") or []) if isinstance(item.get("jobIndustry"), list) else str(item.get("jobIndustry") or ""),
                posted_at=item.get("pubDate"),
                remote=True,
            ))
        if len(jobs) >= limit:
            break

    return SourceResult(source=source, jobs=jobs)


# ---------------------------------------------------------------------------
# Adzuna — international, structured salaries (needs app id + key)
# ---------------------------------------------------------------------------
_ADZUNA_COUNTRIES = {
    "romania": "ro", "germany": "de", "austria": "at", "france": "fr",
    "italy": "it", "spain": "es", "netherlands": "nl", "poland": "pl",
    "united kingdom": "gb", "uk": "gb", "ireland": "ie", "belgium": "be",
    "switzerland": "ch", "portugal": "pt",
}


def _adzuna_country(location: str) -> str:
    loc = normalize_text(location)
    for name, code in _ADZUNA_COUNTRIES.items():
        if name in loc:
            return code
    if contains_any(loc, ["timisoara", "bucharest", "bucuresti", "cluj", "iasi", "brasov"]):
        return "ro"
    return "ro"


def fetch_adzuna(
    keywords: str,
    location: str,
    limit: int = 20,
    app_id: str = "",
    app_key: str = "",
    session: Optional[requests.Session] = None,
    **_,
) -> SourceResult:
    source = "Adzuna"
    if not app_id or not app_key:
        return SourceResult(source=source, skipped=True,
                            error="Adzuna: credentials not configured (ADZUNA_APP_ID / ADZUNA_APP_KEY)")

    session = session or build_session()
    country = _adzuna_country(location)
    response = session.get(
        f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
        params={
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": min(limit, 50),
            "what": keywords.strip(),
            "where": location.strip(),
            "content-type": "application/json",
            "sort_by": "date",
            "max_days_old": 60,
        },
        timeout=DEFAULT_TIMEOUT,
    )
    if response.status_code != 200:
        return SourceResult(source=source,
                            error=http_error_message(source, response.status_code, response.text))

    currency = "ron" if country == "ro" else None
    jobs: List[Dict] = []
    for item in (response.json().get("results") or [])[:limit]:
        if not isinstance(item, dict):
            continue
        smin, smax = item.get("salary_min"), item.get("salary_max")
        salary_text = ""
        if smin or smax:
            salary_text = f"{smin or ''} - {smax or ''}".strip(" -")
        jobs.append(make_job(
            title=item.get("title", ""),
            company=item.get("company", {}),
            location=(item.get("location") or {}).get("display_name", location),
            description=item.get("description", ""),
            url=item.get("redirect_url", ""),
            source=source,
            salary_text=salary_text,
            salary_min=smin,
            salary_max=smax,
            salary_currency=currency,
            category=(item.get("category") or {}).get("label", ""),
            posted_at=item.get("created"),
        ))
    return SourceResult(source=source, jobs=jobs)


# ---------------------------------------------------------------------------
# Careerjet — needs a free affiliate id
# ---------------------------------------------------------------------------
def fetch_careerjet(
    keywords: str,
    location: str,
    limit: int = 20,
    affid: str = "",
    session: Optional[requests.Session] = None,
    **_,
) -> SourceResult:
    source = "Careerjet"
    if not affid:
        return SourceResult(source=source, skipped=True,
                            error="Careerjet: affiliate ID missing (free at careerjet.com/partners)")

    session = session or build_session()
    response = session.get(
        "https://search.api.careerjet.net/v4/query",
        params={
            "keywords": keywords.strip(),
            "location": normalize_location(location),
            "locale_code": "en_RO",
            "pagesize": str(min(limit, 99)),
            "page": "1",
            "sort": "date",
            "affid": affid,
            "user_ip": "86.124.0.1",
            "user_agent": "Mozilla/5.0 (CareerOS/3.0)",
        },
        timeout=DEFAULT_TIMEOUT,
    )
    if response.status_code != 200:
        return SourceResult(source=source,
                            error=http_error_message(source, response.status_code, response.text))

    payload = response.json()
    if str(payload.get("type", "")).upper() == "ERROR":
        return SourceResult(source=source, error=f"Careerjet: {payload.get('message', 'unknown error')}")

    jobs: List[Dict] = []
    for item in (payload.get("jobs") or [])[:limit]:
        if not isinstance(item, dict):
            continue
        jobs.append(make_job(
            title=item.get("title", ""),
            company=item.get("company", ""),
            location=item.get("locations", location),
            description=item.get("description", ""),
            url=item.get("url", ""),
            source=source,
            salary_text=item.get("salary", ""),
            salary_currency="ron",
            posted_at=item.get("date"),
        ))
    return SourceResult(source=source, jobs=jobs)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
PROVIDERS: Dict[str, ProviderSpec] = {
    "jooble": ProviderSpec(
        "jooble", "🇷🇴 Jooble — Romania", "Jooble", fetch_jooble,
        needs_keys=["JOOBLE_API_KEY"], default_on=True,
        help_text="Main Romanian aggregator. Needs a free API key.",
    ),
    "remotive": ProviderSpec(
        "remotive", "🌍 Remotive — Remote", "Remotive", fetch_remotive,
        default_on=True, supports_location=False,
        help_text="Remote-first roles, free API with server-side search.",
    ),
    "arbeitnow": ProviderSpec(
        "arbeitnow", "🇪🇺 Arbeitnow — EU", "Arbeitnow", fetch_arbeitnow,
        default_on=True, supports_location=False, client_side_filter=True,
        help_text="EU jobs from Greenhouse/SmartRecruiters/Recruitee. Free.",
    ),
    "jobicy": ProviderSpec(
        "jobicy", "🛰️ Jobicy — Remote EU", "Jobicy", fetch_jobicy,
        default_on=True, supports_location=False, client_side_filter=True,
        help_text="Remote board with a Europe geo filter. Free.",
    ),
    "adzuna": ProviderSpec(
        "adzuna", "🌐 Adzuna — International", "Adzuna", fetch_adzuna,
        needs_keys=["ADZUNA_APP_ID", "ADZUNA_APP_KEY"], default_on=False,
        help_text="Structured salary data. Free developer account.",
    ),
    "careerjet": ProviderSpec(
        "careerjet", "🔎 Careerjet — RO & EU", "Careerjet", fetch_careerjet,
        needs_keys=["CAREERJET_AFFID"], default_on=False,
        help_text="Needs a free affiliate ID from careerjet.com/partners.",
    ),
}


def fetch_source(key: str, **kwargs) -> SourceResult:
    """Run one provider safely, returning a SourceResult in every case."""
    spec = PROVIDERS.get(key)
    if spec is None:
        return SourceResult(source=key, error=f"Unknown source '{key}'")
    return _timed(spec.short_name, spec.fetch, **kwargs)

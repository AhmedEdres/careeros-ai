"""Search orchestration: query expansion, parallel fetching, dedup, ranking."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .matching import MatchResult, calculate_match, classify_remote_geography, hard_filter_job
from .profile import LOCATION_SYNONYMS, Profile
from .tracks import DEFAULT_TRACK, TRACK_AHMED_OFFICE, resolve_track
from .sources import PROVIDERS, SourceResult, build_session, fetch_source
from .text import (
    canonical_url,
    contains_any,
    is_romania_location,
    normalize_text,
    safe_company_name,
    text_hash,
)

__all__ = [
    "CAREER_PRESETS",
    "SearchRequest",
    "SearchReport",
    "build_search_queries",
    "deduplicate_jobs",
    "run_search",
    "score_and_filter",
]


CAREER_PRESETS: Dict[str, List[str]] = {
    "🔥 Full Career Scan (recommended)": [
        "operations coordinator",
        "financial operations",
        "back office",
        "accounts payable",
        "customer support",
        "compliance officer",
    ],
    "💰 Finance & Compliance": [
        "financial operations",
        "tax compliance",
        "accounts payable",
        "accounting specialist",
        "compliance officer",
        "aml kyc analyst",
    ],
    "⚙️ Operations & Back Office": [
        "operations coordinator",
        "back office",
        "operations specialist",
        "shared services",
        "order management",
    ],
    "📞 Customer Support & BPO": [
        "customer support",
        "customer service",
        "client support",
        "arabic customer support",
        "shared services",
    ],
    "🗣️ Arabic-Speaking Roles": [
        "arabic customer support",
        "arabic speaking",
        "arabic english",
        "arabic advisor",
    ],
    "🏭 Logistics & Production": [
        "logistics coordinator",
        "warehouse coordinator",
        "supply chain",
        "production planner",
        "production operator",
        "quality inspector",
    ],
    # Ahmed's primary office identity: Tax / Compliance / Legal / Administration
    # / Operations / Customer Support / BPO / KYC / AML / Banking Operations.
    # Each entry is a meaningful phrase, not a bag of words — see
    # sources/providers.py._keyword_filter for why that matters.
    TRACK_AHMED_OFFICE: [
        "tax specialist",
        "tax compliance",
        "fiscal specialist",
        "compliance specialist",
        "kyc analyst",
        "aml analyst",
        "regulatory compliance",
        "operations specialist",
        "operations coordinator",
        "back office",
        "business operations",
        "customer support",
        "customer service",
        "legal specialist",
        "contract administrator",
        "arabic customer support",
        "finance operations",
        "shared services",
    ],
    "📝 Custom keywords": [],
}

_EXPANSIONS = {
    "customer support": ["customer service", "client support", "arabic customer support"],
    "customer service": ["customer support", "customer care", "arabic customer service"],
    "operations": ["operations coordinator", "operations specialist", "back office operations"],
    "accounting": ["accounts payable", "accounts receivable", "bookkeeper"],
    "finance": ["financial operations", "financial analyst", "financial compliance"],
    "back office": ["back office operations", "shared services", "data entry"],
    "tax": ["tax compliance", "tax specialist", "tax accounting"],
    "compliance": ["compliance officer", "compliance specialist", "regulatory compliance"],
    "kyc": ["kyc analyst", "aml analyst", "compliance analyst"],
    "aml": ["aml analyst", "kyc analyst", "regulatory compliance"],
    "arabic": ["arabic customer support", "arabic speaking", "arabic operations"],
    "sap": ["sap specialist", "erp specialist", "sap operations"],
    "logistics": ["supply chain", "warehouse coordinator", "freight forwarding"],
    "production": ["production operator", "production planner", "quality inspector"],
    "warehouse": ["warehouse coordinator", "inventory controller", "forklift"],
    "legal": ["legal specialist", "legal assistant", "contract administrator"],
    "contract": ["contract administrator", "contract specialist", "legal assistant"],
}

MAX_QUERIES = 6


@dataclass
class SearchRequest:
    keywords: str = ""
    location: str = "Timisoara"
    preset: str = ""
    limit_per_source: int = 20
    sources: Sequence[str] = field(default_factory=lambda: ["jooble", "remotive", "arbeitnow", "jobicy"])
    expand_queries: bool = True
    secrets: Dict[str, str] = field(default_factory=dict)

    def resolved_queries(self) -> List[str]:
        preset_queries = CAREER_PRESETS.get(self.preset) or []
        if preset_queries and not self.keywords.strip():
            return preset_queries[:MAX_QUERIES]
        return build_search_queries(self.keywords or "operations", self.expand_queries)


@dataclass
class SearchReport:
    jobs: List[Dict] = field(default_factory=list)
    results: List[SourceResult] = field(default_factory=list)
    queries: List[str] = field(default_factory=list)
    raw_count: int = 0
    duplicates_removed: int = 0

    @property
    def errors(self) -> List[str]:
        seen, out = set(), []
        for res in self.results:
            if res.error and res.error not in seen:
                seen.add(res.error)
                out.append(res.error)
        return out

    @property
    def counts_by_source(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for res in self.results:
            if res.count:
                counts[res.source] = counts.get(res.source, 0) + res.count
        return counts

    @property
    def timings(self) -> Dict[str, int]:
        timings: Dict[str, int] = {}
        for res in self.results:
            timings[res.source] = max(timings.get(res.source, 0), res.elapsed_ms)
        return timings


def build_search_queries(base_keywords: str, expand: bool = True) -> List[str]:
    """Expand a keyword phrase into a small set of related queries."""
    base = (base_keywords or "").strip()
    if not base:
        return ["operations"]
    queries = [base]
    if expand:
        lowered = normalize_text(base)
        for key, extras in _EXPANSIONS.items():
            if key in lowered:
                queries.extend(extras)
                break

    seen, unique = set(), []
    for query in queries:
        marker = normalize_text(query)
        if marker and marker not in seen:
            seen.add(marker)
            unique.append(query)
    return unique[:MAX_QUERIES]


# Country / work-mode tags boards append to otherwise identical titles:
# "Customer service manager (GR)", "(CY)", "(UK)", "(m/f/d)".
_COUNTRY_SUFFIX_RE = re.compile(
    r"\s*[\(\[]\s*(?:[a-z]{2,3}|remote|hybrid|onsite|on-site|m/f/d|m/w/d|h/f)\s*[\)\]]\s*$"
)


def _campaign_key(job: Dict) -> str:
    """Identity of a job *campaign* — the same opening posted per country.

    Boards such as Jobicy list one role once per target market:
    "Customer service manager (GR)", "(CY)", "(UK)", "(PT)" — same employer,
    same description, four cards crowding out everything else. They share a
    title once the country tag is stripped, so they collapse into one entry
    that keeps the most eligible location.
    """
    title = normalize_text(job.get("title", ""))
    title = _COUNTRY_SUFFIX_RE.sub("", title).strip()
    company = normalize_text(safe_company_name(job.get("company")))
    return text_hash(f"{title}|{company}")


def _job_location_label(job: Dict) -> str:
    return str((job.get("location") or {}).get("display_name", "") or "")


def _location_rank(job: Dict) -> int:
    """Prefer the variant the candidate is most likely to be eligible for.

    Higher is better. Romania (home country) beats a Greece-only or UK-only
    remote posting of the same campaign; EU-wide remote sits in between.
    """
    location = _job_location_label(job)
    description = str(job.get("description", "") or "")
    loc = normalize_text(location)

    if contains_any(loc, LOCATION_SYNONYMS["Timișoara"]):
        return 100
    if is_romania_location(location):
        return 90

    remote = classify_remote_geography(location, description)
    if remote == "remote_country":
        return 90
    if remote == "remote_eu":
        return 70
    if remote == "remote_unclear":
        return 30
    if remote == "restricted":
        return 10
    if contains_any(loc, LOCATION_SYNONYMS["Europe"]):
        return 25
    return 0


def _job_identity(job: Dict) -> Tuple[str, str, str]:
    """Return (url_key, content_key, company) used for deduplication."""
    url_key = canonical_url(job.get("redirect_url", ""))
    title = normalize_text(job.get("title", ""))
    company = normalize_text(safe_company_name(job.get("company")))
    # Only the city matters: "Timisoara" vs "Timisoara, Timis County".
    location = normalize_text(str((job.get("location") or {}).get("display_name", "")))
    location_token = location.split(",")[0].strip()
    content_key = text_hash(f"{title}|{company}|{location_token}")
    return url_key, content_key, company


def deduplicate_jobs(jobs: List[Dict]) -> Tuple[List[Dict], int]:
    """Collapse duplicates, keeping the richest record and merging sources."""
    by_key: Dict[str, Dict] = {}
    order: List[str] = []
    url_to_key: Dict[str, str] = {}
    url_to_company: Dict[str, str] = {}
    removed = 0

    for job in jobs:
        url_key, content_key, company = _job_identity(job)
        key = url_to_key.get(url_key) if url_key else None
        if key is not None and url_to_company.get(url_key) != company:
            # Same redirect URL but a different employer — a shared/generic
            # "apply here" link, not the same posting. Do not merge.
            key = None
        if key is None:
            key = content_key
        if url_key:
            url_to_key[url_key] = key
            url_to_company[url_key] = company

        existing = by_key.get(key)
        if existing is None:
            by_key[key] = job
            order.append(key)
            continue

        removed += 1
        # Keep whichever record carries more information.
        richer, poorer = (
            (job, existing)
            if len(str(job.get("description", ""))) > len(str(existing.get("description", "")))
            else (existing, job)
        )
        merged = dict(richer)
        merged["salary_text"] = richer.get("salary_text") or poorer.get("salary_text", "")
        merged["salary_min"] = richer.get("salary_min") if richer.get("salary_min") is not None else poorer.get("salary_min")
        merged["salary_max"] = richer.get("salary_max") if richer.get("salary_max") is not None else poorer.get("salary_max")
        merged["posted_at"] = richer.get("posted_at") or poorer.get("posted_at", "")
        if merged.get("age_days") is None:
            merged["age_days"] = poorer.get("age_days")
        sources = {
            str(richer.get("source", "")).split(" / ")[0],
            str(poorer.get("source", "")).split(" / ")[0],
        }
        merged["source"] = " + ".join(sorted(s for s in sources if s))
        merged["duplicate_count"] = int(existing.get("duplicate_count", 1)) + 1
        by_key[key] = merged

    deduped = [by_key[k] for k in order]

    # Second pass: collapse per-country reposts of the same campaign.
    campaigns: Dict[str, Dict] = {}
    campaign_order: List[str] = []
    for entry in deduped:
        key = _campaign_key(entry)
        existing = campaigns.get(key)
        if existing is None:
            campaigns[key] = entry
            campaign_order.append(key)
            continue
        removed += 1
        # Keep the variant he is most likely to be eligible for; if two are
        # equal, keep the richer description.
        better = max(
            (existing, entry),
            key=lambda j: (_location_rank(j), len(str(j.get("description", "")))),
        )
        other = entry if better is existing else existing
        merged = dict(better)
        merged["variant_count"] = int(existing.get("variant_count", 1)) + 1
        variants = list(existing.get("variant_locations") or [])
        if not variants:
            existing_loc = _job_location_label(existing)
            if existing_loc:
                variants.append(existing_loc)
        for loc in (_job_location_label(other), _job_location_label(better)):
            if loc and loc not in variants:
                variants.append(loc)
        merged["variant_locations"] = variants
        campaigns[key] = merged

    return [campaigns[k] for k in campaign_order], removed


def run_search(request: SearchRequest, max_workers: int = 8) -> SearchReport:
    """Fetch every (query × source) combination in parallel."""
    queries = request.resolved_queries()
    secrets = request.secrets or {}
    session = build_session()

    def build_kwargs(key: str, query: str, limit: int) -> Dict[str, object]:
        spec = PROVIDERS[key]
        kwargs: Dict[str, object] = {
            "keywords": query,
            "limit": limit,
            "session": session,
        }
        if spec.supports_location:
            kwargs["location"] = request.location
        if key == "jooble":
            kwargs["api_key"] = secrets.get("JOOBLE_API_KEY", "")
            kwargs["pages"] = 2
        elif key == "adzuna":
            kwargs["app_id"] = secrets.get("ADZUNA_APP_ID", "")
            kwargs["app_key"] = secrets.get("ADZUNA_APP_KEY", "")
        elif key == "careerjet":
            kwargs["affid"] = secrets.get("CAREERJET_AFFID", "")
        return kwargs

    tasks = []
    for key in request.sources:
        spec = PROVIDERS.get(key)
        if spec is None:
            continue
        if spec.client_side_filter:
            # These providers download the whole board and filter locally, so
            # calling them once per query would re-download identical payloads.
            # One call is faster and kinder to the free APIs — but it must
            # receive the queries as separate PHRASES, otherwise a merged
            # keyword string degrades into a bag of words and lets unrelated
            # jobs through ("Office Cleaner" for "back office").
            kwargs = build_kwargs(key, " ".join(queries), request.limit_per_source * 2)
            kwargs["phrases"] = list(queries)
            tasks.append((key, kwargs))
        else:
            for query in queries:
                tasks.append((key, build_kwargs(key, query, request.limit_per_source)))

    report = SearchReport(queries=queries)
    if not tasks:
        report.results.append(SourceResult(source="none", error="No search sources selected."))
        return report

    # Drop identical (source, query) pairs that expansion may have produced.
    seen_signatures = set()
    deduped_tasks = []
    for key, kwargs in tasks:
        signature = (key, normalize_text(str(kwargs.get("keywords", ""))))
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        deduped_tasks.append((key, kwargs))

    all_jobs: List[Dict] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_source, key, **kwargs): key
            for key, kwargs in deduped_tasks
        }
        for future in as_completed(futures):
            result = future.result()
            report.results.append(result)
            all_jobs.extend(result.jobs)

    report.raw_count = len(all_jobs)
    report.jobs, report.duplicates_removed = deduplicate_jobs(all_jobs)
    return report


@dataclass
class FilterOptions:
    min_score: int = 35
    location_filter: str = "Romania"
    romanian_filter: str = "Any"
    max_age_days: int = 0            # 0 == no limit
    only_with_salary: bool = False
    hide_language_blocked: bool = True
    hide_applied: bool = False
    applied_urls: Sequence[str] = field(default_factory=list)
    sort_by: str = "Best match"
    track: str = DEFAULT_TRACK


def score_and_filter(
    jobs: List[Dict],
    profile: Profile,
    options: FilterOptions,
) -> Tuple[List[Dict], Dict[str, int]]:
    """Hard-filter, score, soft-filter and sort. Returns (jobs, stats)."""
    from .profile import LOCATION_SYNONYMS
    from .text import contains_any

    stats = {
        "rejected_hard": 0,
        "below_score": 0,
        "filtered_location": 0,
        "filtered_romanian": 0,
        "filtered_age": 0,
        "filtered_salary": 0,
        "filtered_language": 0,
        "filtered_applied": 0,
    }
    applied = {canonical_url(u) for u in options.applied_urls}
    kept: List[Dict] = []
    track = resolve_track(getattr(options, "track", "") or "")

    for job in jobs:
        keep, reason = hard_filter_job(job, profile, track)
        if not keep:
            stats["rejected_hard"] += 1
            continue

        match = calculate_match(job, profile, track)
        job["_match"] = match

        if getattr(match, "verdict", "") == "skip" or getattr(match, "reject_reason", ""):
            stats["rejected_hard"] += 1
            continue

        if match.score < options.min_score:
            stats["below_score"] += 1
            continue

        if options.location_filter != "All":
            synonyms = LOCATION_SYNONYMS.get(options.location_filter, [])
            location_text = normalize_text(str((job.get("location") or {}).get("display_name", "")))
            # Romania / Timișoara means "I work from here": keep remote that
            # is explicitly open to Romania or Europe-wide.
            reachable_remote = match.remote in {"remote_country", "remote_eu"}
            local_hit = synonyms and contains_any(location_text, synonyms)
            if options.location_filter in {"Romania", "Timișoara"}:
                if not local_hit and not reachable_remote:
                    stats["filtered_location"] += 1
                    continue
            elif synonyms and not local_hit:
                stats["filtered_location"] += 1
                continue

        if options.romanian_filter == "Exclude Romanian-required" and match.romanian in ("reject", "risky"):
            stats["filtered_romanian"] += 1
            continue
        if options.romanian_filter == "Beginner-friendly only" and match.romanian == "reject":
            stats["filtered_romanian"] += 1
            continue

        if options.max_age_days:
            age = job.get("age_days")
            if isinstance(age, (int, float)) and age > options.max_age_days:
                stats["filtered_age"] += 1
                continue

        if options.only_with_salary and not (match.salary and match.salary.has_value):
            stats["filtered_salary"] += 1
            continue

        if options.hide_language_blocked and match.blocking_languages:
            stats["filtered_language"] += 1
            continue

        if options.hide_applied and canonical_url(job.get("redirect_url", "")) in applied:
            stats["filtered_applied"] += 1
            continue

        kept.append(job)

    confidence_rank = {"high": 2, "medium": 1, "low": 0}
    if options.sort_by == "Newest first":
        kept.sort(key=lambda j: (
            j.get("age_days") if isinstance(j.get("age_days"), (int, float)) else 999,
            -j["_match"].score,
        ))
    elif options.sort_by == "Highest salary":
        kept.sort(key=lambda j: (
            -((j["_match"].salary.monthly_ron_mid if j["_match"].salary and j["_match"].salary.has_value else 0) or 0),
            -j["_match"].score,
        ))
    else:  # Best match
        kept.sort(key=lambda j: (
            -j["_match"].score,
            -confidence_rank.get(j["_match"].confidence, 0),
            j.get("age_days") if isinstance(j.get("age_days"), (int, float)) else 999,
        ))
    return kept, stats

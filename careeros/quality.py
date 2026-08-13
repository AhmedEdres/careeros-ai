"""Post-processing guardrails for production job-search quality.

This module deliberately sits *after* the proven v4 matcher rather than
rewriting it. It fixes two production-quality issues seen in real results:

1. ranking was too match-heavy (a 98% CV match could still be only a 73%
   hiring reality fit), and
2. different job boards can surface the same opening with slightly different
   URLs, titles or employer labels.

The goal is not to make scores lower; it is to make them more honest and the
result list more useful to a person who actually has to apply.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Dict, Iterable, List, Tuple

from .matching import MatchResult, priority_band
from .text import normalize_text, safe_company_name, text_hash


# Match remains important, but hiring reality now has equal decision weight.
# Eligibility is a practical gate rather than the dominant ranking signal.
REALITY_BLEND = {
    "match": 0.40,
    "eligibility": 0.25,
    "hiring": 0.35,
}

# A recruiter-readiness gate prevents a weak hiring signal from being hidden by
# a large keyword match. These are ceilings, not penalties: a strong hiring
# signal is never reduced.
HIRING_CEILINGS = (
    (50, 65),
    (60, 75),
    (70, 85),
)

_COUNTRY_TAG_RE = re.compile(
    r"\s*[\(\[]\s*(?:[a-z]{2,3}|m/f/d|m/w/d|h/f|remote|hybrid|onsite|on-site)\s*[\)\]]\s*$",
    re.IGNORECASE,
)
_ROLE_NOISE_RE = re.compile(
    r"\b(?:m/f/d|m/w/d|h/f|full[- ]?time|part[- ]?time|urgent|new)\b",
    re.IGNORECASE,
)


def _job_location(job: Dict) -> str:
    value = job.get("location", "")
    if isinstance(value, dict):
        return str(value.get("display_name", "") or "")
    return str(value or "")


def _norm_title(value: object) -> str:
    text = normalize_text(str(value or ""))
    text = _COUNTRY_TAG_RE.sub("", text)
    text = _ROLE_NOISE_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _norm_company(value: object) -> str:
    return re.sub(r"\s+", " ", normalize_text(safe_company_name(value))).strip()


def _norm_location(value: object) -> str:
    text = normalize_text(str(value or ""))
    text = re.sub(r"\b(?:remote|hybrid|onsite|on[- ]site)\b", " ", text)
    return re.sub(r"\s+", " ", text).strip(" ,-|/")


def _description_fingerprint(job: Dict) -> str:
    text = normalize_text(str(job.get("description", "") or ""))
    tokens = re.findall(r"[a-z0-9]{3,}", text)
    return " ".join(tokens[:180])


def _identity(job: Dict) -> Tuple[str, str, str, str]:
    title = _norm_title(job.get("title"))
    company = _norm_company(job.get("company"))
    location = _norm_location(_job_location(job))
    description = _description_fingerprint(job)
    exact = text_hash(f"{title}|{company}|{location}")
    return exact, title, company, description


def _same_campaign(a: Dict, b: Dict) -> bool:
    """Conservative cross-board duplicate test."""
    _, at, ac, ad = _identity(a)
    _, bt, bc, bd = _identity(b)
    if at != bt and SequenceMatcher(None, at, bt).ratio() < 0.94:
        return False
    if ac == bc and _norm_location(_job_location(a)) == _norm_location(_job_location(b)):
        return True
    if not ad or not bd:
        return False
    return SequenceMatcher(None, ad, bd).ratio() >= 0.93


def _merge_jobs(primary: Dict, secondary: Dict) -> Dict:
    """Keep the richer record and preserve useful provenance."""
    primary_desc = str(primary.get("description", "") or "")
    secondary_desc = str(secondary.get("description", "") or "")
    richer, poorer = (primary, secondary) if len(primary_desc) >= len(secondary_desc) else (secondary, primary)
    merged = dict(richer)

    for field in ("salary_text", "salary_currency", "salary_min", "salary_max", "posted_at", "age_days"):
        if merged.get(field) in (None, "", 0) and poorer.get(field) not in (None, "", 0):
            merged[field] = poorer.get(field)

    sources = set()
    for item in (primary, secondary):
        source = str(item.get("source", "") or "")
        if source:
            sources.update(part.strip() for part in source.split(" + ") if part.strip())
    if sources:
        merged["source"] = " + ".join(sorted(sources))

    merged["duplicate_count"] = int(primary.get("duplicate_count", 1)) + int(secondary.get("duplicate_count", 1))
    return merged


def deduplicate_display_jobs(jobs: List[Dict]) -> Tuple[List[Dict], int]:
    """Run a conservative final duplicate pass over already-fetched jobs."""
    kept: List[Dict] = []
    removed = 0
    exact_index: Dict[str, int] = {}

    for job in jobs:
        exact, *_ = _identity(job)
        idx = exact_index.get(exact)
        if idx is not None:
            kept[idx] = _merge_jobs(kept[idx], job)
            removed += 1
            continue

        match_idx = None
        title = _norm_title(job.get("title"))
        for i, existing in enumerate(kept):
            if _norm_title(existing.get("title"))[:1] != title[:1]:
                continue
            if _same_campaign(existing, job):
                match_idx = i
                break

        if match_idx is not None:
            kept[match_idx] = _merge_jobs(kept[match_idx], job)
            removed += 1
            merged_exact, *_ = _identity(kept[match_idx])
            exact_index[merged_exact] = match_idx
            continue

        exact_index[exact] = len(kept)
        kept.append(job)

    return kept, removed


def calibrate_result(result: MatchResult) -> MatchResult:
    """Make the displayed overall score reflect hiring reality.

    v4 already calculates three useful dimensions. We keep those untouched and
    only change the overall decision score used for ranking.
    """
    raw = (
        REALITY_BLEND["match"] * result.match_score
        + REALITY_BLEND["eligibility"] * result.eligibility_score
        + REALITY_BLEND["hiring"] * result.hiring_score
    )
    score = int(round(max(0, min(100, raw))))

    for minimum_hiring, ceiling in HIRING_CEILINGS:
        if result.hiring_score < minimum_hiring:
            score = min(score, ceiling)
            break

    # Confidence should be a ranking/tie-break signal, not a blunt penalty.
    # A short but obviously relevant local posting may still deserve APPLY.
    # Only prevent near-perfect claims when the evidence is genuinely thin.
    if result.confidence == "low" and score > 88:
        score = 88
    elif result.confidence == "medium" and score > 95:
        score = 95

    result.score = score
    result.verdict_label, result.verdict = priority_band(score, result.confidence)
    result.apply_signals = list(result.reasons[:8])
    result.apply_risks = list(dict.fromkeys(result.warnings + result.hiring_risks))[:6]
    return result


def calibrate_jobs(jobs: Iterable[Dict]) -> None:
    """Calibrate scores in-place after the matcher has populated ``_match``."""
    for job in jobs:
        match = job.get("_match")
        if isinstance(match, MatchResult):
            calibrate_result(match)

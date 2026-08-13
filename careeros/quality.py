"""Post-processing guardrails for production job-search quality."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Dict, Iterable, List, Optional, Tuple

from .matching import MatchResult, blend_scores, priority_band
from .text import normalize_text, safe_company_name, text_hash


REALITY_BLEND = {"match": 0.40, "eligibility": 0.25, "hiring": 0.35}
# If recruiter-readiness is below 70, the overall score cannot exceed 75;
# below 50 it cannot exceed 65. This prevents a very high keyword match from
# masking a weak real-world hiring signal.
HIRING_CEILINGS = ((50, 65), (70, 75), (80, 85))

_COUNTRY_TAG_RE = re.compile(
    r"\s*[\(\[]\s*(?:[a-z]{2,3}|m/f/d|m/w/d|h/f|remote|hybrid|onsite|on-site)\s*[\)\]]\s*$",
    re.IGNORECASE,
)
_ROLE_NOISE_RE = re.compile(
    r"\b(?:m/f/d|m/w/d|h/f|full[- ]?time|part[- ]?time|urgent|new)\b", re.IGNORECASE
)

_MANAGEMENT_TITLE_RE = re.compile(
    r"\b(?:operations|operational|finance|financial|compliance|legal|logistics|supply\s+chain|"
    r"warehouse|procurement|production|manufacturing|service\s+delivery|shared\s+services|"
    r"department|regional|program|programme|project)\s+manager\b|"
    r"\b(?:head\s+of|director\s+of|vp\s+of|vice\s+president\s+of|chief\s+\w+\s+officer)\b|"
    r"\b(?:team\s+lead|people\s+manager|line\s+manager|supervisor)\b",
    re.IGNORECASE,
)

_MANAGEMENT_EVIDENCE = (
    "managed a team", "managed team", "team of", "direct reports", "people management",
    "staff management", "supervised staff", "supervised a team", "led a team",
    "led teams", "team leadership", "hiring and performance", "performance reviews",
    "workforce management", "p&l responsibility", "p&l ownership", "budget ownership",
    "budget management", "department head", "managed employees", "managed staff",
)

_REQUIRED_CREDENTIAL_PATTERNS = (
    r"(?:pmp|prince2|acca|cpa|cfa|cia|cisa|itil|six\s+sigma|iso\s*27001)"
    r"[^.]{0,60}(?:required|mandatory|must\s+have|essential)",
    r"(?:required|mandatory|must\s+have|essential)[^.]{0,60}"
    r"(?:pmp|prince2|acca|cpa|cfa|cia|cisa|itil|six\s+sigma|iso\s*27001)",
)
_CREDENTIAL_TOKENS = (
    "pmp", "prince2", "acca", "cpa", "cfa", "cia", "cisa", "itil", "six sigma", "iso 27001",
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
    p_desc = str(primary.get("description", "") or "")
    s_desc = str(secondary.get("description", "") or "")
    richer, poorer = (primary, secondary) if len(p_desc) >= len(s_desc) else (secondary, primary)
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


def _profile_evidence_text(profile) -> str:
    if profile is None:
        return ""
    skills = " ".join(str(x or "") for x in (getattr(profile, "skills", []) or []))
    highlights = " ".join(str(x or "") for x in (getattr(profile, "highlights", []) or []))
    return normalize_text(f"{skills} {highlights}")


def _management_realism(job: Optional[Dict], profile) -> Tuple[int, str]:
    if not job or profile is None:
        return 0, ""
    title = normalize_text(str(job.get("title", "") or ""))
    description = normalize_text(str(job.get("description", "") or ""))
    if not _MANAGEMENT_TITLE_RE.search(title):
        return 0, ""
    evidence = _profile_evidence_text(profile)
    if any(term in evidence for term in _MANAGEMENT_EVIDENCE):
        return 0, ""
    penalty = 10
    if any(term in description for term in ("manage a team", "manage a team of", "direct reports", "people management", "lead a team")):
        penalty += 5
    return penalty, "⚠️ Management scope is not demonstrated in the documented profile"


def _credential_gap(job: Optional[Dict], profile) -> Tuple[int, str]:
    if not job or profile is None:
        return 0, ""
    description = normalize_text(str(job.get("description", "") or ""))
    if not description:
        return 0, ""
    if not any(re.search(pattern, description, flags=re.IGNORECASE) for pattern in _REQUIRED_CREDENTIAL_PATTERNS):
        return 0, ""
    evidence = _profile_evidence_text(profile)
    if any(re.search(r"\b" + re.escape(credential) + r"\b", evidence) for credential in _CREDENTIAL_TOKENS):
        return 0, ""
    return 8, "⚠️ Posting has a mandatory certification gate not evidenced in the profile"


def calibrate_result(result: MatchResult, job: Optional[Dict] = None, profile=None) -> MatchResult:
    """Apply recruiter-realism guardrails without changing the three visible scores' meaning."""
    management_penalty, management_risk = _management_realism(job, profile)
    credential_penalty, credential_risk = _credential_gap(job, profile)
    if management_penalty:
        result.hiring_score = max(0, result.hiring_score - management_penalty)
        result.hiring_risks.append(management_risk)
        result.adjustments.append(("Management-scope realism", -management_penalty))
    if credential_penalty:
        result.hiring_score = max(0, result.hiring_score - credential_penalty)
        result.hiring_risks.append(credential_risk)
        result.adjustments.append(("Mandatory certification gap", -credential_penalty))

    guardrail_applied = bool(management_penalty or credential_penalty)
    raw = (
        REALITY_BLEND["match"] * result.match_score
        + REALITY_BLEND["eligibility"] * result.eligibility_score
        + REALITY_BLEND["hiring"] * result.hiring_score
    )
    score = int(round(max(0, min(100, raw))))

    if result.hiring_score >= 80 and not guardrail_applied:
        score = blend_scores(result.match_score, result.eligibility_score, result.hiring_score)

    for minimum_hiring, ceiling in HIRING_CEILINGS:
        if result.hiring_score < minimum_hiring:
            score = min(score, ceiling)
            break

    if (
        not guardrail_applied
        and result.match_score >= 80
        and result.eligibility_score >= 80
        and result.hiring_score >= 65
    ):
        score = max(score, 80)

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
    for job in jobs:
        match = job.get("_match")
        if isinstance(match, MatchResult):
            calibrate_result(match)

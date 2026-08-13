"""Post-processing guardrails for production job-search quality."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Dict, Iterable, List, Optional, Tuple

from .matching import MatchResult, blend_scores, priority_band
from .text import normalize_text, safe_company_name, text_hash


# The quality layer deliberately gives recruiter reality more influence than
# raw keyword similarity.  This is the final ranking layer used by the public
# matcher in careeros/__init__.py.
REALITY_BLEND = {"match": 0.40, "eligibility": 0.25, "hiring": 0.35}

# Recruiter-readiness ceilings. A high semantic match must not rescue a role
# where the documented profile would normally fail the first screening pass.
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

# These are specialist families where generic words such as "coordinator",
# "specialist", "manager", "operations" or "compliance" can create a very
# misleading high score.  A candidate with adjacent tools/experience should
# remain visible, but the role must be marked as a stretch unless the profile
# contains direct evidence of that specialist family.
_SPECIALIZED_FAMILIES = {
    "it_technical": (
        "it", "information technology", "information systems", "network", "systems administrator",
        "system administrator", "infrastructure", "service now", "servicenow", "cybersecurity",
        "cyber security", "cloud", "azure", "aws", "devops", "sre", "database administrator",
        "technical support", "it support", "desktop support", "it infrastructure",
    ),
    "software_data": (
        "software", "developer", "programmer", "data scientist", "data engineer", "machine learning",
        "ml engineer", "python", "java", "javascript", "react", "backend", "frontend", "full stack",
        "sql developer", "analytics engineer",
    ),
    "engineering": (
        "mechanical engineer", "electrical engineer", "industrial engineer", "civil engineer",
        "process engineer", "manufacturing engineer", "automation engineer", "quality engineer",
        "design engineer", "engineering specialist", "engineering manager",
    ),
    "procurement": (
        "strategic procurement", "category manager", "category buyer", "buyer", "sourcing manager",
        "procurement manager", "strategic sourcing", "vendor manager",
    ),
    "freight_specialist": (
        "freight forwarder", "freight forwarding", "customs broker", "customs specialist",
        "import export specialist", "trade compliance specialist",
    ),
}

_SPECIALIZED_TITLE_PATTERNS = {
    family: re.compile(
        r"(?:" + "|".join(re.escape(term) for term in terms) + r")",
        re.IGNORECASE,
    )
    for family, terms in _SPECIALIZED_FAMILIES.items()
}

# Profile evidence is intentionally stronger when it appears in the candidate
# skills/highlights than when it is merely a generic word in a job description.
_PROFILE_FAMILY_EVIDENCE = {
    "it_technical": (
        "it", "information technology", "information systems", "network", "infrastructure",
        "servicenow", "service now", "cybersecurity", "cloud", "azure", "aws", "devops",
        "system administrator", "technical support", "it support",
    ),
    "software_data": (
        "software", "developer", "programming", "data scientist", "data engineer", "machine learning",
        "python", "java", "javascript", "sql", "power bi", "analytics",
    ),
    "engineering": (
        "engineer", "engineering", "mechanical", "electrical", "industrial engineering",
        "process engineering", "automation", "manufacturing engineering",
    ),
    "procurement": (
        "procurement", "purchasing", "sourcing", "buyer", "vendor management", "category management",
    ),
    "freight_specialist": (
        "freight", "freight forwarding", "forwarding", "customs", "import export", "trade compliance",
    ),
}


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
    education = str(getattr(profile, "education", "") or "")
    return normalize_text(f"{skills} {highlights} {education}")


def _management_realism(job: Optional[Dict], profile) -> Tuple[int, str]:
    """Penalise leadership scope that is not evidenced by the profile.

    Ten years of experience is not automatically ten years of people management.
    This distinction is important for Operations Manager / Regional Manager roles.
    """
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


def _specialized_family(job: Optional[Dict]) -> Optional[str]:
    if not job:
        return None
    title = normalize_text(str(job.get("title", "") or ""))
    # Title-only by design: a random description mention of "IT systems" must
    # not turn an otherwise suitable compliance/operations job into an IT role.
    for family, pattern in _SPECIALIZED_TITLE_PATTERNS.items():
        if pattern.search(title):
            return family
    return None


def _specialized_transfer_penalty(job: Optional[Dict], profile) -> Tuple[int, str]:
    """Detect specialist false positives that generic keyword matching misses.

    Example: "Senior IT Locations Coordinator" can match coordinator + operations
    + SAP/SQL and look like 80%+, while the actual role may demand IT infrastructure
    experience. We keep it visible as a stretch rather than treating it as a normal
    apply.
    """
    if not job or profile is None:
        return 0, ""
    title = normalize_text(str(job.get("title", "") or ""))
    family = _specialized_family(job)
    if not family:
        return 0, ""

    evidence = _profile_evidence_text(profile)
    family_evidence = _PROFILE_FAMILY_EVIDENCE.get(family, ())
    direct = [term for term in family_evidence if term in evidence]
    if direct:
        return 0, ""

    senior = bool(re.search(r"\b(?:senior|sr\.?|lead|principal|head|director|manager)\b", title))
    # Freight/logistics is adjacent to the candidate's documented logistics
    # exposure, so use a lighter penalty than IT/software/engineering.
    if family == "freight_specialist":
        penalty = 6
        risk = "⚠️ Freight/trade specialism is adjacent, but direct forwarding/customs experience is not documented"
    elif family == "procurement":
        penalty = 8
        risk = "⚠️ Procurement specialism is not directly evidenced in the profile"
    elif family == "it_technical":
        penalty = 15 if senior else 12
        risk = "⚠️ IT/technical specialism is not directly evidenced; coordinator/operations keywords are not enough"
    elif family == "software_data":
        penalty = 18 if senior else 15
        risk = "⚠️ Software/data specialism is not directly evidenced in the profile"
    else:  # engineering
        penalty = 16 if senior else 13
        risk = "⚠️ Engineering specialism is not directly evidenced in the profile"
    return penalty, risk


def _seniority_realism(job: Optional[Dict], profile) -> Tuple[int, str]:
    """Add a modest penalty for senior roles that exceed documented scope.

    Do not punish every senior title: the candidate has 10+ years and senior
    specialist roles can be realistic. Penalise only when the posting signals
    a leadership scope or a senior specialist family without evidence.
    """
    if not job or profile is None:
        return 0, ""
    title = normalize_text(str(job.get("title", "") or ""))
    if not re.search(r"\b(?:senior|sr\.?|lead|principal|head|director|manager)\b", title):
        return 0, ""
    # Management scope is handled separately; avoid double-penalising the same
    # signal for a plain manager title.
    if _MANAGEMENT_TITLE_RE.search(title):
        return 0, ""
    family = _specialized_family(job)
    if family is None:
        return 0, ""
    return _specialized_transfer_penalty(job, profile)


def _apply_realism_penalty(result: MatchResult, penalty: int, risk: str, label: str) -> None:
    if not penalty:
        return
    result.hiring_score = max(0, result.hiring_score - penalty)
    if risk:
        result.hiring_risks.append(risk)
    result.adjustments.append((label, -penalty))


def calibrate_result(result: MatchResult, job: Optional[Dict] = None, profile=None) -> MatchResult:
    """Apply recruiter-realism guardrails without changing score semantics."""
    management_penalty, management_risk = _management_realism(job, profile)
    credential_penalty, credential_risk = _credential_gap(job, profile)
    specialized_penalty, specialized_risk = _specialized_transfer_penalty(job, profile)

    # If the specialist penalty already captures the seniority mismatch, do not
    # add a second penalty for the same missing evidence.
    _apply_realism_penalty(result, management_penalty, management_risk, "Management-scope realism")
    _apply_realism_penalty(result, credential_penalty, credential_risk, "Mandatory certification gap")
    _apply_realism_penalty(result, specialized_penalty, specialized_risk, "Specialist-transfer realism")

    guardrail_applied = bool(management_penalty or credential_penalty or specialized_penalty)
    raw = (
        REALITY_BLEND["match"] * result.match_score
        + REALITY_BLEND["eligibility"] * result.eligibility_score
        + REALITY_BLEND["hiring"] * result.hiring_score
    )
    score = int(round(max(0, min(100, raw))))

    # High-match jobs still need recruiter readiness.  This is intentionally
    # applied after penalties so the visible score is the realistic score.
    for minimum_hiring, ceiling in HIRING_CEILINGS:
        if result.hiring_score < minimum_hiring:
            score = min(score, ceiling)
            break

    # Never force an 80+ score after a realism guardrail.  Previously this
    # exception could restore a high score after a meaningful mismatch.
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
    result.apply_risks = list(dict.fromkeys(result.warnings + result.hiring_risks))[:8]
    return result


def calibrate_jobs(jobs: Iterable[Dict]) -> None:
    for job in jobs:
        match = job.get("_match")
        if isinstance(match, MatchResult):
            calibrate_result(match)

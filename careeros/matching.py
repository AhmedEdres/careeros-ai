"""Matching engine v3 — evidence-based, explainable job scoring.

Design rules
------------
* **Zero-default**: a dimension only earns points on positive evidence.
* **Confidence-aware**: short listings (snippets) cannot be judged as harshly
  as full descriptions, so the final score is reported together with a
  confidence level instead of pretending a 120-character snippet is complete.
* **Explainable**: every dimension returns the evidence that produced it.
* **Whole-word matching**: prevents "eu" matching "Deutschland".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .profile import (
    LOCATION_SYNONYMS,
    NEGATIVE_TITLES,
    Profile,
    REMOTE_FRIENDLY,
    REMOTE_RESTRICTED,
    ROMANIAN_FRIENDLY,
    ROMANIAN_REJECT,
    ROMANIAN_RISKY,
    SENIORITY_PATTERNS,
    SKILL_GROUPS,
)
from .salary import SalaryInfo, parse_salary
from .text import (
    clean_html_text,
    contains_any,
    contains_phrase,
    matched_phrases,
    normalize_text,
    safe_company_name,
)

__all__ = [
    "MatchResult",
    "DIMENSION_MAX",
    "calculate_match",
    "hard_filter_job",
    "classify_language_mention",
    "classify_romanian_requirement",
    "classify_remote_geography",
    "priority_band",
]

DIMENSION_MAX = {
    "location": 20,
    "skills": 25,
    "arabic": 15,
    "english": 10,
    "experience": 10,
    "salary": 10,
    "education": 5,
    "relevance": 5,
}

MAX_ROMANIAN_BONUS = 5
MAX_ROMANIAN_PENALTY = -12


@dataclass
class MatchResult:
    score: int = 0
    dimensions: Dict[str, int] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence: str = "medium"
    romanian: str = "none"
    remote: str = "not_remote"
    salary: Optional[SalaryInfo] = None
    adjustments: List[Tuple[str, int]] = field(default_factory=list)
    blocking_languages: List[str] = field(default_factory=list)
    normalised: bool = False
    attainable: int = 100

    def as_dict(self) -> Dict:
        return {
            "score": self.score,
            "dimensions": self.dimensions,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "confidence": self.confidence,
            "romanian": self.romanian,
            "remote": self.remote,
            "blocking_languages": self.blocking_languages,
        }


# ---------------------------------------------------------------------------
# Job field access helpers (jobs are plain dicts coming from the sources)
# ---------------------------------------------------------------------------
def _job_location(job: Dict) -> str:
    loc = job.get("location")
    if isinstance(loc, dict):
        return str(loc.get("display_name", "") or "")
    return str(loc or "")


def _job_category(job: Dict) -> str:
    cat = job.get("category")
    if isinstance(cat, dict):
        return str(cat.get("label", "") or "")
    return str(cat or "")


def _job_text(job: Dict) -> Tuple[str, str, str, str]:
    """Return (full_text, title, location, description) — all normalised."""
    title = str(job.get("title", "") or "")
    description = clean_html_text(job.get("description", ""))
    company = safe_company_name(job.get("company"))
    category = _job_category(job)
    location = _job_location(job)
    full = normalize_text(f"{title} {description} {company} {category} {location}")
    return full, normalize_text(title), normalize_text(location), normalize_text(description)


# ---------------------------------------------------------------------------
# Classifiers
# ---------------------------------------------------------------------------
def classify_language_mention(text: str, lang: str) -> str:
    """Classify how a language appears: required / preferred / plus / mentioned / none."""
    lang = normalize_text(lang)
    if not contains_phrase(text, lang):
        return "none"

    required = [
        f"{lang} required", f"{lang} is required", f"{lang} mandatory",
        f"{lang} is mandatory", f"fluent {lang}", f"{lang} fluent",
        f"fluent in {lang}", f"fluency in {lang}", f"native {lang}",
        f"{lang} native", f"{lang} speaker", f"{lang} speaking",
        f"{lang} c1", f"{lang} c2", f"proficient in {lang}",
        f"excellent {lang}", f"must speak {lang}",
    ]
    preferred = [
        f"{lang} preferred", f"{lang} is preferred", f"{lang} b2",
        f"{lang} advanced", f"advanced {lang}", f"good {lang}",
        f"good command of {lang}", f"solid {lang}",
    ]
    plus = [
        f"{lang} is a plus", f"{lang} a plus", f"{lang} is an advantage",
        f"{lang} advantage", f"{lang} is a bonus", f"{lang} bonus",
        f"{lang} nice to have", f"{lang} desirable", f"{lang} would be nice",
        f"knowledge of {lang}", f"{lang} b1", f"{lang} a2",
    ]

    if contains_any(text, required):
        return "required"
    if contains_any(text, preferred):
        return "preferred"
    if contains_any(text, plus):
        return "plus"
    return "mentioned"


def classify_romanian_requirement(text: str) -> str:
    """Return one of: reject / risky / friendly / none."""
    if contains_any(text, ROMANIAN_REJECT):
        return "reject"
    if contains_any(text, ROMANIAN_FRIENDLY):
        return "friendly"
    if contains_any(text, ROMANIAN_RISKY):
        return "risky"
    if contains_any(text, ["romanian", "romana", "limba romana"]):
        return "risky"
    return "none"


def classify_remote_geography(location_text: str, description_text: str) -> str:
    """Return: excellent / good / restricted / not_remote."""
    loc = normalize_text(location_text)
    desc = normalize_text(description_text)
    combined = f"{loc} {desc[:1500]}"

    is_remote = contains_any(loc, ["remote", "work from home", "wfh", "telemunca", "anywhere"]) \
        or contains_any(desc[:600], ["fully remote", "100% remote", "remote first", "work from home"])
    if not is_remote:
        return "not_remote"

    if contains_any(combined, REMOTE_RESTRICTED):
        return "restricted"
    if contains_any(combined, REMOTE_FRIENDLY):
        return "excellent"
    if contains_any(loc, LOCATION_SYNONYMS["Europe"]):
        return "excellent"
    return "good"


HIGH_PRIORITY_THRESHOLD = 80
MEDIUM_PRIORITY_THRESHOLD = 55


def priority_band(score: int, confidence: str = "medium") -> Tuple[str, str]:
    """Map a score to a (label, band) badge.

    Thresholds sit at 80/55 because scores are normalised against the
    attainable points: a strong local match now genuinely reaches the 80s, so a
    lower bar would mark almost everything "high priority" and tell the user
    nothing.
    """
    if score >= HIGH_PRIORITY_THRESHOLD:
        return "🔥 HIGH PRIORITY", "high"
    if score >= MEDIUM_PRIORITY_THRESHOLD:
        return "🟡 WORTH A LOOK", "medium"
    return "⚪ LOW PRIORITY", "low"


# ---------------------------------------------------------------------------
# Hard filter
# ---------------------------------------------------------------------------
def hard_filter_job(job: Dict, profile: Profile) -> Tuple[bool, str]:
    """Reject hopeless listings before scoring. Returns (keep, reason)."""
    full, title, loc, desc = _job_text(job)

    if not str(job.get("title", "")).strip():
        return False, "Missing title"

    # 1. Romanian far above the candidate's level.
    if profile.romanian_rank < 4 and contains_any(full, ROMANIAN_REJECT):
        return False, "🔴 Requires advanced Romanian (C1/C2/fluent/native)"

    # 2. Geographically restricted remote roles.
    if contains_any(loc, REMOTE_RESTRICTED):
        return False, "🔴 Geographically restricted (outside EU)"
    if classify_remote_geography(loc, desc) == "restricted":
        return False, "🔴 Remote but restricted to a non-EU region"

    # 3. Clearly different career track (title only — descriptions mention
    #    unrelated teams too often to be trusted here).
    wrong_track = matched_phrases(title, NEGATIVE_TITLES)
    if wrong_track:
        return False, f"🔴 Different career track ({wrong_track[0]})"

    return True, ""


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------
def _score_location(loc: str, desc: str, profile: Profile, result: MatchResult) -> int:
    home = normalize_text(profile.location)
    remote_class = classify_remote_geography(loc, desc)
    result.remote = remote_class

    if home and contains_phrase(loc, home):
        result.reasons.append(f"📍 {profile.location} — perfect location match")
        return 20
    if contains_any(loc, LOCATION_SYNONYMS["Timișoara"]):
        result.reasons.append("📍 Timișoara area — no relocation needed")
        return 20
    if contains_any(loc, LOCATION_SYNONYMS["Romania"]):
        result.reasons.append("🇷🇴 Romania — same country, work authorisation OK")
        return 15

    if remote_class == "excellent":
        result.reasons.append("🏠 Remote — EU/Europe/worldwide eligible")
        return 16
    if remote_class == "good":
        result.reasons.append("🏠 Remote — eligibility not stated")
        result.warnings.append("⚠️ Remote without an explicit EU mention — confirm Romania is eligible")
        return 10
    if remote_class == "restricted":
        result.warnings.append("⚠️ Remote role restricted to another region")
        return 2

    if contains_any(loc, LOCATION_SYNONYMS["Europe"]):
        if profile.open_to_relocation:
            result.reasons.append("🌍 Europe-based — relocation possible")
            return 10
        result.warnings.append("⚠️ Outside Romania — would require relocation")
        return 5

    if not loc.strip():
        result.warnings.append("⚠️ Location not stated in the listing")
        return 0
    result.warnings.append("⚠️ Location outside your target area")
    return 0


def _score_skills(full: str, title: str, result: MatchResult) -> int:
    total = 0
    labels: List[str] = []
    for group in SKILL_GROUPS.values():
        hits = matched_phrases(full, group["words"])
        if not hits:
            continue
        # Title hits are far stronger evidence than a passing mention.
        in_title = any(contains_phrase(title, hit) for hit in hits)
        weight = group["weight"] + (3 if in_title else 0)
        # Multiple distinct hits inside a group add a little extra confidence.
        weight += min(len(hits) - 1, 2)
        total += weight
        labels.append(group["label"])

    capped = min(total, DIMENSION_MAX["skills"])
    if labels:
        result.reasons.append(
            f"💼 Skills match: {', '.join(labels[:3])} ({capped}/{DIMENSION_MAX['skills']})"
        )
    else:
        result.warnings.append("⚠️ No familiar skill keywords found in this listing")
    return capped


def _score_arabic(full: str, result: MatchResult) -> int:
    level = classify_language_mention(full, "arabic")
    if level == "required":
        result.reasons.append("🗣️ Arabic required — your strongest differentiator")
        return 15
    if level == "preferred":
        result.reasons.append("🗣️ Arabic preferred — strong advantage")
        return 12
    if level == "plus":
        result.reasons.append("🗣️ Arabic is a plus")
        return 10
    if level == "mentioned":
        result.reasons.append("🗣️ Arabic mentioned in the listing")
        return 7
    if contains_any(full, ["multilingual", "bilingual", "mena", "middle east", "gulf"]):
        result.reasons.append("🌐 Multilingual/MENA context — Arabic is an asset")
        return 4
    return 0


def _score_english(full: str, result: MatchResult) -> int:
    level = classify_language_mention(full, "english")
    if level == "required":
        result.reasons.append("🇬🇧 English required — matches your B2+ level")
        return 10
    if level == "preferred":
        result.reasons.append("🇬🇧 English preferred")
        return 8
    if level in ("plus", "mentioned"):
        result.reasons.append("🇬🇧 English mentioned")
        return 6
    return 0


def _extract_required_years(text: str) -> Optional[int]:
    patterns = [
        r"(\d{1,2})\s*\+?\s*(?:-|to)?\s*\d{0,2}\s*years?\s+(?:of\s+)?experience",
        r"minimum\s+(?:of\s+)?(\d{1,2})\s*years?",
        r"at least\s+(\d{1,2})\s*years?",
        r"(\d{1,2})\s*ani\s+experienta",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                years = int(match.group(1))
            except (TypeError, ValueError):
                continue
            if 0 < years <= 30:
                return years
    return None


def _score_experience(full: str, title: str, profile: Profile, result: MatchResult) -> int:
    required = _extract_required_years(full)
    score = 0

    if contains_any(title, SENIORITY_PATTERNS["leadership"]):
        score = 9
        result.reasons.append(f"🧑‍💼 Leadership role — fits {profile.experience_years}+ years")
    elif contains_any(title, SENIORITY_PATTERNS["senior"]):
        score = 9
        result.reasons.append("🧑‍💼 Senior level — matches your seniority")
    elif contains_any(title, SENIORITY_PATTERNS["mid"]):
        score = 8
        result.reasons.append("🧑‍💼 Specialist/coordinator level — good fit")
    elif contains_any(title, SENIORITY_PATTERNS["junior"]):
        score = 4
        result.warnings.append("⚠️ Entry-level title — likely below your experience and salary target")
    else:
        score = 3

    if required is not None:
        if required <= profile.experience_years:
            score = min(DIMENSION_MAX["experience"], score + 1)
            result.reasons.append(f"✅ Asks for {required}+ years — you have {profile.experience_years}")
        else:
            score = max(0, score - 3)
            result.warnings.append(f"⚠️ Asks for {required}+ years of experience")
    return min(score, DIMENSION_MAX["experience"])


# Boilerplate that mentions "legal" without the role being legal work.
_LEGAL_BOILERPLATE = [
    "legal requirements", "legal obligations", "legal regulations",
    "legal framework", "legally required", "legal reasons", "legal basis",
    "equal opportunity", "legally authorized", "legally authorised",
    "legal working age", "legal entity", "legal notice", "in accordance with legal",
]


def _score_education(full: str, title: str, profile: Profile, result: MatchResult) -> int:
    edu = normalize_text(profile.education)
    legal_terms = ["law", "legal", "juridic", "lawyer", "jurist", "paralegal", "counsel"]

    # Only credit a legal background when the ROLE is legal — not when the ad
    # merely says it complies with "legal requirements".
    legal_in_title = contains_any(title, legal_terms)

    # Strip boilerplate phrases before deciding whether "legal" is meaningful.
    body_without_boilerplate = full
    for phrase in _LEGAL_BOILERPLATE:
        body_without_boilerplate = body_without_boilerplate.replace(normalize_text(phrase), " ")

    legal_in_body = contains_any(body_without_boilerplate, legal_terms)

    if "law" in edu and legal_in_title:
        result.reasons.append("🎓 Legal role — your Law degree is directly relevant")
        return 5
    if "law" in edu and legal_in_body:
        result.reasons.append("🎓 Legal/compliance exposure — Law degree is an asset")
        return 4
    if contains_any(full, ["master", "masters", "postgraduate"]):
        result.reasons.append("🎓 Master's degree relevant")
        return 4
    if contains_any(full, ["bachelor", "university degree", "higher education", "studii superioare", "degree"]):
        result.reasons.append("🎓 Degree requirement satisfied")
        return 3
    return 0


def _score_salary(job: Dict, profile: Profile, result: MatchResult) -> int:
    info = parse_salary(
        job.get("salary_text", ""),
        fallback_min=job.get("salary_min"),
        fallback_max=job.get("salary_max"),
        currency_hint=job.get("salary_currency"),
    )
    result.salary = info

    if not info.has_value:
        result.warnings.append("⚠️ Salary not published — ask early in the process")
        return 0

    best = info.monthly_ron_max or info.monthly_ron_min or 0
    target_min = float(profile.target_salary_min or 0)

    if target_min <= 0:
        return 5
    if best >= float(profile.target_salary_max or target_min):
        result.reasons.append(f"💰 Salary at/above your target (≈{best:,.0f} RON/month)")
        return 10
    if best >= target_min:
        result.reasons.append(f"💰 Salary meets your minimum (≈{best:,.0f} RON/month)")
        return 9
    if best >= target_min * 0.85:
        result.reasons.append(f"💰 Salary slightly below target (≈{best:,.0f} RON/month)")
        return 6
    if best >= target_min * 0.7:
        result.warnings.append(f"⚠️ Salary below target (≈{best:,.0f} RON/month)")
        return 3
    result.warnings.append(f"🔴 Salary well below target (≈{best:,.0f} RON/month)")
    return 0


def required_foreign_languages(full: str, profile: Profile) -> List[str]:
    """Languages the posting *requires* that the candidate does not speak."""
    blocking = []
    for language in profile.other_languages:
        if classify_language_mention(full, language) == "required":
            blocking.append(language)
    return blocking


def _score_relevance(full: str, result: MatchResult) -> int:
    if contains_any(full, ["bpo", "shared services", "shared service", "outsourcing",
                           "middle east", "mena", "gulf", "gcc"]):
        result.reasons.append("🌐 BPO / Shared services / MENA — high relevance to your background")
        return 5
    if contains_any(full, ["multilingual", "bilingual", "international team", "global team"]):
        result.reasons.append("🌐 International/multilingual environment")
        return 3
    return 0


def _confidence(description: str, job: Dict) -> str:
    """How much do we trust this score? Snippets carry far less signal."""
    length = len(clean_html_text(job.get("description", "")))
    if length >= 900:
        return "high"
    if length >= 250:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def calculate_match(job: Dict, profile: Profile) -> MatchResult:
    """Score a job against the profile and explain the result."""
    full, title, loc, desc = _job_text(job)
    result = MatchResult()

    dims = {
        "location": _score_location(loc, desc, profile, result),
        "skills": _score_skills(full, title, result),
        "arabic": _score_arabic(full, result),
        "english": _score_english(full, result),
        "experience": _score_experience(full, title, profile, result),
        "salary": _score_salary(job, profile, result),
        "education": _score_education(full, title, profile, result),
        "relevance": _score_relevance(full, result),
    }
    total = sum(dims.values())

    # --- Romanian compatibility adjustment ---------------------------------
    romanian = classify_romanian_requirement(full)
    result.romanian = romanian
    if romanian == "friendly":
        total += MAX_ROMANIAN_BONUS
        result.adjustments.append(("Romanian beginner-friendly", MAX_ROMANIAN_BONUS))
        result.reasons.append("🟢 Romanian optional/beginner — compatible with your level")
    elif romanian == "risky":
        gap = max(0, 4 - profile.romanian_rank)  # 4 == B2
        penalty = max(MAX_ROMANIAN_PENALTY, -3 * gap) if gap else 0
        if penalty:
            total += penalty
            result.adjustments.append(("Romanian likely required", penalty))
            result.warnings.append("🟠 Romanian may be required — verify before applying")
    elif romanian == "reject":
        total += MAX_ROMANIAN_PENALTY
        result.adjustments.append(("Advanced Romanian required", MAX_ROMANIAN_PENALTY))
        result.warnings.append("🔴 Advanced Romanian required")

    # --- Languages the candidate does not speak ----------------------------
    # A required French/German/Dutch posting is effectively closed to him, so
    # it must never outrank a role he can actually get.
    blocking_languages = required_foreign_languages(full, profile)
    if blocking_languages:
        names = ", ".join(lang.title() for lang in blocking_languages[:3])
        penalty = -30 if len(blocking_languages) == 1 else -40
        total += penalty
        result.adjustments.append((f"Requires {names}", penalty))
        result.warnings.insert(0, f"🔴 Requires fluent {names} — not in your profile")
        result.blocking_languages = blocking_languages

    # --- Freshness nudge ---------------------------------------------------
    age_days = job.get("age_days")
    if isinstance(age_days, (int, float)):
        if age_days <= 3:
            total += 3
            result.adjustments.append(("Posted in the last 3 days", 3))
            result.reasons.append("🆕 Posted within the last 3 days")
        elif age_days <= 7:
            total += 1
            result.adjustments.append(("Posted this week", 1))
        elif age_days > 45:
            total -= 3
            result.adjustments.append(("Posting older than 45 days", -3))
            result.warnings.append("⚠️ Listing is over 45 days old — may be filled")

    # --- Normalise against what was actually knowable ----------------------
    # Arabic and salary are rarely mentioned at all. Scoring them out of the
    # full 100 pushed genuinely excellent local jobs down to ~70%, so almost
    # nothing reached "high priority" and the ranking lost its meaning.
    # Dimensions that carry no signal in the posting are therefore excluded
    # from the denominator: the score becomes "how well does this match on the
    # evidence available", which is what the user actually needs to compare.
    unknown = 0
    if dims["arabic"] == 0 and not contains_any(full, ["arabic", "multilingual", "bilingual"]):
        unknown += DIMENSION_MAX["arabic"]
    if dims["salary"] == 0 and not (result.salary and result.salary.has_value):
        unknown += DIMENSION_MAX["salary"]

    attainable = sum(DIMENSION_MAX.values()) - unknown
    if attainable > 0 and unknown:
        base = sum(dims.values())
        adjustments = total - base
        # Rescale the earned points onto the full 0-100 range, then re-apply
        # the bonuses/penalties so they keep their intended weight.
        total = (base / attainable) * 100 + adjustments
        result.normalised = True
        result.attainable = attainable

    result.confidence = _confidence(desc, job)
    result.dimensions = dims
    result.score = int(max(0, min(100, round(total))))
    return result

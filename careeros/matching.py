"""Matching engine v4 — three scores, career-track-aware weighting.

The engine answers "what gives this candidate the highest realistic
probability of being hired in Romania/the EU?", not merely "what matches
the CV?". Three separate scores are blended 40 / 35 / 25:

* **Match** — does the job suit his skills (weights depend on the track)
* **Eligibility** — can he legally and practically take it
* **Hiring** — would a recruiter realistically shortlist him

A weak fit cannot be propped up by the absence of legal barriers: when
match < 50 the eligibility+hiring contribution is capped.

Design rules carried over from v3
---------------------------------
* **Zero-default**: a dimension only earns points on positive evidence.
* **Confidence-aware**: short listings cannot be judged as harshly as full ads.
* **Explainable**: every score returns the evidence that produced it.
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
    ENGLISH_ABOVE_B2,
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
from .tracks import (
    BASE_DIMENSION_MAX,
    DEFAULT_TRACK,
    LOGISTICS_ALLOWED_TITLES,
    TRACK_AHMED_OFFICE,
    TRACK_LOGISTICS,
    dimension_max as track_dimension_max,
    resolve_track,
    romanian_pressure,
    skill_multiplier,
    track_weights,
)

__all__ = [
    "MatchResult",
    "DIMENSION_MAX",
    "BLEND_WEIGHTS",
    "calculate_match",
    "hard_filter_job",
    "classify_language_mention",
    "classify_romanian_requirement",
    "classify_remote_geography",
    "foreign_labour_market",
    "priority_band",
    "blend_scores",
]

DIMENSION_MAX = dict(BASE_DIMENSION_MAX)

MAX_ROMANIAN_BONUS = 5
MAX_ROMANIAN_PENALTY = -12

# Overall ranking = 40% match + 35% eligibility + 25% hiring reality.
BLEND_WEIGHTS = {"match": 0.40, "eligibility": 0.35, "hiring": 0.25}
WEAK_MATCH_THRESHOLD = 50
# When match < 50, eligibility+hiring may contribute at most this many
# overall points, so a 9% match with "no legal barriers" scores 32, not 52.
WEAK_MATCH_OTHER_CAP = 28


@dataclass
class MatchResult:
    score: int = 0
    match_score: int = 0
    eligibility_score: int = 0
    hiring_score: int = 0
    dimensions: Dict[str, int] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    eligibility_reasons: List[str] = field(default_factory=list)
    hiring_reasons: List[str] = field(default_factory=list)
    hiring_risks: List[str] = field(default_factory=list)
    confidence: str = "medium"
    romanian: str = "none"
    remote: str = "not_remote"
    salary: Optional[SalaryInfo] = None
    adjustments: List[Tuple[str, int]] = field(default_factory=list)
    blocking_languages: List[str] = field(default_factory=list)
    normalised: bool = False
    attainable: int = 100
    track: str = DEFAULT_TRACK
    romanian_pressure: float = 1.0
    verdict: str = "skip"
    verdict_label: str = "🔴 SKIP"
    apply_signals: List[str] = field(default_factory=list)
    apply_risks: List[str] = field(default_factory=list)
    reject_reason: str = ""

    def as_dict(self) -> Dict:
        return {
            "score": self.score,
            "match_score": self.match_score,
            "eligibility_score": self.eligibility_score,
            "hiring_score": self.hiring_score,
            "dimensions": self.dimensions,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "eligibility_reasons": self.eligibility_reasons,
            "hiring_reasons": self.hiring_reasons,
            "hiring_risks": self.hiring_risks,
            "confidence": self.confidence,
            "romanian": self.romanian,
            "remote": self.remote,
            "blocking_languages": self.blocking_languages,
            "track": self.track,
            "verdict": self.verdict,
            "verdict_label": self.verdict_label,
            "apply_signals": self.apply_signals,
            "apply_risks": self.apply_risks,
            "reject_reason": self.reject_reason,
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
# "fluent English & French" / "English and German required" — the second
# language is not next to "fluent", so phrase checks miss it.
_FLUENT_BUNDLE_RE = re.compile(
    r"(?:fluent(?:ly)?(?:\s+in)?|fluency\s+in|native(?:-|\s+)level|"
    r"must\s+speak|languages?)\s+"
    r"([a-z]+(?:\s*(?:and|&|/|,)\s*[a-z]+){1,8})",
    re.IGNORECASE,
)
_PAIR_WITH_ENGLISH_RE = re.compile(
    r"(?:english|arabic)\s*(?:and|&|/)\s*([a-z]+)"
    r"|"
    r"([a-z]+)\s*(?:and|&|/)\s*(?:english|arabic)",
    re.IGNORECASE,
)


def _language_in_required_bundle(text: str, lang: str) -> bool:
    """True when *lang* is listed as a fluency/required language with others."""
    lang = normalize_text(lang)
    for match in _FLUENT_BUNDLE_RE.finditer(text):
        parts = [
            p.strip()
            for p in re.split(r"\s*(?:and|&|/|,)\s*", normalize_text(match.group(1)))
            if p.strip()
        ]
        if lang in parts:
            return True
    for match in _PAIR_WITH_ENGLISH_RE.finditer(text):
        other = normalize_text(match.group(1) or match.group(2) or "")
        if other == lang:
            # Only treat as required when the pair is not clearly a plus.
            window = text[max(0, match.start() - 12): match.end() + 24]
            if contains_any(window, ["a plus", "an advantage", "nice to have", "bonus"]):
                return False
            return True
    return False


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
        f"with {lang}", f"speak {lang}", f"{lang}-speaking",
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

    # Plus beats a coordinated list: "English and French is a plus".
    if contains_any(text, plus):
        return "plus"
    if contains_any(text, required) or _language_in_required_bundle(text, lang):
        return "required"
    if contains_any(text, preferred):
        return "preferred"
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
    if contains_any(text, ["english only", "english-speaking workplace", "english speaking workplace"]):
        return "friendly"
    return "none"


_EU_REGION_TOKENS = {
    "europe", "europa", "european union", "eu", "eea", "emea", "cet",
}

# Region tokens that mean "you can work from Romania".
_OPEN_REGION_TOKENS = {
    "europe", "europa", "european union", "eu", "eea", "emea", "cet",
    "worldwide", "anywhere", "global", "world",
}

# Stripped from a location before deciding leftover text is a place name.
_LOCATION_NOISE = _OPEN_REGION_TOKENS | {
    "remote", "work from home", "wfh", "telemunca", "hybrid",
    "onsite", "on-site", "on site", "office", "based",
    "timezone", "time zone", "cest", "gmt", "utc",
}

# Pretty names for ISO-style title tags: "Customer service manager (GR)".
# Skip codes that collide with job abbreviations (IT, HR, QA, PR, PM, EN).
_TITLE_MARKET_CODES = {
    "gr": "Greece", "el": "Greece",
    "cy": "Cyprus",
    "uk": "UK", "gb": "UK",
    "pl": "Poland",
    "pt": "Portugal",
    "es": "Spain",
    "nl": "Netherlands",
    "be": "Belgium",
    "at": "Austria",
    "ie": "Ireland",
    "se": "Sweden",
    "dk": "Denmark",
    "fi": "Finland",
    "no": "Norway",
    "ch": "Switzerland",
    "hu": "Hungary",
    "bg": "Bulgaria",
    "sk": "Slovakia",
    "si": "Slovenia",
    "lt": "Lithuania",
    "lv": "Latvia",
    "ee": "Estonia",
    "cz": "Czechia",
    "ua": "Ukraine",
    "tr": "Turkey",
    "ae": "UAE",
    "de": "Germany",
    "fr": "France",
    "us": "USA",
    "ca": "Canada",
    "in": "India",
    "mt": "Malta",
    "lu": "Luxembourg",
}

_TITLE_MARKET_RE = re.compile(r"[\(\[]\s*([a-z]{2,3})\s*[\)\]]", re.IGNORECASE)

# Extra markets not already listed under LOCATION_SYNONYMS["Europe"].
_EXTRA_FOREIGN_MARKETS = {
    "uk": "UK",
    "united kingdom": "UK",
    "england": "UK",
    "britain": "UK",
    "great britain": "UK",
    "scotland": "UK",
    "wales": "UK",
    "united states": "USA",
    "usa": "USA",
    "canada": "Canada",
    "olanda": "Netherlands",
    "tara de jos": "Netherlands",
    "germania": "Germany",
    "ungaria": "Hungary",
    "italia": "Italy",
    "franta": "France",
    "franța": "France",
    "belgia": "Belgium",
    "spania": "Spain",
    "cehia": "Czechia",
    "polonia": "Poland",
    "austria": "Austria",
    "grecia": "Greece",
    "suedia": "Sweden",
    "danemarca": "Denmark",
    "irlanda": "Ireland",
    "portugalia": "Portugal",
    "anglia": "UK",
    "marea britanie": "UK",
    "india": "India",
    "uae": "UAE",
    "united arab emirates": "UAE",
    "dubai": "UAE",
    "turkey": "Turkey",
    "turkiye": "Turkey",
    "ukraine": "Ukraine",
    "cyprus": "Cyprus",
    "malta": "Malta",
    "luxembourg": "Luxembourg",
    "iceland": "Iceland",
    "london": "UK",
    "manchester": "UK",
    "birmingham": "UK",
    "warsaw": "Poland",
    "warszawa": "Poland",
    "krakow": "Poland",
    "athens": "Greece",
    "berlin": "Germany",
    "munich": "Germany",
    "hamburg": "Germany",
    "paris": "France",
    "madrid": "Spain",
    "barcelona": "Spain",
    "amsterdam": "Netherlands",
    "lisbon": "Portugal",
    "prague": "Czechia",
    "vienna": "Austria",
    "brussels": "Belgium",
    "dublin": "Ireland",
}

_PRETTY_MARKET = {
    "olanda": "Netherlands",
    "tara de jos": "Netherlands",
    "germania": "Germany",
    "ungaria": "Hungary",
    "italia": "Italy",
    "franta": "France",
    "franța": "France",
    "belgia": "Belgium",
    "spania": "Spain",
    "cehia": "Czechia",
    "polonia": "Poland",
    "grecia": "Greece",
    "suedia": "Sweden",
    "danemarca": "Denmark",
    "irlanda": "Ireland",
    "portugalia": "Portugal",
    "anglia": "UK",
    "marea britanie": "UK",

    "uk": "UK", "united kingdom": "UK", "england": "UK", "britain": "UK",
    "great britain": "UK", "scotland": "UK", "wales": "UK",
    "usa": "USA", "united states": "USA",
    "uae": "UAE", "united arab emirates": "UAE",
    "germany": "Germany", "deutschland": "Germany",
    "france": "France", "spain": "Spain", "italy": "Italy",
    "netherlands": "Netherlands", "poland": "Poland", "polska": "Poland",
    "czech": "Czechia", "czechia": "Czechia", "austria": "Austria",
    "belgium": "Belgium", "portugal": "Portugal", "ireland": "Ireland",
    "sweden": "Sweden", "denmark": "Denmark", "finland": "Finland",
    "norway": "Norway", "switzerland": "Switzerland", "hungary": "Hungary",
    "croatia": "Croatia", "greece": "Greece", "bulgaria": "Bulgaria",
    "slovakia": "Slovakia", "slovenia": "Slovenia", "lithuania": "Lithuania",
    "latvia": "Latvia", "estonia": "Estonia",
}


def _is_home_location(text: str) -> bool:
    return contains_any(text, LOCATION_SYNONYMS["Romania"] + LOCATION_SYNONYMS["Timișoara"])


def _is_open_region(text: str) -> bool:
    return contains_any(text, _OPEN_REGION_TOKENS)


def _countries_named_in(text: str) -> List[str]:
    """Return pretty country labels mentioned in already-normalised text."""
    found: List[str] = []
    seen = set()
    phrases = []
    for phrase in LOCATION_SYNONYMS["Europe"]:
        if phrase in _EU_REGION_TOKENS:
            continue
        if phrase in LOCATION_SYNONYMS["Romania"] or phrase == "romania":
            continue
        phrases.append((phrase, _PRETTY_MARKET.get(phrase, phrase.title())))
    phrases.extend(_EXTRA_FOREIGN_MARKETS.items())
    phrases.sort(key=lambda item: len(item[0]), reverse=True)
    for phrase, label in phrases:
        if label in seen:
            continue
        if contains_phrase(text, phrase):
            found.append(label)
            seen.add(label)
    return found


def _leftover_place(location_text: str) -> str:
    """What remains of a location after removing remote/worldwide filler."""
    text = normalize_text(location_text)
    for token in sorted(_LOCATION_NOISE, key=len, reverse=True):
        text = re.sub(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", " ", text)
    return re.sub(r"[\s,;:/|]+", " ", text).strip()


def _title_market(title: str) -> Optional[str]:
    for code in _TITLE_MARKET_RE.findall(normalize_text(title)):
        if code == "ro":
            return None
        label = _TITLE_MARKET_CODES.get(code)
        if label:
            return label
    return None


def foreign_labour_market(location_text: str, title: str = "", description: str = "") -> Optional[str]:
    """Return the actual foreign labour market; title country beats agency cities."""
    loc = normalize_text(location_text)
    title_n = normalize_text(title)
    desc_n = normalize_text(description)[:400]

    # A foreign destination in the title is authoritative even when a recruiter
    # board puts Timișoara/Arad/etc. in the location field. A clear Romania/home
    # statement in the title wins back to the Romanian market.
    title_markets = _countries_named_in(title_n)
    tagged = _title_market(title_n)
    if tagged and tagged not in title_markets:
        title_markets.append(tagged)
    if title_markets and not _is_home_location(title_n):
        return title_markets[0]

    named = _countries_named_in(loc)
    if named:
        return named[0] if not _is_home_location(title_n) else None

    if _is_home_location(loc):
        return None

    if desc_n and not _is_home_location(desc_n):
        desc_markets = _countries_named_in(desc_n)
        if desc_markets:
            return desc_markets[0]

    if not _is_open_region(loc):
        leftover = _leftover_place(location_text)
        if leftover and not _is_home_location(leftover):
            pretty = _PRETTY_MARKET.get(leftover, _EXTRA_FOREIGN_MARKETS.get(leftover))
            return pretty or leftover.title()
    return None


def classify_remote_geography(location_text: str, description_text: str) -> str:
    """Return: remote_country / remote_eu / remote_unclear / restricted / not_remote.

    "Remote — Europe/EU/EEA/worldwide" genuinely means he can work from
    Romania. "Remote — Greece" almost always means remote *from within
    Greece*, which is a different country's labour market — naming one
    foreign country is not EU-wide eligibility.
    """
    loc = normalize_text(location_text)
    desc = normalize_text(description_text)
    combined = f"{loc} {desc[:1500]}"

    is_remote = contains_any(loc, ["remote", "work from home", "wfh", "telemunca", "anywhere"]) \
        or contains_any(desc[:600], ["fully remote", "100% remote", "remote first", "work from home"])
    if not is_remote:
        return "not_remote"

    if contains_any(combined, REMOTE_RESTRICTED):
        return "restricted"

    mentions_romania = contains_any(combined, LOCATION_SYNONYMS["Romania"])
    if mentions_romania:
        return "remote_country"

    # A single foreign country named in the *location* (e.g. "Remote — Greece"
    # or "Remote — Europe, Netherlands") is that country's labour market, not
    # EU-wide eligibility. It must win over both generic "anywhere"/"global"/
    # "worldwide" wording in the ad body and over an accompanying open-region
    # token: "Remote — Europe, Netherlands" is a Dutch-market role, so the
    # country wins even though "Europe" is also present. This is checked before
    # REMOTE_FRIENDLY so a country never falls through to remote_eu.
    single_country = [
        country for country in LOCATION_SYNONYMS["Europe"]
        if country not in _EU_REGION_TOKENS and contains_phrase(loc, country)
    ]
    if not single_country:
        single_country = [country for country in _EXTRA_FOREIGN_MARKETS if contains_phrase(loc, country)]
    if single_country:
        return "remote_unclear"

    # "Remote — Europe/EU/EEA/worldwide" is real EU-wide eligibility.
    if contains_any(combined, REMOTE_FRIENDLY):
        return "remote_eu"

    if contains_any(loc, LOCATION_SYNONYMS["Europe"]):
        return "remote_eu"
    return "remote_unclear"


HIGH_PRIORITY_THRESHOLD = 80
STRONG_APPLY_THRESHOLD = 70
MEDIUM_PRIORITY_THRESHOLD = 60
LOW_PRIORITY_THRESHOLD = 50


def priority_band(score: int, confidence: str = "medium") -> Tuple[str, str]:
    """Map a score to an apply / maybe / skip verdict.

    80–100 APPLY immediately · 70–79 Strong application · 60–69 Consider
    · 50–59 Low priority · <50 Skip.
    """
    if score >= HIGH_PRIORITY_THRESHOLD:
        return "🟢 APPLY", "apply"
    if score >= STRONG_APPLY_THRESHOLD:
        return "🟢 STRONG", "strong"
    if score >= MEDIUM_PRIORITY_THRESHOLD:
        return "🟡 MAYBE", "maybe"
    if score >= LOW_PRIORITY_THRESHOLD:
        return "🟠 LOW", "low"
    return "🔴 SKIP", "skip"


_SPECIALIZED_SENIOR_TITLE = [
    "project manager", "programme manager", "program manager",
    "head of logistics", "head of fulfillment", "head of fulfilment",
    "logistics director", "fulfillment director",
]


def _is_specialized_senior_mismatch(title: str, full: str) -> bool:
    """Senior specialised PM / EU logistics leadership he should not apply to."""
    senior = contains_any(title, ["senior", "sr.", "head of", "director", "principal", "lead "])
    specialised = contains_any(
        title,
        ["project manager", "programme manager", "program manager",
         "fulfillment", "fulfilment", "supply chain manager"],
    )
    eu_exp = contains_any(full, [
        "european experience", "eu experience", "experience in europe",
        "years in logistics", "pmp ", "prince2", "agile project",
    ])
    if senior and specialised:
        return True
    if contains_any(title, _SPECIALIZED_SENIOR_TITLE) and (senior or eu_exp):
        return True
    return False


# ---------------------------------------------------------------------------
# Hard filter
# ---------------------------------------------------------------------------
def hard_filter_job(job: Dict, profile: Profile, track: str = "") -> Tuple[bool, str]:
    """Reject hopeless listings before scoring. Returns (keep, reason).

    Advanced Romanian and non-EU remote restrictions stay hard stops.
    Wrong-track titles are track-aware: a CNC operator is rejected on the
    finance track but kept on Logistics & Production.
    """
    full, title, loc, desc = _job_text(job)
    resolved = resolve_track(track)

    if not str(job.get("title", "")).strip():
        return False, "Missing title"

    # 1. Romanian far above the candidate's level (C1/C2/fluent/native).
    #    Graded "Romanian required" is *not* a hard stop — that lives in
    #    the eligibility score.
    if profile.romanian_rank < 4 and contains_any(full, ROMANIAN_REJECT):
        return False, "🔴 Requires advanced Romanian (C1/C2/fluent/native)"

    # 2. Geographically restricted or unreachable roles.
    #    He works from Timișoara. Remote is only useful when Romania / the
    #    EU / worldwide is eligible. "Remote — Greece/Poland/UK" is that
    #    country's labour market. On-site jobs outside Romania need relocation.
    if contains_any(loc, REMOTE_RESTRICTED):
        return False, "🔴 Geographically restricted (outside EU)"
    remote_class = classify_remote_geography(loc, desc)
    if remote_class == "restricted":
        return False, "🔴 Remote but restricted to a non-EU region"

    raw_location = _job_location(job)
    raw_title = str(job.get("title", "") or "")
    market = foreign_labour_market(raw_location, raw_title, desc)
    if market:
        home = profile.location or "Timișoara"
        if remote_class != "not_remote":
            return False, (
                f"🔴 Remote but only from {market} — not reachable from {home}"
            )
        if not profile.open_to_relocation:
            return False, (
                f"🔴 On-site in {market} — you are based in {home} "
                f"and not open to relocation"
            )

    # 3. Required language the candidate does not speak — rejection, not a -5.
    blocking = required_foreign_languages(full, profile)
    if blocking:
        names = ", ".join(lang.title() for lang in blocking[:3])
        return False, f"🔴 {names} required — language mismatch"

    # 3b. English above B2 (native / C1 / C2). Working "English required" is OK.
    if profile.english_rank < 5 and contains_any(full, ENGLISH_ABOVE_B2):
        return False, "🔴 English required above B2 (native/C1/C2)"

    # 4. Specialised senior PM / logistics leadership (not transferable).
    if _is_specialized_senior_mismatch(title, full):
        return False, (
            "🔴 Senior specialised project / logistics leadership — "
            "not a transferable-skills application"
        )

    # 5. US outbound sales / dialer — not Ahmed's market or work auth.
    if contains_any(title, ["dialer", "us sales", "usa sales", "sdr", "bdr", "cold call"]):
        return False, "🔴 US sales / dialer — not a reachable or relevant role"

    # 6. Clearly different career track (title only).
    negatives = list(NEGATIVE_TITLES)
    if resolved == TRACK_LOGISTICS:
        negatives = [t for t in negatives if t not in LOGISTICS_ALLOWED_TITLES]
    wrong_track = matched_phrases(title, negatives)
    if wrong_track:
        return False, f"🔴 Different career track ({wrong_track[0]})"

    return True, ""


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------
def _score_location(
    loc: str, desc: str, profile: Profile, result: MatchResult, market: Optional[str] = None
) -> int:
    home = normalize_text(profile.location)
    remote_class = classify_remote_geography(loc, desc)
    result.remote = remote_class
    if market:
        if profile.open_to_relocation and remote_class == "not_remote":
            result.reasons.append(f"🌍 {market} — relocation possible")
            return 8
        result.warnings.append(f"🚫 Foreign labour market: {market}")
        return 0

    if home and contains_phrase(loc, home):
        result.reasons.append(f"📍 {profile.location} — perfect location match")
        return 15
    if contains_any(loc, LOCATION_SYNONYMS["Timișoara"]):
        result.reasons.append("📍 Timișoara area — no relocation needed")
        return 15
    if contains_any(loc, LOCATION_SYNONYMS["Romania"]):
        result.reasons.append("🇷🇴 Romania — same country, work authorisation OK")
        return 12

    if remote_class == "remote_country":
        result.reasons.append("🏠 Remote — Romania explicitly eligible")
        return 14
    if remote_class in {"remote_eu", "excellent"}:
        result.reasons.append("🏠 Remote — EU/Europe/worldwide eligible")
        return 13
    if remote_class in {"remote_unclear", "good"}:
        result.reasons.append("🏠 Remote — but tied to another country, or eligibility not stated")
        result.warnings.append(
            "⚠️ Remote listing names a single foreign country (or none) — "
            "this is usually that country's labour market, not EU-wide"
        )
        return 4
    if remote_class == "restricted":
        result.warnings.append("⚠️ Remote role restricted to another region")
        return 1

    if contains_any(loc, LOCATION_SYNONYMS["Europe"]):
        if profile.open_to_relocation:
            result.reasons.append("🌍 Europe-based — relocation possible")
            return 8
        result.warnings.append("⚠️ Outside Romania — would require relocation")
        return 3

    if not loc.strip():
        result.warnings.append("⚠️ Location not stated in the listing")
        return 0
    result.warnings.append("⚠️ Location outside your target area")
    return 0


def _score_skills(full: str, title: str, result: MatchResult, track: str = "") -> int:
    total = 0.0
    labels: List[str] = []
    for key, group in SKILL_GROUPS.items():
        hits = matched_phrases(full, group["words"])
        if not hits:
            continue
        # Title hits are far stronger evidence than a passing mention.
        in_title = any(contains_phrase(title, hit) for hit in hits)
        weight = group["weight"] + (3 if in_title else 0)
        # Multiple distinct hits inside a group add a little extra confidence.
        weight += min(len(hits) - 1, 2)
        weight *= skill_multiplier(track, key)
        total += weight
        labels.append(group["label"])

    capped = int(round(min(total, BASE_DIMENSION_MAX["skills"])))
    skills_max = track_dimension_max(track, "skills")
    if labels:
        result.reasons.append(
            f"💼 Skills match: {', '.join(labels[:3])} ({capped}/{BASE_DIMENSION_MAX['skills']}"
            + (f", track cap {skills_max}" if skills_max != BASE_DIMENSION_MAX["skills"] else "")
            + ")"
        )
    else:
        result.warnings.append("⚠️ No familiar skill keywords found in this listing")
    return capped


def _score_arabic(full: str, result: MatchResult) -> int:
    level = classify_language_mention(full, "arabic")
    if level == "required":
        result.reasons.append("🗣️ Arabic required — your strongest differentiator")
        return 20
    if level == "preferred":
        result.reasons.append("🗣️ Arabic preferred — strong advantage")
        return 16
    if level == "plus":
        result.reasons.append("🗣️ Arabic is a plus")
        return 12
    if level == "mentioned":
        result.reasons.append("🗣️ Arabic mentioned in the listing")
        return 8
    if contains_any(full, ["multilingual", "bilingual", "mena", "middle east", "gulf"]):
        result.reasons.append("🌐 Multilingual/MENA context — Arabic is an asset")
        return 5
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
        if _is_specialized_senior_mismatch(title, full):
            score = 2
            result.warnings.append(
                "⚠️ Senior specialised title — transferable experience is not enough"
            )
        else:
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
        return 10
    if contains_any(full, ["multilingual", "bilingual", "international team", "global team"]):
        result.reasons.append("🌐 International/multilingual environment")
        return 6
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
# v4: eligibility, hiring reality, blend
# ---------------------------------------------------------------------------
def _clamp(value: float, lo: int = 0, hi: int = 100) -> int:
    return int(max(lo, min(hi, round(value))))


def blend_scores(match: int, eligibility: int, hiring: int) -> int:
    """40/35/25 blend with a weak-fit cap.

    When match < 50 the eligibility+hiring contribution cannot exceed
    ``WEAK_MATCH_OTHER_CAP`` overall points, so a 9% match with no legal
    barriers scores 32 rather than 52.
    """
    other = BLEND_WEIGHTS["eligibility"] * eligibility + BLEND_WEIGHTS["hiring"] * hiring
    if match < WEAK_MATCH_THRESHOLD:
        other = min(other, WEAK_MATCH_OTHER_CAP)
    return _clamp(BLEND_WEIGHTS["match"] * match + other)


def _score_eligibility(
    full: str,
    loc: str,
    desc: str,
    profile: Profile,
    result: MatchResult,
    blocking: List[str],
    pressure: float,
    market: Optional[str] = None,
) -> int:
    """Can he legally and practically take this job? Absence of barriers is
    *not* a large bonus — only positive evidence of access scores highly.
    """
    score = 16
    notes: List[str] = []

    if market and result.remote == "not_remote":
        # Title/description pin this on-site role to a specific foreign
        # labour market even though the location field reads Romanian —
        # must not be scored as if it were a local, work-authorised role.
        if profile.open_to_relocation:
            score += 8
            notes.append(f"🌍 {market} — relocation possible, but work authorisation is not yet in place")
        else:
            score -= 20
            notes.append(f"🚫 On-site in {market} — not reachable from {profile.location} without relocating")
    elif contains_phrase(loc, normalize_text(profile.location)) or contains_any(
        loc, LOCATION_SYNONYMS.get("Timișoara", [])
    ):
        score += 42
        notes.append("📍 On-site in your city — you can start without relocating")
    elif contains_any(loc, LOCATION_SYNONYMS.get("Romania", [])):
        score += 24
        notes.append("🇷🇴 Romania-based — work authorisation is already in place")
    elif result.remote == "remote_country":
        score += 32
        notes.append("🏠 Remote and explicitly open to Romania")
    elif result.remote in {"remote_eu", "excellent"}:
        score += 28
        notes.append("🏠 Remote and explicitly EU/Europe eligible")
    elif result.remote in {"remote_unclear", "good"}:
        score += 6
        notes.append("🏠 Remote, but likely another country's labour market")
        result.warnings.append(
            "⚠️ Remote listing names a single foreign country (or none) — "
            "confirm Romania is eligible before applying"
        )
    elif result.remote == "restricted":
        score -= 28
        notes.append("🚫 Remote role is restricted to another region")
    elif contains_any(loc, LOCATION_SYNONYMS.get("Europe", [])):
        if profile.open_to_relocation:
            score += 10
            notes.append("🌍 EU on-site — reachable if you relocate")
        else:
            score += 4
            notes.append("🌍 EU on-site but outside Romania")
    elif not loc.strip():
        score += 0
        notes.append("⚠️ Location not stated — eligibility is unverified")
    else:
        score += 0
        notes.append("⚠️ Location is outside your reachable area")

    # Already living and working in Romania is the practical work-auth signal.
    if profile.country and "romania" in normalize_text(profile.country):
        score += 10
        notes.append("🪪 You already live and work in Romania")

    if blocking:
        names = ", ".join(lang.title() for lang in blocking[:3])
        score -= 42
        notes.append(f"🚫 Requires fluent {names} — you cannot take this role")
    else:
        if len(desc) >= 80:
            score += 12
        if classify_language_mention(full, "english") == "required":
            score += 8
            notes.append("🇬🇧 Working language is English — you meet it")

    romanian = result.romanian
    if romanian == "friendly":
        # Spec: "Romanian is a plus" costs nothing — and the explicit
        # compatibility is a small positive signal of access.
        score += 8
        notes.append("🟢 Romanian optional/a plus — no eligibility cost")
    elif romanian == "none":
        pass
    elif romanian == "risky":
        gap = max(0, 4 - profile.romanian_rank)
        penalty = int(round(14 * (gap / 4) * pressure)) if gap else int(round(4 * pressure))
        score -= penalty
        notes.append(
            f"🟠 Unspecified Romanian requirement (pressure {pressure:.2f}) −{penalty}"
        )
        result.warnings.append("🟠 Romanian may be required — verify before applying")
    elif romanian == "reject":
        penalty = int(round(36 * pressure))
        score -= penalty
        notes.append(f"🔴 Advanced Romanian required −{penalty}")

    result.eligibility_reasons = notes
    return _clamp(score)


def _title_track_alignment(title: str, track: str) -> int:
    """How obviously the title belongs on the selected track. −10 … +18."""
    finance = ["finance", "financial", "account", "tax", "compliance", "audit", "aml", "kyc"]
    support = ["support", "service", "customer", "client", "help desk", "call center", "bpo"]
    ops = ["operations", "coordinator", "back office", "administrator", "specialist"]
    legal = ["legal", "contract", "paralegal", "regulatory"]
    arabic = ["arabic"]
    logistics = [
        "logistics", "warehouse", "supply", "freight", "production", "operator",
        "quality", "planner", "inventory", "shipping",
    ]
    tables = {
        "💰 Finance & Compliance": finance,
        "📞 Customer Support & BPO": support,
        "⚙️ Operations & Back Office": ops,
        "🗣️ Arabic-Speaking Roles": arabic + support,
        "🏭 Logistics & Production": logistics,
        # English-first office identity: tax/compliance/legal/admin/ops/support,
        # deliberately excluding the logistics/production word list.
        TRACK_AHMED_OFFICE: finance + support + ops + legal,
    }
    words = tables.get(track)
    if not words:
        # Full scan / custom: any of the above is a mild positive.
        if contains_any(title, finance + support + ops + logistics):
            return 8
        return 0
    if contains_any(title, words):
        return 16
    # Wrong-family title on a focused track.
    others = finance + support + logistics
    if track.startswith("💰") and contains_any(title, ["production", "operator", "warehouse"]):
        return -10
    if track.startswith("🏭") and contains_any(title, finance) and not contains_any(title, logistics):
        return -6
    if contains_any(title, others) and not contains_any(title, words):
        return -4
    return 2


def _score_hiring(
    job: Dict,
    profile: Profile,
    full: str,
    title: str,
    loc: str,
    result: MatchResult,
    blocking: List[str],
    pressure: float,
    track: str,
    match_dims: Dict[str, int],
    match_score: int = 0,
    market: Optional[str] = None,
) -> int:
    """Would a recruiter realistically shortlist him for this posting?"""
    score = 26
    reasons: List[str] = []
    risks: List[str] = []

    align = _title_track_alignment(title, track)
    score += align
    if align >= 12:
        reasons.append("🎯 Title is a clean fit for the selected career track")
    elif align <= -6:
        risks.append("📉 Title does not look like the track a recruiter would search")

    arabic = classify_language_mention(full, "arabic")
    if arabic == "required":
        score += 18
        reasons.append("🗣️ Arabic is required — a native speaker is shortlisted immediately")
    elif arabic in {"preferred", "plus"}:
        score += 8
        reasons.append("🗣️ Arabic is an advertised plus — you stand out")
    elif arabic == "mentioned":
        score += 4

    if market and result.remote == "not_remote":
        # A recruiter in the actual foreign market cannot treat him as a
        # local, no-relocation-risk candidate just because the board's
        # location field reads Romanian.
        risks.append(f"📉 Role is tied to the {market} labour market — relocation risk for the employer")
    elif contains_phrase(loc, normalize_text(profile.location)) or contains_any(
        loc, LOCATION_SYNONYMS.get("Timișoara", [])
    ):
        score += 10
        reasons.append("📍 Local candidate — no relocation risk for the employer")
    elif contains_any(loc, LOCATION_SYNONYMS.get("Romania", [])):
        score += 5

    required = _extract_required_years(full)
    if required is not None:
        if required <= profile.experience_years:
            score += 6
            reasons.append(f"✅ Asks for {required}+ years — you have {profile.experience_years}")
        else:
            score -= 8
            risks.append(f"⚠️ Asks for {required}+ years of experience")

    if contains_any(title, SENIORITY_PATTERNS["junior"]):
        score -= 8
        risks.append("⚠️ Junior/intern title — a recruiter will see you as overqualified")
    elif contains_any(title, SENIORITY_PATTERNS["leadership"]) and profile.experience_years >= 8:
        score += 5
        reasons.append("🧑‍💼 Leadership title matches your seniority")

    if blocking:
        score -= 24
        risks.append("🚫 A required language you do not speak ends the screening")

    if result.romanian == "reject":
        score -= 16
        risks.append("🔴 Advanced Romanian will stop the recruiter at the first filter")
    elif result.romanian == "risky":
        hit = int(round(8 * pressure))
        score -= hit
        risks.append("🟠 Romanian is likely required — many RO recruiters will filter you out")

    age = job.get("age_days")
    if isinstance(age, (int, float)):
        if age <= 3:
            score += 4
            reasons.append("🆕 Fresh posting — recruiters are still building a longlist")
        elif age > 45:
            score -= 6
            risks.append("⚠️ Listing is over 45 days old — the role may already be filled")

    skills_max = max(1, track_dimension_max(track, "skills"))
    skills_frac = match_dims.get("skills", 0) / skills_max
    if skills_frac >= 0.6:
        score += 8
    elif match_dims.get("skills", 0) == 0:
        score -= 14
        risks.append("📉 No overlapping skills a recruiter can tick off")

    # EU-regulated finance/compliance often wants local (not Egyptian tax) exp.
    if track.startswith("💰") and contains_any(title, ["compliance", "tax", "aml", "kyc"]):
        score -= 6
        risks.append("⚖️ EU-regulated finance roles often prefer local tax/compliance experience")

    if match_score >= 80:
        score += 10
        reasons.append("📌 Strong skill match — the recruiter can tick the boxes")

    result.hiring_reasons = reasons
    result.hiring_risks = risks
    return _clamp(score)


def _scale_dimensions(raw: Dict[str, int], track: str) -> Dict[str, int]:
    """Rescale v3-scale evidence onto the track's 100-point table."""
    weights = track_weights(track)
    scaled: Dict[str, int] = {}
    for dim, value in raw.items():
        old_max = BASE_DIMENSION_MAX.get(dim, 10)
        new_max = weights.get(dim, old_max)
        if old_max <= 0 or new_max <= 0:
            scaled[dim] = 0
        else:
            scaled[dim] = int(round(min(new_max, (value / old_max) * new_max)))
    return scaled


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def calculate_match(job: Dict, profile: Profile, track: str = "") -> MatchResult:
    """Score a job against the profile and explain the three v4 scores."""
    resolved = resolve_track(track)
    full, title, loc, desc = _job_text(job)
    result = MatchResult(track=resolved)

    # Computed once so location, eligibility and hiring-reality scoring all
    # agree on whether this posting is actually tied to a foreign market —
    # the hard filter already does this with the raw (unnormalised) title.
    market = foreign_labour_market(loc, title, desc)

    raw = {
        "location": _score_location(loc, desc, profile, result, market),
        "skills": _score_skills(full, title, result, resolved),
        "arabic": _score_arabic(full, result),
        "english": _score_english(full, result),
        "experience": _score_experience(full, title, profile, result),
        "salary": _score_salary(job, profile, result),
        "education": _score_education(full, title, profile, result),
        "relevance": _score_relevance(full, result),
    }

    romanian = classify_romanian_requirement(full)
    result.romanian = romanian
    if romanian == "friendly":
        result.reasons.append("🟢 Romanian optional/beginner — compatible with your level")
        result.adjustments.append(("Romanian beginner-friendly", 0))

    blocking_languages = required_foreign_languages(full, profile)
    if blocking_languages:
        names = ", ".join(lang.title() for lang in blocking_languages[:3])
        result.warnings.insert(0, f"🔴 Requires fluent {names} — not in your profile")
        result.blocking_languages = blocking_languages
        result.adjustments.append((f"Requires {names}", 0))

    pressure = romanian_pressure(resolved, loc, result.remote)
    result.romanian_pressure = pressure

    weights = track_weights(resolved)
    dims = _scale_dimensions(raw, resolved)

    # Normalise the Match score against evidence that was actually present.
    # Arabic and salary are absent from most ads; leaving them in the
    # denominator flattened every strong local job to ~70%.
    unknown = 0
    if raw["arabic"] == 0 and not contains_any(full, ["arabic", "multilingual", "bilingual"]):
        unknown += weights.get("arabic", 0)
    if raw["salary"] == 0 and not (result.salary and result.salary.has_value):
        unknown += weights.get("salary", 0)

    attainable = sum(weights.values()) - unknown
    match_points = sum(dims.values())
    if attainable > 0 and unknown:
        match_total = (match_points / attainable) * 100
        result.normalised = True
        result.attainable = attainable
    else:
        match_total = match_points
        result.attainable = sum(weights.values()) or 100

    match_score = _clamp(match_total)
    eligibility_score = _score_eligibility(
        full, loc, desc, profile, result, blocking_languages, pressure, market,
    )
    hiring_score = _score_hiring(
        job, profile, full, title, loc, result,
        blocking_languages, pressure, resolved, dims, match_score, market,
    )

    result.dimensions = dims
    result.match_score = match_score
    result.eligibility_score = eligibility_score
    result.hiring_score = hiring_score
    result.score = blend_scores(match_score, eligibility_score, hiring_score)
    result.confidence = _confidence(desc, job)

    if blocking_languages:
        names = ", ".join(lang.title() for lang in blocking_languages[:3])
        result.reject_reason = f"{names} required — language mismatch"
        result.score = min(result.score, 35)
        result.verdict_label, result.verdict = "🔴 SKIP", "skip"
    elif _is_specialized_senior_mismatch(title, full):
        result.reject_reason = "Senior specialised experience required"
        result.score = min(result.score, 45)
        result.verdict_label, result.verdict = priority_band(result.score)
    else:
        result.verdict_label, result.verdict = priority_band(result.score)

    result.apply_signals = list(result.reasons[:8])
    result.apply_risks = list(dict.fromkeys(result.warnings + result.hiring_risks))[:6]
    return result

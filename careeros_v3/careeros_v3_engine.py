from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# CareerOS V3 — source-independent intelligence layer
# ---------------------------------------------------------------------------
# Design goals:
#   1. Keep source collection separate from ranking.
#   2. Normalize every source into one canonical schema.
#   3. Merge duplicates before scoring.
#   4. Reject only explicit hard incompatibilities.
#   5. Prevent generic words ("support", "operations", "English") from
#      overpowering a wrong-career-family match.
#   6. Reward direct transferable evidence from Ahmed's actual background.
# ---------------------------------------------------------------------------

PROFILE = {
    "name": "Ahmed",
    "location": "Timisoara",
    "country": "Romania",
    "romanian_level": "beginner",
    "english_level": "B2",
    "experience_years": 10,
    "education": "Master's Degree in Law",
    "languages": {"arabic", "english", "romanian"},
    "skills": {
        "operations", "client management", "financial compliance", "customer service",
        "customer support", "excel", "sap", "erp", "sql", "administration",
        "logistics", "arabic", "english", "tax", "banking", "accounting",
        "audit", "legal", "regulatory", "documentation", "case management",
        "stakeholder management", "reporting", "data entry", "process improvement",
    },
    "target_salary_min": 5000,
    "target_salary_max": 7000,
    "open_to_remote": True,
    "open_to_relocation": False,
}

CAREER_FAMILIES = {
    "Finance & Compliance": {
        "strong": ["finance", "financial", "accounting", "accountant", "accounts payable", "accounts receivable", "tax", "taxation", "compliance", "audit", "regulatory", "banking", "treasury", "collections", "payroll", "invoice", "billing", "risk", "enhanced due diligence", "due diligence", "customer due diligence", "kyc", "aml", "financial crime", "edd analyst"],
        "support": ["excel", "sap", "erp", "reporting", "reconciliation", "controls", "documentation", "legal"],
        "exclude": ["software engineer", "frontend", "backend", "devops", "data scientist", "machine learning", "network engineer", "service desk", "sales engineer", "graphic designer", "digital marketing", "cro manager"],
    },
    "Operations & Back Office": {
        "strong": ["operations", "operational", "back office", "operations specialist", "operations coordinator", "administrator", "administration", "business operations", "shared services", "process", "case management", "order management", "transaction processing", "quality operations"],
        "support": ["excel", "erp", "sap", "reporting", "documentation", "customer support", "client management", "stakeholder", "workflow", "process improvement"],
        "exclude": ["software engineer", "frontend", "backend", "devops", "network engineer", "service desk engineer", "data scientist", "machine learning", "surgeon", "nurse"],
    },
    "Customer Support & BPO": {
        "strong": ["customer support", "customer service", "customer care", "client support", "client service", "contact center", "call center", "bpo", "helpdesk", "technical support", "customer experience", "customer operations"],
        "support": ["arabic", "english", "crm", "ticketing", "case management", "client management", "problem solving", "order management"],
        "exclude": ["software engineer", "frontend", "backend", "data scientist", "research scientist", "sales director", "cro manager"],
    },
    "Arabic-Speaking Roles": {
        "strong": ["arabic", "arabic speaker", "arabic speaking", "mena", "middle east", "gcc", "mena region"],
        "support": ["customer support", "customer service", "operations", "back office", "finance", "compliance", "sales support", "account management"],
        "exclude": ["software engineer", "network engineer", "medical doctor"],
    },
    "Logistics & Supply Chain": {
        "strong": ["logistics", "supply chain", "warehouse", "inventory", "transport", "fulfillment", "procurement", "purchasing", "distribution", "dispatch", "order fulfillment", "warehouse coordinator"],
        "support": ["operations", "erp", "sap", "excel", "inventory control", "stock", "planning"],
        "exclude": ["software engineer", "frontend", "backend", "data scientist"],
    },
    "General Administration": {
        "strong": ["administrative", "administration", "office administrator", "office coordinator", "document control", "data entry", "records", "legal assistant", "administrative assistant", "coordinator"],
        "support": ["excel", "documentation", "reporting", "customer service", "operations", "legal"],
        "exclude": ["software engineer", "frontend", "backend", "network engineer", "data scientist"],
    },
    "Production & Quality": {
        "strong": ["production operator", "production", "manufacturing", "quality control", "quality specialist", "quality assurance", "warehouse", "operator", "assembly", "plant", "factory"],
        "support": ["quality", "safety", "inventory", "process", "documentation", "shift"],
        "exclude": ["software engineer", "frontend", "backend", "cro manager"],
    },
}

# Roles that should never get a high career-fit score from generic transferable
# words alone. This is the main protection against the old false positives.
TECHNICAL_FAMILIES = [
    "software engineer", "frontend", "backend", "full stack", "devops",
    "network engineer", "service desk engineer", "site reliability",
    "data scientist", "machine learning", "cloud engineer", "cybersecurity",
]

COUNTRY_LOCKS = {
    "united states": "United States", "usa": "United States", "canada": "Canada",
    "united kingdom": "United Kingdom", "uk": "United Kingdom", "india": "India",
    "germany": "Germany", "france": "France", "spain": "Spain", "italy": "Italy",
    "poland": "Poland", "greece": "Greece", "hungary": "Hungary", "ireland": "Ireland",
    "netherlands": "Netherlands", "australia": "Australia", "switzerland": "Switzerland",
    "austria": "Austria", "belgium": "Belgium", "sweden": "Sweden", "norway": "Norway",
    "denmark": "Denmark", "finland": "Finland", "czech republic": "Czech Republic",
    "slovakia": "Slovakia", "bulgaria": "Bulgaria", "serbia": "Serbia", "croatia": "Croatia",
}

LANGUAGE_PATTERNS = {
    "german": [r"\bgerman\s+(?:is\s+)?(?:required|mandatory|essential)\b", r"\brequired\s+(?:fluent\s+)?german\b", r"\bfluent\s+german\b", r"\bnative\s+german\b", r"\bgerman\s*(?:b2|c1|c2)\b"],
    "french": [r"\bfrench\s+(?:is\s+)?(?:required|mandatory|essential)\b", r"\brequired\s+(?:fluent\s+)?french\b", r"\bfluent\s+french\b", r"\bnative\s+french\b", r"\bfrench\s*(?:b2|c1|c2)\b"],
    "dutch": [r"\bdutch\s+(?:is\s+)?(?:required|mandatory|essential)\b", r"\brequired\s+(?:fluent\s+)?dutch\b", r"\bfluent\s+dutch\b", r"\bnative\s+dutch\b", r"\bdutch\s*(?:b2|c1|c2)\b"],
    "spanish": [r"\bspanish\s+(?:is\s+)?(?:required|mandatory|essential)\b", r"\brequired\s+(?:fluent\s+)?spanish\b", r"\bfluent\s+spanish\b", r"\bnative\s+spanish\b", r"\bspanish\s*(?:b2|c1|c2)\b"],
    "italian": [r"\bitalian\s+(?:is\s+)?(?:required|mandatory|essential)\b", r"\brequired\s+(?:fluent\s+)?italian\b", r"\bfluent\s+italian\b", r"\bnative\s+italian\b", r"\bitalian\s*(?:b2|c1|c2)\b"],
    "hungarian": [r"\bhungarian\s+(?:is\s+)?(?:required|mandatory|essential)\b", r"\brequired\s+(?:fluent\s+)?hungarian\b", r"\bfluent\s+hungarian\b", r"\bnative\s+hungarian\b", r"\bhungarian\s*(?:b2|c1|c2)\b"],
}

@dataclass
class Job:
    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    url: str = ""
    source: str = ""
    salary_text: str = ""
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    age_days: Optional[int] = None
    work_mode: str = ""
    category: str = ""
    duplicate_count: int = 1
    sources: List[str] = field(default_factory=list)
    career_family: str = ""
    family_fit: int = 0
    score: int = 0
    confidence: str = "low"
    hard_reject_reasons: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    dimensions: Dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


def normalize_text(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()


def canonical_url(url: str) -> str:
    if not url:
        return ""
    try:
        p = urlsplit(url.strip())
        if p.scheme not in {"http", "https"} or not p.netloc:
            return url.strip().lower()
        qs = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
              if not k.lower().startswith(("utm_", "ref", "trk", "source"))]
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), urlencode(sorted(qs)), ""))
    except Exception:
        return url.strip().lower()


def source_key(job: Dict[str, Any]) -> str:
    url = canonical_url(str(job.get("redirect_url") or job.get("url") or ""))
    if url:
        return "url:" + url
    title = normalize_text(job.get("title"))
    company = normalize_text(job.get("company"))
    return f"tc:{title}|{company}"


def normalize_job(raw: Dict[str, Any], source: Optional[str] = None) -> Job:
    company = raw.get("company", "")
    if isinstance(company, dict):
        company = company.get("display_name") or company.get("name") or ""
    loc = raw.get("location", "")
    if isinstance(loc, dict):
        loc = loc.get("display_name") or loc.get("name") or ""
    title = clean_text(raw.get("title") or raw.get("name") or "")
    description = clean_text(raw.get("description") or raw.get("snippet") or raw.get("content") or "")
    url = str(raw.get("redirect_url") or raw.get("link") or raw.get("url") or "").strip()
    source_name = source or str(raw.get("source") or "Unknown")
    salary_min = raw.get("salary_min")
    salary_max = raw.get("salary_max")
    try: salary_min = float(salary_min) if salary_min is not None else None
    except (TypeError, ValueError): salary_min = None
    try: salary_max = float(salary_max) if salary_max is not None else None
    except (TypeError, ValueError): salary_max = None
    j = Job(title=title, company=clean_text(company) or "Company not listed",
            location=clean_text(loc), description=description, url=url,
            source=source_name, salary_text=clean_text(raw.get("salary_text") or raw.get("salary") or ""),
            salary_min=salary_min, salary_max=salary_max,
            age_days=raw.get("age_days"), work_mode=clean_text(raw.get("work_mode") or ""),
            category=clean_text(raw.get("category") if not isinstance(raw.get("category"), dict) else raw.get("category", {}).get("label", "")))
    return j


def _title_company_similarity(a: Job, b: Job) -> float:
    at = normalize_text(a.title)
    bt = normalize_text(b.title)
    ac = normalize_text(a.company)
    bc = normalize_text(b.company)
    return 0.65 * SequenceMatcher(None, at, bt).ratio() + 0.35 * SequenceMatcher(None, ac, bc).ratio()


def deduplicate_jobs(raw_jobs: Sequence[Dict[str, Any] | Job]) -> Tuple[List[Job], int]:
    canonical: Dict[str, Job] = {}
    merged = 0
    fuzzy_buckets: Dict[Tuple[str, str], List[Job]] = {}

    for raw in raw_jobs:
        job = raw if isinstance(raw, Job) else normalize_job(raw)
        key = canonical_url(job.url)
        if key:
            lookup = "url:" + key
            if lookup in canonical:
                base = canonical[lookup]
                _merge_job(base, job)
                merged += 1
            else:
                canonical[lookup] = job
                fuzzy_buckets.setdefault((normalize_text(job.company), normalize_text(job.title)[:12]), []).append(job)
            continue

        bucket = (normalize_text(job.company), normalize_text(job.title)[:12])
        match = next((existing for existing in fuzzy_buckets.get(bucket, []) if _title_company_similarity(existing, job) >= 0.90), None)
        if match:
            _merge_job(match, job)
            merged += 1
        else:
            fuzzy_buckets.setdefault(bucket, []).append(job)
            canonical[f"anon:{len(canonical)}"] = job

    jobs = list(canonical.values())
    for j in jobs:
        j.sources = sorted(set(j.sources or [j.source]))
        j.duplicate_count = max(1, len(j.sources))
    return jobs, merged


def _merge_job(base: Job, incoming: Job) -> None:
    if len(incoming.description) > len(base.description):
        base.description = incoming.description
    if not base.location and incoming.location:
        base.location = incoming.location
    if not base.salary_text and incoming.salary_text:
        base.salary_text = incoming.salary_text
    if base.salary_min is None:
        base.salary_min = incoming.salary_min
    if base.salary_max is None:
        base.salary_max = incoming.salary_max
    base.sources = sorted(set((base.sources or [base.source]) + [incoming.source] + incoming.sources))
    if base.age_days is None or (incoming.age_days is not None and incoming.age_days < base.age_days):
        base.age_days = incoming.age_days


def job_text(job: Job) -> str:
    return normalize_text(" ".join([job.title, job.description, job.company, job.location, job.category]))


def detect_blocking_languages(text: str) -> List[str]:
    found = []
    for language, patterns in LANGUAGE_PATTERNS.items():
        if any(re.search(p, text, flags=re.I) for p in patterns):
            found.append(language)
    return found


def detect_romanian_hard_requirement(text: str) -> bool:
    patterns = [
        r"\bromanian\s+(?:is\s+)?(?:required|mandatory|essential)\b",
        r"\brequired\s+(?:fluent\s+)?romanian\b",
        r"\bfluent\s+romanian\b", r"\bnative\s+romanian\b",
        r"\bromanian\s*(?:b2|c1|c2)\b",
        r"\blimba romana\s+(?:obligatorie|obligatoriu|avansat[a]?)\b",
    ]
    return any(re.search(p, text, flags=re.I) for p in patterns)


def detect_location_hard_reject(job: Job, profile: Dict[str, Any]) -> Optional[str]:
    loc = normalize_text(job.location)
    text = job_text(job)
    if "remote" in loc or "remote" in text:
        # Explicit worldwide / Europe / Romania eligibility wins unless a more
        # specific country-only restriction is also present.
        if any(x in text for x in ["worldwide", "work from anywhere", "anywhere", "europe", "european union", "romania", "timisoara"]):
            m = re.search(r"\b(?:remote|work from home).{0,50}\b([a-z ]+)\s+only\b", loc)
            if not m:
                return None
        for needle, pretty in COUNTRY_LOCKS.items():
            if re.search(rf"\b{re.escape(needle)}\b", loc) and needle not in {"romania"}:
                return f"Remote role is restricted to {pretty}, not Romania."
        return None
    # On-site / hybrid abroad is not actionable without relocation.
    if not profile.get("open_to_relocation", False):
        for needle, pretty in COUNTRY_LOCKS.items():
            if re.search(rf"\b{re.escape(needle)}\b", loc):
                return f"On-site/hybrid location is outside Romania ({pretty})."
    return None


def detect_experience_hard_reject(text: str, profile: Dict[str, Any]) -> Optional[int]:
    patterns = [
        r"\b(?:minimum|min\.?|at least)\s*(\d+)\+?\s*(?:years?|yrs?)\b",
        r"\b(\d+)\+?\s*(?:years?|yrs?)\s+of\s+(?:relevant\s+)?experience\b",
    ]
    for p in patterns:
        for m in re.finditer(p, text, flags=re.I):
            required = int(m.group(1))
            if required > int(profile.get("experience_years", 0)):
                return required
    return None


def hard_eligibility(job: Job, profile: Dict[str, Any] = PROFILE) -> Tuple[bool, List[str]]:
    text = job_text(job)
    reasons = []
    blocked = detect_blocking_languages(text)
    if blocked:
        reasons.append("Required language not in profile: " + ", ".join(x.title() for x in blocked) + ".")
    if detect_romanian_hard_requirement(text):
        reasons.append("Romanian is explicitly required above Beginner level.")
    location_reason = detect_location_hard_reject(job, profile)
    if location_reason:
        reasons.append(location_reason)
    req = detect_experience_hard_reject(text, profile)
    if req:
        reasons.append(f"Listing explicitly requires {req}+ years of experience; profile has {profile['experience_years']}.")
    return not reasons, reasons


def infer_family(job: Job) -> Tuple[str, int, List[str], List[str]]:
    text = job_text(job)
    title = normalize_text(job.title)
    candidates = []
    for family, cfg in CAREER_FAMILIES.items():
        strong_hits = [x for x in cfg["strong"] if x in title or x in text]
        support_hits = [x for x in cfg["support"] if x in text]
        excludes = [x for x in cfg["exclude"] if x in title]
        score = min(100, len(strong_hits) * 18 + len(support_hits) * 5)
        if strong_hits and any(x in title for x in cfg["strong"]):
            score += 12
        if excludes:
            score -= 50
        candidates.append((score, family, strong_hits, support_hits, excludes))
    candidates.sort(reverse=True)
    best = candidates[0]
    # A title-only technical role is a hard family mismatch for this profile.
    technical = [x for x in TECHNICAL_FAMILIES if x in title]
    if technical:
        return "Technical / Engineering", 0, [], ["Role is primarily technical/engineering and does not align with the target career families."]
    if best[0] <= 0:
        return "Other", 0, [], ["No strong career-family evidence found."]
    reasons = [f"Career family: {best[1]}"]
    if best[2]:
        reasons.append("Direct role signals: " + ", ".join(best[2][:4]))
    return best[1], min(100, best[0]), reasons, []


def parse_salary(job: Job) -> Optional[float]:
    if job.salary_min is not None or job.salary_max is not None:
        vals = [x for x in [job.salary_min, job.salary_max] if x is not None]
        return sum(vals) / len(vals) if vals else None
    text = normalize_text(job.salary_text)
    if not text:
        return None
    nums = []
    for raw in re.findall(r"\d[\d., ]*", text):
        s = raw.replace(" ", "")
        # Romanian 5.000 / 7,000 and decimal variants.
        if s.count(".") == 1 and s.count(",") == 0 and len(s.split(".")[-1]) == 3:
            s = s.replace(".", "")
        elif s.count(",") == 1 and len(s.split(",")[-1]) == 3:
            s = s.replace(",", "")
        else:
            s = s.replace(",", ".")
        try:
            nums.append(float(s))
        except ValueError:
            pass
    if not nums:
        return None
    # Only treat RON/lei salaries as directly comparable. EUR is converted with
    # a conservative fixed approximation for ranking; this is intentionally not
    # a financial quote.
    if any(x in text for x in ["eur", "€"]):
        return sum(nums) / len(nums) * 5.0
    if any(x in text for x in ["usd", "$", "dollar"]):
        return sum(nums) / len(nums) * 4.5
    return sum(nums) / len(nums)


def _dim_location(job: Job) -> int:
    loc = normalize_text(job.location)
    if "timisoara" in loc or "timis" in loc:
        return 20
    if "romania" in loc or "bucuresti" in loc or "bucharest" in loc:
        return 15
    if "remote" in loc:
        if any(x in loc for x in ["worldwide", "europe", "romania", "anywhere"]):
            return 15
        return 7
    return 0


def _dim_skills(job: Job, family: str) -> Tuple[int, List[str]]:
    text = job_text(job)
    direct = []
    for skill in PROFILE["skills"]:
        if skill in text:
            direct.append(skill)
    family_cfg = CAREER_FAMILIES.get(family, {})
    family_hits = [x for x in family_cfg.get("strong", []) if x in text]
    score = min(25, len(set(direct)) * 2 + len(set(family_hits)) * 3)
    # Direct, role-specific evidence gets more weight than generic tools.
    if any(x in text for x in ["tax", "compliance", "accounting", "audit", "operations", "customer support", "logistics"]):
        score += 4
    return min(25, score), direct[:6]


def _dim_language(job: Job) -> Tuple[int, int, List[str]]:
    text = job_text(job)
    arabic = 0
    english = 0
    reasons = []
    if re.search(r"\barabic\b|\barabe\b|\barabic speaker|mena|middle east|gcc", text):
        arabic = 15
        reasons.append("Arabic is directly relevant")
    elif "arabic" in text:
        arabic = 8
        reasons.append("Arabic is mentioned")
    if re.search(r"\benglish\b|\benglish speaking\b|\bengleza\b", text):
        english = 10
        reasons.append("English is relevant")
    return arabic, english, reasons


def _dim_experience(job: Job) -> Tuple[int, str]:
    title = normalize_text(job.title)
    text = job_text(job)
    required = None
    m = re.search(r"\b(?:minimum|min\.?|at least)\s*(\d+)\+?\s*(?:years?|yrs?)\b", text)
    if m:
        required = int(m.group(1))
    seniority = 0
    if any(x in title for x in ["senior", "lead", "manager", "specialist"]):
        seniority = 1
    years = PROFILE["experience_years"]
    if required is not None:
        if required <= years:
            return 10, "Experience requirement is within profile range"
        return 0, "Experience requirement exceeds profile"
    if seniority and years >= 5:
        return 9, "Seniority is plausible for 10+ years"
    return 7, "Experience level is not explicitly incompatible"


def _dim_salary(job: Job) -> Tuple[int, Optional[float], str]:
    salary = parse_salary(job)
    if salary is None:
        return 0, None, "Salary not published"
    target = PROFILE["target_salary_min"]
    if salary >= target:
        return 10, salary, f"Published salary is around/above {target:,} RON target"
    if salary >= target * 0.8:
        return 6, salary, "Published salary is below target but reasonably close"
    return 2, salary, "Published salary is materially below target"


def _dim_education(job: Job) -> Tuple[int, str]:
    text = job_text(job)
    if any(x in text for x in ["law", "legal", "compliance", "regulatory", "master", "degree"]):
        return 5, "Law/degree background is relevant"
    return 0, "No direct education signal"


def _dim_relevance(job: Job, family: str) -> Tuple[int, str]:
    text = job_text(job)
    hits = sum(1 for x in ["bpo", "shared services", "mena", "operations", "compliance", "back office", "customer support"] if x in text)
    if family == "Technical / Engineering":
        return 0, "Technical role"
    return min(5, hits), "Relevant shared-services/operations context" if hits else "Limited contextual evidence"


def score_job(job: Job, profile: Dict[str, Any] = PROFILE) -> Job:
    family, family_fit, family_reasons, family_warnings = infer_family(job)
    job.career_family = family
    job.family_fit = family_fit
    job.reasons = list(family_reasons)
    job.warnings = list(family_warnings)

    loc = _dim_location(job)
    skills, direct_skills = _dim_skills(job, family)
    arabic, english, lang_reasons = _dim_language(job)
    experience, exp_reason = _dim_experience(job)
    salary, salary_value, salary_reason = _dim_salary(job)
    education, edu_reason = _dim_education(job)
    relevance, relevance_reason = _dim_relevance(job, family)

    job.dimensions = {
        "location": loc,
        "skills": skills,
        "arabic": arabic,
        "english": english,
        "experience": experience,
        "salary": salary,
        "education": education,
        "relevance": relevance,
    }
    base = sum(job.dimensions.values())

    if direct_skills:
        job.reasons.append("Transferable evidence: " + ", ".join(direct_skills[:5]))
    job.reasons.extend(lang_reasons)
    if loc:
        job.reasons.append("Location is actionable for Timișoara/Romania")
    if experience:
        job.reasons.append(exp_reason)
    if salary_value is not None:
        job.reasons.append(salary_reason)
    else:
        job.warnings.append(salary_reason + " — ask early in the process")
    if education:
        job.reasons.append(edu_reason)
    if relevance:
        job.reasons.append(relevance_reason)

    # Career-family guardrail: family fit is a multiplier, not a replacement for
    # the existing dimensional score. This preserves the old scoring model while
    # preventing generic English/operations points from producing false positives.
    if family_fit >= 75:
        multiplier = 1.00
    elif family_fit >= 55:
        multiplier = 0.92
    elif family_fit >= 35:
        multiplier = 0.78
    elif family_fit >= 15:
        multiplier = 0.58
    else:
        multiplier = 0.25

    score = round(base * multiplier)
    # Direct Arabic roles get a modest tie-breaker, never enough to rescue a bad
    # family fit by themselves.
    if arabic == 15 and family_fit >= 35:
        score = min(100, score + 3)
    # Freshness boost is capped and only affects ranking, not eligibility.
    if job.age_days is not None:
        if job.age_days <= 3:
            score += 3
        elif job.age_days <= 7:
            score += 2
        elif job.age_days > 45:
            score -= 3
    # Multi-source confirmation is a useful trust signal.
    if job.duplicate_count >= 2:
        score += 2
        job.reasons.append(f"Seen on {job.duplicate_count} job sources")
    job.score = max(0, min(100, score))

    if family_fit >= 65 and base >= 45:
        job.confidence = "high"
    elif family_fit >= 35 and base >= 30:
        job.confidence = "medium"
    else:
        job.confidence = "low"
    return job


def rank_jobs(raw_jobs: Sequence[Dict[str, Any] | Job], profile: Dict[str, Any] = PROFILE) -> Dict[str, Any]:
    jobs, merged = deduplicate_jobs(raw_jobs)
    eligible = []
    stats = {
        "raw": len(raw_jobs), "unique": len(jobs), "duplicates_removed": merged,
        "rejected_hard": 0, "rejected_language": 0, "rejected_romanian": 0,
        "rejected_location": 0, "rejected_experience": 0,
    }
    rejected = []
    for job in jobs:
        ok, reasons = hard_eligibility(job, profile)
        if not ok:
            job.hard_reject_reasons = reasons
            rejected.append(job)
            stats["rejected_hard"] += 1
            joined = normalize_text(" ".join(reasons))
            if "required language" in joined: stats["rejected_language"] += 1
            if "romanian" in joined: stats["rejected_romanian"] += 1
            if "remote role" in joined or "on-site" in joined or "outside romania" in joined: stats["rejected_location"] += 1
            if "years of experience" in joined: stats["rejected_experience"] += 1
            continue
        eligible.append(score_job(job, profile))

    eligible.sort(key=lambda j: (j.score, j.family_fit, -(j.age_days if j.age_days is not None else 9999)), reverse=True)
    return {"jobs": eligible, "rejected": rejected, "stats": stats}


# ---------------------------------------------------------------------------
# Source adapter helpers. These are intentionally transport-agnostic so the
# project can add Selenium/curl_cffi adapters without touching the ranking code.
# ---------------------------------------------------------------------------
class SourceAdapter:
    name = "base"
    requires_credentials = False

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        return raw

    def search(self, query: str, location: str, limit: int = 20) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        raise NotImplementedError


class JoobleAdapter(SourceAdapter):
    name = "Jooble"
    requires_credentials = True

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, location: str, limit: int = 20):
        import requests
        if not self.api_key:
            return [], "JOOBLE_API_KEY missing"
        payload = {"keywords": query, "location": location or "Timisoara, Romania", "radius": "40", "page": "1", "ResultOnPage": str(limit), "companysearch": "false"}
        try:
            r = requests.post(f"https://jooble.org/api/{self.api_key}", json=payload, timeout=30, headers={"Accept": "application/json", "User-Agent": "CareerOS/3.0"})
            if r.status_code != 200:
                return [], f"HTTP {r.status_code}"
            jobs = []
            for x in r.json().get("jobs", [])[:limit]:
                jobs.append({"title": x.get("title"), "company": x.get("company"), "location": x.get("location") or location, "description": x.get("snippet", ""), "redirect_url": x.get("link", ""), "salary_text": x.get("salary", ""), "source": "Jooble"})
            return jobs, None
        except Exception as exc:
            return [], str(exc)


class RemotiveAdapter(SourceAdapter):
    name = "Remotive"

    def search(self, query: str, location: str = "", limit: int = 20):
        import requests
        try:
            r = requests.get("https://remotive.com/api/remote-jobs", timeout=30, headers={"Accept": "application/json", "User-Agent": "CareerOS/3.0"})
            if r.status_code != 200:
                return [], f"HTTP {r.status_code}"
            qwords = [w for w in re.findall(r"[a-zA-Z]+", normalize_text(query)) if len(w) >= 3]
            jobs = []
            for x in r.json().get("jobs", []):
                text = normalize_text(" ".join([x.get("title", ""), x.get("company_name", ""), x.get("description", ""), x.get("category", "")]))
                if qwords and not any(w in text for w in qwords):
                    continue
                jobs.append({"title": x.get("title"), "company": x.get("company_name"), "location": f"Remote — {x.get('candidate_required_location', 'Worldwide')}", "description": x.get("description", ""), "redirect_url": x.get("url", ""), "salary_text": x.get("salary", ""), "source": "Remotive"})
                if len(jobs) >= limit:
                    break
            return jobs, None
        except Exception as exc:
            return [], str(exc)


# Registry makes future eJobs/BestJobs/LinkedIn adapters drop-in additions.
SOURCE_ADAPTERS = {
    "Jooble": JoobleAdapter,
    "Remotive": RemotiveAdapter,
}

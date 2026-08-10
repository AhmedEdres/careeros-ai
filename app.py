import streamlit as st
import requests
import re
import html
import unicodedata
import csv
import io
import json
import hashlib
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="CareerOS AI",
    page_icon="🎯",
    layout="wide",
)

# =========================================================
# API KEYS
# =========================================================
ADZUNA_APP_ID = st.secrets.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = st.secrets.get("ADZUNA_APP_KEY", "")
JOOBLE_API_KEY = st.secrets.get("JOOBLE_API_KEY", "")
CLAUDE_API_KEY = st.secrets.get("CLAUDE_API_KEY", "")


# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================
def init_session():
    defaults = {
        "applied_jobs": {},        # {url: {title, company, date, status, notes}}
        "search_results": [],
        "claude_cache": {},        # {job_url: analysis_text}
        "search_count": 0,        # Force-refresh counter
        "page_index": 0,          # Pagination
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()


# =========================================================
# EDITABLE PROFILE (stored in session_state)
# =========================================================
DEFAULT_PROFILE = {
    "name": "Ahmed",
    "location": "Timisoara",
    "country": "Romania",
    "languages": ["Arabic", "English", "Romanian"],
    "romanian_level": "Beginner",
    "education": "Master's Degree in Law",
    "experience_years": 10,
    "skills": [
        "operations", "client management", "financial compliance",
        "customer service", "customer support", "excel", "sap",
        "erp", "sql", "administration", "logistics", "arabic",
        "english", "tax", "banking", "accounting",
    ],
    "target_salary_min": 5000,
    "target_salary_max": 7000,
    "preferred_locations": ["Timisoara", "Romania", "Remote"],
    "preferred_categories": [
        "Finance", "Accounting", "Tax", "Legal",
        "Compliance", "Administration", "Customer Support",
        "Back Office", "Logistics",
    ],
}

if "profile" not in st.session_state:
    st.session_state.profile = DEFAULT_PROFILE.copy()

PROFILE = st.session_state.profile


# =========================================================
# SKILL GROUPS — expanded keyword matching
# =========================================================
SKILL_GROUPS = {
    "operations_support": {
        "words": [
            "operations", "operational", "coordinator", "administrator",
            "administration", "back office", "backoffice",
            "customer support", "customer service", "customer care",
            "client service", "client support", "client management",
            "call center", "call centre", "contact center",
            "contact centre", "help desk", "helpdesk", "service desk",
            "support specialist", "support agent", "support representative",
            "customer success", "customer experience", "bpo",
            "business process", "shared services", "shared service",
            "order management", "order processing", "data entry",
        ],
        "weight": 15,
        "label": "Operations / Customer Support",
    },
    "finance_compliance": {
        "words": [
            "finance", "financial", "accounting", "accountant",
            "accounts payable", "accounts receivable", "bookkeeping",
            "tax", "taxation", "compliance", "regulatory",
            "invoice", "invoicing", "billing", "procurement",
            "legal", "audit", "auditor", "auditing",
            "banking", "bank", "collection", "collections",
            "treasury", "credit", "credit control", "risk",
            "aml", "anti-money laundering", "kyc",
            "know your customer", "due diligence",
            "financial analyst", "financial controller",
        ],
        "weight": 18,
        "label": "Finance / Compliance / Legal",
    },
    "logistics": {
        "words": [
            "logistics", "warehouse", "depot", "supply chain",
            "inventory", "transport", "transportation",
            "purchasing", "procurement", "shipping",
            "freight", "distribution", "fulfillment",
        ],
        "weight": 10,
        "label": "Logistics / Supply Chain",
    },
    "tools": {
        "words": [
            "sap", "erp", "excel", "microsoft excel", "sql",
            "ibm cognos", "power bi", "vba",
        ],
        "weight": 8,
        "label": "Tools (SAP / ERP / Excel / SQL)",
    },
}

# Romanian patterns
ROMANIAN_PATTERNS_HIGH = [
    "romanian c1", "romanian c2", "romana c1", "romana c2",
    "fluent romanian", "romanian fluent", "fluent in romanian",
    "native romanian", "romanian native",
    "limba romana nivel avansat", "romana avansat",
]
ROMANIAN_PATTERNS_ANY = ROMANIAN_PATTERNS_HIGH + [
    "romanian required", "romanian language required",
    "limba romana", "limba română", "romanian b2", "romana b2",
    "cunoasterea limbii romane", "cunoștințe de limba română",
]

# Negative keywords
NEGATIVE_KEYWORDS = [
    "senior developer", "senior engineer", "lead developer",
    "staff engineer", "principal engineer", "machine learning engineer",
    "data scientist", "devops", "full stack developer",
    "frontend developer", "backend developer",
    "react developer", "java developer", "python developer",
    "c++ developer", "golang developer", "rust developer",
    "ios developer", "android developer",
    "ux designer", "ui designer", "graphic designer",
    "medical doctor", "nurse", "dentist", "pharmacist",
    "truck driver", "construction worker", "electrician",
    "plumber", "mechanic",
]

# Location synonyms for smarter filtering
LOCATION_SYNONYMS = {
    "Timișoara": [
        "timisoara", "timișoara", "temesvar", "temeschburg",
        "timis", "timiș",
    ],
    "Romania": [
        "romania", "românia", "bucharest", "bucurești",
        "cluj", "iasi", "iași", "brasov", "brașov",
        "timisoara", "constanta", "constanța",
    ],
    "Remote": ["remote", "work from home", "wfh", "anywhere"],
    "Europe": [
        "europe", "europa", "eu", "eea",
        "germany", "france", "spain", "italy", "netherlands",
        "poland", "czech", "austria", "belgium", "portugal",
        "romania", "timisoara",
    ],
}


# =========================================================
# TEXT HELPERS
# =========================================================
def normalize_text(text: str) -> str:
    text = str(text or "")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower()


def clean_html_text(text: str) -> str:
    text = html.unescape(str(text or ""))
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_company_name(company) -> str:
    if isinstance(company, dict):
        return str(company.get("display_name", "") or "Company not listed")
    return str(company or "Company not listed")


def normalize_location(location: str) -> str:
    location = str(location or "").strip()
    if not location:
        return "Timisoara, Romania"
    normalized = normalize_text(location)
    if normalized in {"timisoara", "timisoara romania", "timis", "timis romania"}:
        return "Timisoara, Romania"
    if "romania" not in normalized and (
        "timisoara" in normalized or normalized == "timis"
    ):
        return f"{location}, Romania"
    return location


def is_romania_location(location: str) -> bool:
    text = normalize_text(location)
    return any(
        place in text
        for place in ["romania", "timisoara", "bucharest", "bucuresti"]
    )


def valid_url(url: str) -> bool:
    try:
        parsed = urlparse(str(url))
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def text_hash(text: str) -> str:
    """Fast hash for deduplication instead of O(n²) fuzzy matching."""
    # Normalize aggressively: remove non-alphanumeric, lowercase
    cleaned = re.sub(r"[^a-z0-9]", "", normalize_text(text))
    return hashlib.md5(cleaned.encode()).hexdigest()


# =========================================================
# APPLICATION TRACKING — JSON-based persistence
# =========================================================
APPLIED_FILE = "applied_jobs.json"


def load_applied() -> Dict:
    """Load applied jobs from JSON file (persistent across reruns)."""
    try:
        with open(APPLIED_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_applied(data: Dict):
    """Save applied jobs to JSON file."""
    try:
        with open(APPLIED_FILE, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # Graceful fail on read-only filesystems


def mark_applied(job_url: str, title: str, company: str, notes: str = ""):
    """Mark a job as applied with metadata."""
    applied = load_applied()
    applied[job_url] = {
        "title": title,
        "company": company,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "Applied",
        "notes": notes,
    }
    save_applied(applied)
    st.session_state.applied_jobs = applied


def get_applied_urls() -> set:
    """Get set of applied job URLs."""
    return set(load_applied().keys())


# Initialize from file on first load
if not st.session_state.applied_jobs:
    st.session_state.applied_jobs = load_applied()


# =========================================================
# JOOBLE — PRIMARY ROMANIA SOURCE
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def search_jooble_jobs(
    keywords: str,
    location: str,
    results_per_page: int = 20,
    pages: int = 2,
    _refresh: int = 0,  # Force-refresh parameter
) -> Tuple[List[Dict], Optional[str]]:
    if not JOOBLE_API_KEY:
        return [], (
            "Jooble API key is missing. "
            "Add JOOBLE_API_KEY to Streamlit Secrets."
        )

    search_location = normalize_location(location)
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Ahmed-CareerOS/2.0",
    }

    all_jobs: List[Dict] = []

    for page_num in range(1, pages + 1):
        payload = {
            "keywords": keywords.strip(),
            "location": search_location,
            "radius": "50",
            "page": str(page_num),
            "ResultOnPage": str(results_per_page),
            "companysearch": "false",
        }

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=35
            )

            if response.status_code == 401:
                return [], "Jooble rejected the API key (HTTP 401)."
            if response.status_code == 403:
                return [], "Jooble denied access (HTTP 403)."
            if response.status_code == 404:
                return [], "Jooble endpoint not found (HTTP 404)."
            if response.status_code != 200:
                body = clean_html_text(response.text)[:250]
                return [], f"Jooble HTTP {response.status_code}: {body}"

            data = response.json()
            jooble_jobs = data.get("jobs", [])

            if not isinstance(jooble_jobs, list) or not jooble_jobs:
                break

            for job in jooble_jobs:
                if not isinstance(job, dict):
                    continue

                company = safe_company_name(
                    job.get("company", "Company not listed")
                )
                job_location = job.get("location") or search_location

                all_jobs.append({
                    "title": job.get("title", "Job title not available"),
                    "company": {"display_name": company},
                    "location": {"display_name": str(job_location)},
                    "description": job.get("snippet", ""),
                    "redirect_url": job.get("link", ""),
                    "salary_text": job.get("salary", ""),
                    "salary_min": None,
                    "salary_max": None,
                    "source": (
                        "Jooble"
                        + (f" / {job.get('source')}" if job.get("source") else "")
                    ),
                    "category": {"label": job.get("type", "")},
                    "jooble_id": job.get("id"),
                    "updated": job.get("updated", ""),
                })

        except requests.exceptions.Timeout:
            if all_jobs:
                break
            return [], "Jooble request timed out."
        except requests.exceptions.RequestException as error:
            if all_jobs:
                break
            return [], f"Jooble connection error: {error}"
        except ValueError:
            if all_jobs:
                break
            return [], "Jooble returned invalid JSON."

    return all_jobs, None


# =========================================================
# REMOTIVE — REMOTE JOBS
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def search_remotive_jobs(
    keywords: str,
    results_per_page: int = 20,
    _refresh: int = 0,
) -> Tuple[List[Dict], Optional[str]]:
    url = "https://remotive.com/api/remote-jobs"
    headers = {
        "User-Agent": "Ahmed-CareerOS/2.0",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=35)

        if response.status_code != 200:
            return [], f"Remotive returned HTTP {response.status_code}."

        data = response.json()
        remotive_jobs = data.get("jobs", [])

        search_words = [
            word.lower()
            for word in re.findall(r"[a-zA-Z]+", keywords)
            if len(word) >= 3
        ]

        normalized_jobs: List[Dict] = []

        for job in remotive_jobs:
            if not isinstance(job, dict):
                continue

            title = job.get("title", "")
            company = job.get("company_name", "")
            description = job.get("description", "")
            category = job.get("category", "")
            candidate_location = job.get(
                "candidate_required_location", "Remote"
            )

            searchable = normalize_text(
                f"{title} {company} {description} {category}"
            )

            if search_words and not any(w in searchable for w in search_words):
                continue

            normalized_jobs.append({
                "title": title or "Job title not available",
                "company": {"display_name": company or "Company not listed"},
                "location": {"display_name": f"Remote — {candidate_location}"},
                "description": description,
                "redirect_url": job.get("url", ""),
                "salary_text": job.get("salary", ""),
                "salary_min": None,
                "salary_max": None,
                "source": "Remotive",
                "category": {"label": category},
            })

            if len(normalized_jobs) >= results_per_page:
                break

        return normalized_jobs, None

    except requests.exceptions.Timeout:
        return [], "Remotive request timed out."
    except requests.exceptions.RequestException as error:
        return [], f"Remotive connection error: {error}"
    except ValueError:
        return [], "Remotive returned invalid JSON."


# =========================================================
# ADZUNA — OPTIONAL
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def search_adzuna_jobs(
    keywords: str,
    location: str,
    results_per_page: int = 20,
    _refresh: int = 0,
) -> Tuple[List[Dict], Optional[str]]:
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return [], "Adzuna credentials not configured."

    if is_romania_location(location):
        return [], "Adzuna skipped for Romania; using Jooble."

    country_code = "gb"
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": keywords,
        "where": location,
        "content-type": "application/json",
        "sort_by": "date",
    }
    headers = {
        "User-Agent": "Ahmed-CareerOS/2.0",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=25)

        if response.status_code != 200:
            return [], f"Adzuna HTTP {response.status_code}."

        data = response.json()
        results = data.get("results", [])
        normalized: List[Dict] = []

        for job in results[:results_per_page]:
            loc_data = job.get("location", {})
            display_loc = (
                loc_data.get("display_name", location)
                if isinstance(loc_data, dict)
                else str(loc_data or location)
            )
            cat_data = job.get("category", {})
            display_cat = (
                cat_data.get("label", "")
                if isinstance(cat_data, dict)
                else str(cat_data or "")
            )

            normalized.append({
                "title": job.get("title", "Job title not available"),
                "company": {"display_name": safe_company_name(job.get("company", {}))},
                "location": {"display_name": display_loc},
                "description": job.get("description", ""),
                "redirect_url": job.get("redirect_url", ""),
                "salary_text": (
                    f"{job.get('salary_min')} - {job.get('salary_max')}"
                    if job.get("salary_min") is not None else ""
                ),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "source": "Adzuna",
                "category": {"label": display_cat},
            })

        return normalized, None

    except requests.exceptions.Timeout:
        return [], "Adzuna request timed out."
    except requests.exceptions.RequestException as error:
        return [], f"Adzuna connection error: {error}"
    except ValueError:
        return [], "Adzuna returned invalid JSON."


# =========================================================
# DEDUPLICATION — Hash-based O(n) instead of O(n²)
# =========================================================
def remove_duplicate_jobs(jobs: List[Dict]) -> List[Dict]:
    unique: List[Dict] = []
    seen_urls: set = set()
    seen_hashes: set = set()

    for job in jobs:
        link = str(job.get("redirect_url", "") or "").strip().lower()

        # 1. URL-based dedup (primary — fast)
        if link:
            clean_link = re.sub(
                r"[?&](utm_\w+|ref|source|medium|fbclid|gclid)=[^&]*", "", link
            )
            if clean_link in seen_urls:
                continue
            seen_urls.add(clean_link)

        # 2. Hash-based title+company dedup (O(1) per job)
        title = normalize_text(job.get("title", ""))
        company = normalize_text(safe_company_name(job.get("company", {})))
        job_hash = text_hash(f"{title}{company}")

        if job_hash in seen_hashes:
            continue
        seen_hashes.add(job_hash)

        unique.append(job)

    return unique


# =========================================================
# MATCHING ENGINE — Weighted Multi-Dimensional (max 100)
# =========================================================
def calculate_match(job: Dict) -> Dict:
    """
    Dimension weights (total = 100):
      Location:     20    |  Arabic:      15
      English:      10    |  Skills:      25
      Experience:   10    |  Education:    5
      Salary:       10    |  Relevance:    5
    """
    title = job.get("title", "")
    description = job.get("description", "")
    company = safe_company_name(job.get("company", {}))
    category = job.get("category", {}).get("label", "")
    location_text = job.get("location", {}).get("display_name", "")
    salary_min = job.get("salary_min")

    text = normalize_text(f"{title} {description} {company} {category}")
    title_norm = normalize_text(title)
    loc_norm = normalize_text(location_text)

    dims = {}
    reasons = []
    warnings = []
    score = 0

    # --- 1. LOCATION (max 20) ---
    loc_score = 0
    if any(s in loc_norm for s in LOCATION_SYNONYMS["Timișoara"]):
        loc_score = 20
        reasons.append("📍 Location: Timișoara — perfect match")
    elif any(s in loc_norm for s in ["romania", "românia"]):
        loc_score = 15
        reasons.append("🇷🇴 Location: Romania")
    elif any(s in loc_norm for s in LOCATION_SYNONYMS["Remote"]):
        loc_score = 12
        reasons.append("🏠 Location: Remote")
    elif any(s in loc_norm for s in ["europe", "europa", "eu", "eea"]):
        loc_score = 8
        reasons.append("🌍 Location: Europe")
    else:
        loc_score = 3
    score += loc_score
    dims["location"] = loc_score

    # --- 2. ARABIC (max 15) ---
    arabic_score = 0
    if any(w in text for w in ["arabic", "arabe", "arabă", "limba araba"]):
        arabic_score = 15
        reasons.append("🗣️ Arabic language required — strong match")
    else:
        arabic_score = 2
    score += arabic_score
    dims["arabic"] = arabic_score

    # --- 3. ENGLISH (max 10) ---
    eng_score = 0
    if any(w in text for w in ["english", "engleza", "limba engleza"]):
        eng_score = 10
        reasons.append("🇬🇧 English language required — matches profile")
    else:
        eng_score = 4
    score += eng_score
    dims["english"] = eng_score

    # --- 4. SKILLS (max 25) ---
    skill_score = 0
    matched_groups = []
    for group_data in SKILL_GROUPS.values():
        if any(w in text for w in group_data["words"]):
            skill_score += group_data["weight"]
            matched_groups.append(group_data["label"])
    skill_score = min(skill_score, 25)
    if matched_groups:
        reasons.append(
            f"💼 Skills: {', '.join(matched_groups[:3])} ({skill_score}/25)"
        )
    score += skill_score
    dims["skills"] = skill_score

    # --- 5. EXPERIENCE (max 10) ---
    exp_score = 0
    if re.search(r"\b(?:senior|lead|manager|director|head of)\b", title_norm):
        exp_score = 10
        reasons.append("🧑‍💼 Senior/leadership — fits 10+ years")
    elif re.search(r"\b(?:mid|intermediate|specialist)\b", title_norm):
        exp_score = 8
        reasons.append("🧑‍💼 Mid-level role")
    elif re.search(r"\b(?:junior|entry|intern|trainee|graduate)\b", title_norm):
        exp_score = 4
        reasons.append("🧑‍💼 Entry-level — may be below experience")
    else:
        exp_score = 6
    score += exp_score
    dims["experience"] = exp_score

    # --- 6. EDUCATION (max 5) ---
    edu_score = 0
    if any(w in text for w in ["law", "legal", "juridic", "master"]):
        edu_score = 5
        reasons.append("🎓 Aligns with Law degree")
    else:
        edu_score = 3
    score += edu_score
    dims["education"] = edu_score

    # --- 7. SALARY (max 10) ---
    salary_score = 0
    if salary_min is not None and isinstance(salary_min, (int, float)):
        if salary_min >= PROFILE["target_salary_min"]:
            salary_score = 10
            reasons.append(f"💰 Salary meets target ({salary_min:,.0f}+)")
        elif salary_min >= PROFILE["target_salary_min"] * 0.8:
            salary_score = 7
        else:
            salary_score = 2
    else:
        salary_score = 5
    score += salary_score
    dims["salary"] = salary_score

    # --- 8. RELEVANCE (max 5) ---
    relevance_score = 0
    if any(w in text for w in [
        "multilingual", "bilingual", "bpo", "shared service",
        "outsourcing", "middle east", "mena", "gulf",
    ]):
        relevance_score = 5
        reasons.append("🌐 Multilingual / BPO / MENA relevance")
    else:
        relevance_score = 2
    score += relevance_score
    dims["relevance"] = relevance_score

    # ===== PENALTIES =====
    if any(normalize_text(p) in text for p in ROMANIAN_PATTERNS_HIGH):
        score -= 15
        warnings.append("⚠️ Requires advanced Romanian (C1/C2/fluent)")
    elif any(normalize_text(p) in text for p in ROMANIAN_PATTERNS_ANY):
        score -= 8
        warnings.append("⚠️ Romanian language may be required")

    restricted = [
        "united states", "usa only", "us only",
        "canada only", "uk only", "india only", "us-based",
    ]
    if "remote" in loc_norm and any(r in loc_norm for r in restricted):
        score -= 10
        warnings.append("🌍 Remote but geographically restricted")

    if any(nk in title_norm for nk in NEGATIVE_KEYWORDS):
        score -= 20
        warnings.append("🚫 Role title suggests different career track")

    score = max(0, min(100, score))

    return {
        "score": score,
        "reasons": reasons,
        "warnings": warnings,
        "dimensions": dims,
    }


# =========================================================
# CLAUDE AI ANALYSIS — per-job, cached, structured
# =========================================================
def analyze_with_claude(job: Dict, match_data: Dict) -> str:
    """Analyze a single job with Claude, using match context."""
    if not CLAUDE_API_KEY:
        return "⚠️ Claude API key not configured. Add CLAUDE_API_KEY to Secrets."

    job_url = job.get("redirect_url", "")

    # Check cache first
    if job_url and job_url in st.session_state.claude_cache:
        return st.session_state.claude_cache[job_url]

    title = job.get("title", "Unknown")
    company = safe_company_name(job.get("company", {}))
    location = job.get("location", {}).get("display_name", "Unknown")
    description = clean_html_text(job.get("description", ""))[:2000]
    salary = job.get("salary_text", "Not specified")

    # Include match engine context for better analysis
    match_reasons = "\n".join(f"  - {r}" for r in match_data.get("reasons", []))
    match_warnings = "\n".join(f"  - {w}" for w in match_data.get("warnings", []))
    match_score = match_data.get("score", 0)
    dims = match_data.get("dimensions", {})

    prompt = f"""You are Ahmed's career advisor. Analyze this job against his profile.

AHMED'S PROFILE:
- 10 years: operations, client management, financial compliance, tax, accounting, collections, B2B
- Managed 250+ corporate accounts at Egyptian Tax Authority
- Languages: Arabic (native), English (B2+), Romanian (beginner A1)
- Education: Master's in Law (LL.M.)
- Location: Timișoara, Romania (full work authorization, currently employed)
- Tools: SAP, Excel/VBA, IBM Cognos, Power BI, SQL
- Target salary: 5,000-7,000 RON/month

JOB DETAILS:
Title: {title}
Company: {company}
Location: {location}
Salary: {salary}
Description: {description}

MATCHING ENGINE RESULTS (score: {match_score}/100):
Dimension scores: {json.dumps(dims)}
Strengths found:
{match_reasons}
Warnings:
{match_warnings}

INSTRUCTIONS:
Respond in this exact format:
MATCH: [X]% — [one-line justification]

STRENGTHS:
1. [strength]
2. [strength]
3. [strength]

RISKS:
1. [risk]
2. [risk]
3. [risk]

VERDICT: [APPLY / SKIP / APPLY WITH CAUTION] — [reason]

Be concise, practical, and specific to Ahmed's situation."""

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        result = response.content[0].text

        # Cache the result
        if job_url:
            st.session_state.claude_cache[job_url] = result

        return result
    except ImportError:
        return "❌ anthropic package not installed. Add it to requirements.txt."
    except Exception as e:
        return f"❌ Claude analysis failed: {e}"


# =========================================================
# MULTI-QUERY SEARCH
# =========================================================
def build_search_queries(base_keywords: str) -> List[str]:
    queries = [base_keywords.strip()]
    base_lower = base_keywords.lower().strip()

    expansions = {
        "customer support": ["customer service", "arabic customer support"],
        "customer service": ["customer support", "arabic customer service"],
        "operations": ["operations coordinator", "back office operations"],
        "accounting": ["accounts payable", "accounts receivable"],
        "finance": ["financial operations", "financial compliance"],
        "back office": ["back office operations", "data entry"],
        "tax": ["tax accounting", "tax compliance"],
    }

    for key, extras in expansions.items():
        if key in base_lower:
            queries.extend(extras)
            break

    seen = set()
    unique = []
    for q in queries:
        if q.lower() not in seen:
            seen.add(q.lower())
            unique.append(q)

    return unique[:4]


# =========================================================
# PARALLEL SEARCH
# =========================================================
def run_parallel_search(
    keywords: str,
    location: str,
    max_results: int,
    use_jooble: bool,
    use_remotive: bool,
    use_adzuna: bool,
    expand_queries: bool,
    refresh_count: int,
) -> Tuple[List[Dict], List[str], List[str]]:

    queries = build_search_queries(keywords) if expand_queries else [keywords]
    tasks = []

    for query in queries:
        if use_jooble:
            tasks.append((
                "Jooble", search_jooble_jobs,
                {"keywords": query, "location": location,
                 "results_per_page": max_results, "pages": 2,
                 "_refresh": refresh_count}
            ))
        if use_remotive:
            tasks.append((
                "Remotive", search_remotive_jobs,
                {"keywords": query, "results_per_page": max_results,
                 "_refresh": refresh_count}
            ))
        if use_adzuna:
            tasks.append((
                "Adzuna", search_adzuna_jobs,
                {"keywords": query, "location": location,
                 "results_per_page": max_results,
                 "_refresh": refresh_count}
            ))

    if not tasks:
        return [], [], ["No search sources selected."]

    all_jobs: List[Dict] = []
    errors: List[str] = []
    source_counts: Dict[str, int] = {}

    with ThreadPoolExecutor(max_workers=6) as executor:
        future_map = {
            executor.submit(func, **kwargs): name
            for name, func, kwargs in tasks
        }

        for future in as_completed(future_map):
            source = future_map[future]
            try:
                jobs, err = future.result()
                if err:
                    if "skipped for Romania" not in str(err):
                        errors.append(f"{source}: {err}")
                else:
                    all_jobs.extend(jobs)
                    source_counts[source] = (
                        source_counts.get(source, 0) + len(jobs)
                    )
            except Exception as e:
                errors.append(f"{source}: {e}")

    counts_list = [f"{s}: {c}" for s, c in source_counts.items()]
    return all_jobs, counts_list, errors


# =========================================================
# EXPORT
# =========================================================
def export_jobs_csv(jobs: List[Dict]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Title", "Company", "Location", "Source",
        "Match %", "Salary", "Link", "Warnings", "Applied",
    ])
    applied_urls = get_applied_urls()
    for idx, job in enumerate(jobs):
        match = job.get("_match", {})
        url = job.get("redirect_url", "")
        writer.writerow([
            idx + 1,
            job.get("title", ""),
            safe_company_name(job.get("company", {})),
            job.get("location", {}).get("display_name", ""),
            job.get("source", ""),
            match.get("score", 0),
            job.get("salary_text", ""),
            url,
            "; ".join(match.get("warnings", [])),
            "Yes" if url in applied_urls else "No",
        ])
    return output.getvalue()


def export_applied_csv() -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "Company", "Date Applied", "Status", "Notes", "URL"])
    for url, data in st.session_state.applied_jobs.items():
        writer.writerow([
            data.get("title", ""),
            data.get("company", ""),
            data.get("date", ""),
            data.get("status", ""),
            data.get("notes", ""),
            url,
        ])
    return output.getvalue()


# =========================================================
# UI — HEADER
# =========================================================
st.title("🎯 CareerOS AI")
st.subheader("AI-Powered Job Search & Application Assistant")
st.write(
    "Search Romanian and remote jobs, combine multiple sources, "
    "rank them against your profile, track applications."
)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("⚙️ Search Settings")

    keywords = st.text_input("🔍 Keywords", "customer support")
    location = st.text_input("📍 Location", "Timisoara")
    max_results = st.slider("Results per source", 5, 50, 25)

    st.divider()
    st.subheader("🔗 Sources")
    search_jooble = st.checkbox("🇷🇴 Jooble — Romania", value=True)
    search_remote = st.checkbox("🌍 Remotive — Remote", value=True)
    search_adzuna = st.checkbox("🌐 Adzuna — International", value=False)

    st.divider()
    st.subheader("📌 Filters")

    expand_queries = st.checkbox(
        "🔄 Expand search queries", value=True,
        help="Search related keyword variations automatically",
    )

    location_filter = st.selectbox(
        "Location filter",
        ["All", "Timișoara", "Romania", "Remote", "Europe"],
    )

    min_match = st.slider("Minimum match %", 0, 100, 40, 5)

    romanian_filter = st.radio(
        "Romanian requirement",
        ["Any", "Exclude Romanian-required", "Allow beginner-friendly"],
    )

    st.divider()
    st.subheader("👤 Edit Profile")
    with st.expander("Adjust your profile", expanded=False):
        new_exp = st.number_input(
            "Years of experience",
            min_value=0, max_value=40,
            value=PROFILE["experience_years"],
        )
        new_rom = st.selectbox(
            "Romanian level",
            ["Beginner", "A1", "A2", "B1", "B2", "C1", "C2"],
            index=0,
        )
        new_sal_min = st.number_input(
            "Min salary (RON)", value=PROFILE["target_salary_min"], step=500
        )
        new_sal_max = st.number_input(
            "Max salary (RON)", value=PROFILE["target_salary_max"], step=500
        )
        if st.button("💾 Save profile changes"):
            st.session_state.profile["experience_years"] = new_exp
            st.session_state.profile["romanian_level"] = new_rom
            st.session_state.profile["target_salary_min"] = new_sal_min
            st.session_state.profile["target_salary_max"] = new_sal_max
            st.toast("✅ Profile updated!")

    st.divider()
    st.subheader("💡 Suggested searches")
    st.caption(
        "• arabic customer support\n"
        "• customer service english\n"
        "• operations specialist\n"
        "• back office\n"
        "• financial operations\n"
        "• accounts payable\n"
        "• tax accounting\n"
        "• logistics coordinator\n"
        "• SAP Excel"
    )

    st.divider()
    st.subheader("🔐 API status")
    st.write(f"Jooble: {'✅' if JOOBLE_API_KEY else '❌ missing'}")
    st.write(f"Adzuna: {'✅' if ADZUNA_APP_ID and ADZUNA_APP_KEY else '⚪ not set'}")
    st.write("Remotive: ✅ no key needed")
    st.write(f"Claude: {'✅' if CLAUDE_API_KEY else '⚪ optional'}")

    st.divider()
    applied_count = len(st.session_state.applied_jobs)
    st.metric("📋 Applications tracked", applied_count)


# =========================================================
# SEARCH SECTION
# =========================================================
st.divider()

search_col, refresh_col = st.columns([3, 1])
with search_col:
    search_clicked = st.button("🔎 Search Jobs", type="primary")
with refresh_col:
    force_refresh = st.button(
        "🔄 Force Refresh",
        help="Bypass cache and fetch fresh results",
    )

if force_refresh:
    st.session_state.search_count += 1
    search_clicked = True

JOBS_PER_PAGE = 10

if search_clicked:
    st.session_state.page_index = 0  # Reset pagination

    with st.status("Searching across sources...", expanded=True) as status:
        all_jobs, source_counts, search_errors = run_parallel_search(
            keywords=keywords,
            location=location,
            max_results=max_results,
            use_jooble=search_jooble,
            use_remotive=search_remote,
            use_adzuna=search_adzuna,
            expand_queries=expand_queries,
            refresh_count=st.session_state.search_count,
        )

        if source_counts:
            status.update(
                label=f"✅ {' | '.join(source_counts)}",
                state="complete",
            )
        else:
            status.update(label="⚠️ No sources returned results", state="error")

    for err in search_errors:
        st.warning(err)

    st.toast(f"Search complete — {len(all_jobs)} raw results")

    # Deduplicate
    all_jobs = remove_duplicate_jobs(all_jobs)

    if not all_jobs:
        st.error("No jobs found. Try different keywords or check API keys.")
        st.markdown(
            "**Quick troubleshooting:**\n\n"
            "1. Jooble API key is set in Streamlit Secrets\n"
            "2. Secret name is exactly `JOOBLE_API_KEY`\n"
            "3. Try a simpler search like `customer support`\n"
            "4. Make sure location is `Timisoara`"
        )
    else:
        # Score
        for job in all_jobs:
            job["_match"] = calculate_match(job)

        # Filter
        filtered = []
        for job in all_jobs:
            match = job["_match"]
            s = match["score"]

            if s < min_match:
                continue

            loc = normalize_text(
                job.get("location", {}).get("display_name", "")
            )
            if location_filter != "All":
                synonyms = LOCATION_SYNONYMS.get(location_filter, [])
                if synonyms and not any(syn in loc for syn in synonyms):
                    continue

            if romanian_filter != "Any":
                text = normalize_text(
                    f"{job.get('title', '')} {job.get('description', '')}"
                )
                if romanian_filter == "Exclude Romanian-required":
                    if any(normalize_text(p) in text for p in ROMANIAN_PATTERNS_ANY):
                        continue
                elif romanian_filter == "Allow beginner-friendly":
                    if any(normalize_text(p) in text for p in ROMANIAN_PATTERNS_HIGH):
                        continue

            filtered.append(job)

        filtered.sort(key=lambda j: j["_match"]["score"], reverse=True)
        st.session_state.search_results = filtered

        if not filtered:
            st.warning(
                f"No jobs passed filters (min {min_match}%). "
                "Try lowering minimum or changing filters."
            )
        else:
            # Dashboard
            best_score = filtered[0]["_match"]["score"]
            high_count = sum(1 for j in filtered if j["_match"]["score"] >= 70)

            st.success(f"Found {len(filtered)} matching jobs from {len(all_jobs)} total")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Jobs Found", len(filtered))
            m2.metric("Best Match", f"{best_score}%")
            m3.metric("🔥 High Priority", high_count)
            m4.metric("Applications", len(st.session_state.applied_jobs))

            # Export
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                csv_data = export_jobs_csv(filtered)
                st.download_button(
                    "📥 Export results CSV", csv_data,
                    "careeros_results.csv", "text/csv",
                )
            with exp_col2:
                if st.session_state.applied_jobs:
                    app_csv = export_applied_csv()
                    st.download_button(
                        "📥 Export applications CSV", app_csv,
                        "careeros_applications.csv", "text/csv",
                    )

            st.divider()
            st.header("🎯 Recommended Jobs")

            # Pagination
            total = len(filtered)
            page_idx = st.session_state.page_index
            start = 0
            end = min((page_idx + 1) * JOBS_PER_PAGE, total)

            applied_urls = get_applied_urls()

            for idx, job in enumerate(filtered[start:end]):
                match = job["_match"]
                s = match["score"]
                title = job.get("title", "Unknown")
                company = safe_company_name(job.get("company", {}))
                job_loc = job.get("location", {}).get("display_name", "N/A")
                source = job.get("source", "N/A")
                salary = job.get("salary_text", "")
                desc = clean_html_text(job.get("description", ""))
                link = job.get("redirect_url", "")

                if s >= 70:
                    priority = "🔥 HIGH PRIORITY"
                elif s >= 45:
                    priority = "🟡 POSSIBLE MATCH"
                else:
                    priority = "⚪ LOW PRIORITY"

                is_applied = link in applied_urls

                with st.container(border=True):
                    header_col, badge_col = st.columns([4, 1])
                    with header_col:
                        st.subheader(f"{start + idx + 1}. {title}")
                    with badge_col:
                        if is_applied:
                            st.write("✅ **Applied**")

                    st.write(f"**{priority} — Match: {s}%**")
                    st.progress(s / 100)

                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"🏢 **Company:** {company}")
                        st.write(f"📍 **Location:** {job_loc}")
                    with c2:
                        st.write(f"🌐 **Source:** {source}")
                        st.write(
                            f"💰 **Salary:** {salary}" if salary
                            else "💰 **Salary:** Not specified"
                        )

                    if match["reasons"]:
                        with st.expander("✅ Why this matches", expanded=False):
                            for r in match["reasons"]:
                                st.success(f"✓ {r}")

                    if match["warnings"]:
                        with st.expander("⚠️ Check before applying", expanded=False):
                            for w in match["warnings"]:
                                st.warning(f"⚠ {w}")

                    if desc:
                        with st.expander("📄 Job description"):
                            st.write(desc[:1200])

                    # Dimension breakdown
                    with st.expander("📊 Score breakdown"):
                        dim_cols = st.columns(4)
                        dim_names = {
                            "location": "📍 Location",
                            "arabic": "🗣️ Arabic",
                            "english": "🇬🇧 English",
                            "skills": "💼 Skills",
                            "experience": "🧑‍💼 Experience",
                            "education": "🎓 Education",
                            "salary": "💰 Salary",
                            "relevance": "🌐 Relevance",
                        }
                        dim_maxes = {
                            "location": 20, "arabic": 15, "english": 10,
                            "skills": 25, "experience": 10, "education": 5,
                            "salary": 10, "relevance": 5,
                        }
                        for i, (dk, dv) in enumerate(match.get("dimensions", {}).items()):
                            col = dim_cols[i % 4]
                            label = dim_names.get(dk, dk)
                            mx = dim_maxes.get(dk, 10)
                            col.metric(label, f"{dv}/{mx}")

                    # Action buttons
                    btn1, btn2, btn3 = st.columns([1, 1, 1])
                    if valid_url(link):
                        with btn1:
                            st.link_button("📩 View & Apply", link)

                    with btn2:
                        if not is_applied:
                            if st.button(
                                "✅ Mark applied",
                                key=f"apply_{idx}_{hash(link or str(idx))}",
                            ):
                                mark_applied(link, title, company)
                                st.toast(f"✅ Marked: {title}")
                                st.rerun()
                        else:
                            st.write("✅ Already tracked")

                    with btn3:
                        if CLAUDE_API_KEY:
                            if st.button(
                                "🤖 Analyze with Claude",
                                key=f"claude_{idx}_{hash(link or str(idx))}",
                            ):
                                with st.spinner("Analyzing..."):
                                    analysis = analyze_with_claude(job, match)
                                st.info(analysis)

            # Load More button
            if end < total:
                remaining = total - end
                if st.button(f"📄 Load more ({remaining} remaining)"):
                    st.session_state.page_index += 1
                    st.rerun()

            st.caption(f"Showing {end} of {total} jobs")

# =========================================================
# APPLICATION TRACKER TAB
# =========================================================
if st.session_state.applied_jobs:
    st.divider()
    st.header("📋 Application Tracker")

    for url, data in st.session_state.applied_jobs.items():
        with st.container(border=True):
            tc1, tc2, tc3 = st.columns([3, 1, 1])
            with tc1:
                st.write(f"**{data.get('title', 'Unknown')}** — {data.get('company', '')}")
            with tc2:
                st.write(f"📅 {data.get('date', '')}")
            with tc3:
                st.write(f"📌 {data.get('status', 'Applied')}")

# =========================================================
# PROFILE SECTION
# =========================================================
st.divider()
with st.expander("🎯 Your Job Search Profile"):
    st.write(f"**Candidate:** {PROFILE['name']}")
    st.write(f"📍 **Location:** {PROFILE['location']}, {PROFILE['country']}")
    st.write(f"🗣️ **Languages:** Arabic / English / Romanian ({PROFILE['romanian_level']})")
    st.write(f"🎓 **Education:** {PROFILE['education']}")
    st.write(f"💼 **Experience:** {PROFILE['experience_years']}+ years")
    st.write(
        f"💰 **Target Salary:** "
        f"{PROFILE['target_salary_min']:,} – "
        f"{PROFILE['target_salary_max']:,} RON"
    )

st.info(
    "Next phase: AI-powered CV tailoring, "
    "cover letter generation, "
    "follow-up reminders."
)

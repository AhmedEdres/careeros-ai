import streamlit as st
import requests
import re
import html
import unicodedata
import csv
import io
import json
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher

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
# AHMED PROFILE
# =========================================================
PROFILE = {
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

# Expanded keyword groups for smarter matching
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
        "words": ["sap", "erp", "excel", "microsoft excel", "sql", "ibm cognos", "power bi"],
        "weight": 8,
        "label": "Tools (SAP / ERP / Excel / SQL)",
    },
}

# Romanian requirement patterns (expanded)
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

# Negative keywords — jobs that almost never fit
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


def fuzzy_similar(a: str, b: str, threshold: float = 0.85) -> bool:
    """Check if two strings are fuzzy-similar."""
    if not a or not b:
        return False
    return SequenceMatcher(None, a, b).ratio() >= threshold


# =========================================================
# JOOBLE — PRIMARY ROMANIA SOURCE
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def search_jooble_jobs(
    keywords: str,
    location: str,
    results_per_page: int = 20,
    pages: int = 2,
) -> Tuple[List[Dict], Optional[str]]:
    """
    Search Jooble with multi-page support for broader coverage.
    POST https://jooble.org/api/{api_key}
    """
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
        "User-Agent": "Ahmed-CareerOS/1.0",
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
                return [], (
                    "Jooble rejected the API key (HTTP 401). "
                    "Check JOOBLE_API_KEY in Streamlit Secrets."
                )
            if response.status_code == 403:
                return [], (
                    "Jooble denied access (HTTP 403). "
                    "The API key may be invalid or inactive."
                )
            if response.status_code == 404:
                return [], (
                    "Jooble endpoint not found (HTTP 404). "
                    "Check the API key."
                )
            if response.status_code != 200:
                body_preview = clean_html_text(response.text)[:250]
                return [], (
                    f"Jooble returned HTTP {response.status_code}. "
                    f"Response: {body_preview}"
                )

            data = response.json()
            jooble_jobs = data.get("jobs", [])

            if not isinstance(jooble_jobs, list):
                return all_jobs or [], "Jooble returned an unexpected format."

            if not jooble_jobs:
                break  # No more pages

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
            return [], f"Connection error while contacting Jooble: {error}"
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
) -> Tuple[List[Dict], Optional[str]]:
    """Remotive public API. No key required."""

    url = "https://remotive.com/api/remote-jobs"
    headers = {
        "User-Agent": "Ahmed-CareerOS/1.0",
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
# ADZUNA — OPTIONAL INTERNATIONAL SOURCE
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def search_adzuna_jobs(
    keywords: str,
    location: str,
    results_per_page: int = 20,
) -> Tuple[List[Dict], Optional[str]]:

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return [], "Adzuna credentials are not configured."

    if is_romania_location(location):
        return [], "Adzuna skipped for Romania; using Jooble as primary."

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
        "User-Agent": "Ahmed-CareerOS/1.0",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=25)

        if response.status_code != 200:
            return [], f"Adzuna returned HTTP {response.status_code}."

        data = response.json()
        results = data.get("results", [])
        normalized_jobs: List[Dict] = []

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

            normalized_jobs.append({
                "title": job.get("title", "Job title not available"),
                "company": {"display_name": safe_company_name(job.get("company", {}))},
                "location": {"display_name": display_loc},
                "description": job.get("description", ""),
                "redirect_url": job.get("redirect_url", ""),
                "salary_text": (
                    f"{job.get('salary_min')} - {job.get('salary_max')}"
                    if job.get("salary_min") is not None
                    else ""
                ),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "source": "Adzuna",
                "category": {"label": display_cat},
            })

        return normalized_jobs, None

    except requests.exceptions.Timeout:
        return [], "Adzuna request timed out."
    except requests.exceptions.RequestException as error:
        return [], f"Adzuna connection error: {error}"
    except ValueError:
        return [], "Adzuna returned invalid JSON."


# =========================================================
# DEDUPLICATION (fuzzy-aware)
# =========================================================
def remove_duplicate_jobs(jobs: List[Dict]) -> List[Dict]:
    unique: List[Dict] = []
    seen_urls: set = set()
    seen_titles: List[str] = []

    for job in jobs:
        title = normalize_text(job.get("title", ""))
        company = normalize_text(safe_company_name(job.get("company", {})))
        link = str(job.get("redirect_url", "") or "").strip().lower()

        # URL-based dedup
        if link:
            # Strip tracking params for better dedup
            clean_link = re.sub(r"[?&](utm_\w+|ref|source|medium)=[^&]*", "", link)
            if clean_link in seen_urls:
                continue
            seen_urls.add(clean_link)

        # Title+company fuzzy dedup
        combined = f"{title}|{company}"
        if any(fuzzy_similar(combined, seen) for seen in seen_titles):
            continue
        seen_titles.append(combined)

        unique.append(job)

    return unique


# =========================================================
# MATCHING ENGINE — Weighted Multi-Dimensional
# =========================================================
def calculate_match(job: Dict) -> Dict:
    """
    Weighted scoring across 8 dimensions.
    Returns dict with: score (0-100), reasons, warnings, dimensions.

    Dimension weights (total = 100):
      Location:     20
      Arabic:       15
      English:      10
      Skills:       25
      Experience:   10
      Education:     5
      Salary:       10
      Relevance:     5
    """
    title = job.get("title", "")
    description = job.get("description", "")
    company = safe_company_name(job.get("company", {}))
    category = job.get("category", {}).get("label", "")
    location_text = job.get("location", {}).get("display_name", "")
    salary_text = job.get("salary_text", "")
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")

    text = normalize_text(f"{title} {description} {company} {category}")
    title_norm = normalize_text(title)
    loc_norm = normalize_text(location_text)

    dims = {}
    reasons = []
    warnings = []
    score = 0

    # ----- 1. LOCATION (max 20) -----
    loc_score = 0
    if "timisoara" in loc_norm or "timișoara" in loc_norm:
        loc_score = 20
        reasons.append("📍 Location: Timișoara — perfect match")
    elif "romania" in loc_norm:
        loc_score = 15
        reasons.append("🇷🇴 Location: Romania")
    elif "remote" in loc_norm:
        loc_score = 12
        reasons.append("🏠 Location: Remote")
    elif any(c in loc_norm for c in ["europe", "europa", "eu"]):
        loc_score = 8
        reasons.append("🌍 Location: Europe")
    else:
        loc_score = 3
    score += loc_score
    dims["location"] = loc_score

    # ----- 2. ARABIC LANGUAGE (max 15) -----
    arabic_score = 0
    arabic_indicators = ["arabic", "arabe", "arabă", "limba araba"]
    if any(w in text for w in arabic_indicators):
        arabic_score = 15
        reasons.append("🗣️ Arabic language required — strong match")
    else:
        arabic_score = 2  # Not a negative, just not a boost
    score += arabic_score
    dims["arabic"] = arabic_score

    # ----- 3. ENGLISH LANGUAGE (max 10) -----
    eng_score = 0
    if "english" in text or "engleza" in text or "limba engleza" in text:
        eng_score = 10
        reasons.append("🇬🇧 English language required — matches your profile")
    else:
        eng_score = 4  # Most international roles assume English
    score += eng_score
    dims["english"] = eng_score

    # ----- 4. SKILLS MATCH (max 25) -----
    skill_score = 0
    matched_groups = []

    for group_name, group_data in SKILL_GROUPS.items():
        if any(w in text for w in group_data["words"]):
            skill_score += group_data["weight"]
            matched_groups.append(group_data["label"])

    skill_score = min(skill_score, 25)

    if matched_groups:
        reasons.append(
            f"💼 Skills match: {', '.join(matched_groups[:3])} ({skill_score}/25)"
        )
    else:
        reasons.append("💼 Skills: no direct keyword match")

    score += skill_score
    dims["skills"] = skill_score

    # ----- 5. EXPERIENCE LEVEL (max 10) -----
    exp_score = 0
    if re.search(r"\b(?:senior|lead|manager|director|head of)\b", title_norm):
        exp_score = 10
        reasons.append("🧑‍💼 Senior/leadership role — fits 10+ years experience")
    elif re.search(r"\b(?:mid|intermediate|specialist)\b", title_norm):
        exp_score = 8
        reasons.append("🧑‍💼 Mid-level role — good fit")
    elif re.search(r"\b(?:junior|entry|intern|trainee|graduate)\b", title_norm):
        exp_score = 4
        reasons.append("🧑‍💼 Entry-level — may be below your experience")
    else:
        exp_score = 6
    score += exp_score
    dims["experience"] = exp_score

    # ----- 6. EDUCATION (max 5) -----
    edu_score = 0
    if any(w in text for w in ["law", "legal", "juridic", "master"]):
        edu_score = 5
        reasons.append("🎓 Education: aligns with your Law degree")
    else:
        edu_score = 3
    score += edu_score
    dims["education"] = edu_score

    # ----- 7. SALARY (max 10) -----
    salary_score = 0
    if salary_min is not None and isinstance(salary_min, (int, float)):
        if salary_min >= PROFILE["target_salary_min"]:
            salary_score = 10
            reasons.append(f"💰 Salary meets target ({salary_min:,.0f}+)")
        elif salary_min >= PROFILE["target_salary_min"] * 0.8:
            salary_score = 7
            reasons.append(f"💰 Salary close to target ({salary_min:,.0f})")
        else:
            salary_score = 2
    else:
        salary_score = 5  # Unknown salary — neutral
    score += salary_score
    dims["salary"] = salary_score

    # ----- 8. GENERAL RELEVANCE (max 5) -----
    relevance_score = 0
    # Boost for BPO / shared services / multilingual roles
    relevance_indicators = [
        "multilingual", "multi-lingual", "bilingual",
        "bpo", "shared service", "outsourcing",
        "middle east", "mena", "gulf",
    ]
    if any(w in text for w in relevance_indicators):
        relevance_score = 5
        reasons.append("🌐 Multilingual / BPO / MENA relevance")
    else:
        relevance_score = 2
    score += relevance_score
    dims["relevance"] = relevance_score

    # ===== PENALTIES =====

    # Romanian requirement penalty
    if any(normalize_text(p) in text for p in ROMANIAN_PATTERNS_HIGH):
        score -= 15
        warnings.append(
            "⚠️ Requires advanced Romanian (C1/C2/fluent) — "
            "does not match your Beginner level"
        )
    elif any(normalize_text(p) in text for p in ROMANIAN_PATTERNS_ANY):
        score -= 8
        warnings.append(
            "⚠️ Romanian language may be required — check the listing"
        )

    # Remote geographic restriction
    restricted_regions = [
        "united states", "usa only", "us only",
        "canada only", "uk only", "india only",
        "us-based", "us based",
    ]
    if "remote" in loc_norm and any(r in loc_norm for r in restricted_regions):
        score -= 10
        warnings.append(
            "🌍 Remote but geographically restricted — "
            "verify Romania is eligible"
        )

    # Negative keyword penalty (clearly irrelevant roles)
    if any(nk in title_norm for nk in NEGATIVE_KEYWORDS):
        score -= 20
        warnings.append(
            "🚫 Role title suggests a different career track"
        )

    score = max(0, min(100, score))

    return {
        "score": score,
        "reasons": reasons,
        "warnings": warnings,
        "dimensions": dims,
    }


# =========================================================
# CLAUDE AI ANALYSIS (optional)
# =========================================================
def analyze_with_claude(job: Dict) -> str:
    if not CLAUDE_API_KEY:
        return "⚠️ Claude API key not configured. Add CLAUDE_API_KEY to Secrets."

    title = job.get("title", "Unknown")
    company = safe_company_name(job.get("company", {}))
    location = job.get("location", {}).get("display_name", "Unknown")
    description = clean_html_text(job.get("description", ""))[:1500]
    salary = job.get("salary_text", "Not specified")

    prompt = f"""You are a career advisor. Analyze this job for Ahmed.

Ahmed's profile:
- 10 years in operations, client management, financial compliance, tax, accounting, support
- Languages: Arabic (native), English (fluent), Romanian (beginner)
- Education: Master's in Law
- Location: Timișoara, Romania
- Target salary: 5,000–7,000 RON

Job details:
Title: {title}
Company: {company}
Location: {location}
Salary: {salary}
Description: {description}

Provide:
1. Match percentage (0-100%) with brief justification
2. Top 3 strengths for Ahmed
3. Top 3 risks or challenges
4. Recommendation: Apply or Skip? Why?

Be concise and practical."""

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except ImportError:
        return "❌ anthropic package not installed. Add it to requirements.txt."
    except Exception as e:
        return f"❌ Claude analysis failed: {e}"


# =========================================================
# MULTI-QUERY SEARCH — Run multiple keyword variations
# =========================================================
def build_search_queries(base_keywords: str) -> List[str]:
    """Generate keyword variations for broader coverage."""
    queries = [base_keywords.strip()]

    # Add common variations if the base is generic
    base_lower = base_keywords.lower().strip()

    expansions = {
        "customer support": [
            "customer service",
            "arabic customer support",
            "english customer support",
        ],
        "customer service": [
            "customer support",
            "arabic customer service",
        ],
        "operations": [
            "operations coordinator",
            "operations specialist",
            "back office operations",
        ],
        "accounting": [
            "accounts payable",
            "accounts receivable",
            "bookkeeper",
        ],
        "finance": [
            "financial operations",
            "financial compliance",
            "financial analyst",
        ],
    }

    for key, extras in expansions.items():
        if key in base_lower:
            queries.extend(extras)
            break

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for q in queries:
        if q.lower() not in seen:
            seen.add(q.lower())
            unique.append(q)

    return unique[:4]  # Cap at 4 queries to be reasonable


# =========================================================
# PARALLEL SEARCH ORCHESTRATOR
# =========================================================
def run_parallel_search(
    keywords: str,
    location: str,
    max_results: int,
    use_jooble: bool,
    use_remotive: bool,
    use_adzuna: bool,
    expand_queries: bool,
) -> Tuple[List[Dict], List[str], List[str]]:
    """
    Run all selected sources in parallel, with optional query expansion.
    Returns: (all_jobs, source_counts, errors)
    """
    all_jobs: List[Dict] = []
    errors: List[str] = []
    source_counts: List[str] = []

    queries = build_search_queries(keywords) if expand_queries else [keywords]

    tasks = []
    for query in queries:
        if use_jooble:
            tasks.append(("Jooble", search_jooble_jobs, (query, location, max_results, 1)))
        if use_remotive:
            tasks.append(("Remotive", search_remotive_jobs, (query, max_results)))
        if use_adzuna:
            tasks.append(("Adzuna", search_adzuna_jobs, (query, location, max_results)))

    if not tasks:
        return [], [], ["No search sources selected."]

    source_job_counts = {}

    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_info = {
            executor.submit(func, *args): (name, args[0])
            for name, func, args in tasks
        }

        for future in as_completed(future_to_info):
            source_name, query_used = future_to_info[future]
            try:
                jobs, err = future.result()
                if err:
                    if "skipped for Romania" not in str(err):
                        errors.append(f"{source_name}: {err}")
                else:
                    all_jobs.extend(jobs)
                    source_job_counts[source_name] = (
                        source_job_counts.get(source_name, 0) + len(jobs)
                    )
            except Exception as e:
                errors.append(f"{source_name}: {e}")

    for src, count in source_job_counts.items():
        source_counts.append(f"{src}: {count}")

    return all_jobs, source_counts, errors


# =========================================================
# EXPORT TO CSV
# =========================================================
def export_jobs_csv(jobs: List[Dict]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Title", "Company", "Location", "Source",
        "Match %", "Salary", "Link", "Warnings",
    ])
    for idx, job in enumerate(jobs):
        match = job.get("_match", {})
        writer.writerow([
            idx + 1,
            job.get("title", ""),
            safe_company_name(job.get("company", {})),
            job.get("location", {}).get("display_name", ""),
            job.get("source", ""),
            match.get("score", 0),
            job.get("salary_text", ""),
            job.get("redirect_url", ""),
            "; ".join(match.get("warnings", [])),
        ])
    return output.getvalue()


# =========================================================
# STREAMLIT UI
# =========================================================
st.title("🎯 CareerOS AI")
st.subheader("AI-Powered Job Search & Application Assistant")
st.write(
    "Search Romanian and remote jobs, combine multiple sources, "
    "rank them against your profile, and apply directly."
)

# =========================================================
# SESSION STATE
# =========================================================
if "applied_jobs" not in st.session_state:
    st.session_state.applied_jobs = set()
if "search_results" not in st.session_state:
    st.session_state.search_results = []

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
        "🔄 Expand search queries",
        value=True,
        help="Automatically search related keyword variations for broader coverage",
    )

    location_filter = st.selectbox(
        "Location filter",
        ["All", "Timișoara", "Romania", "Remote", "Europe"],
        index=0,
    )

    min_match = st.slider("Minimum match %", 0, 100, 40, 5)

    romanian_filter = st.radio(
        "Romanian requirement",
        ["Any", "Exclude Romanian-required", "Allow beginner-friendly"],
        index=0,
    )

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
# SEARCH
# =========================================================
st.divider()

if st.button("🔎 Search Jobs", type="primary"):

    with st.status("Searching across sources...", expanded=True) as status:
        all_jobs, source_counts, search_errors = run_parallel_search(
            keywords=keywords,
            location=location,
            max_results=max_results,
            use_jooble=search_jooble,
            use_remotive=search_remote,
            use_adzuna=search_adzuna,
            expand_queries=expand_queries,
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
        # Score all jobs
        scored_jobs = []
        for job in all_jobs:
            match = calculate_match(job)
            job["_match"] = match
            scored_jobs.append(job)

        # Apply filters
        filtered = []
        for job in scored_jobs:
            match = job["_match"]
            s = match["score"]

            # Min match filter
            if s < min_match:
                continue

            # Location filter
            loc = normalize_text(
                job.get("location", {}).get("display_name", "")
            )
            if location_filter == "Timișoara" and "timisoara" not in loc:
                continue
            elif location_filter == "Romania" and "romania" not in loc:
                continue
            elif location_filter == "Remote" and "remote" not in loc:
                continue
            elif location_filter == "Europe" and not any(
                x in loc for x in [
                    "europe", "europa", "germany", "france",
                    "spain", "italy", "romania", "timisoara",
                ]
            ):
                continue

            # Romanian filter
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

        # Sort by score
        filtered.sort(key=lambda j: j["_match"]["score"], reverse=True)

        # Store in session
        st.session_state.search_results = filtered

        if not filtered:
            st.warning(
                f"No jobs passed your filters (min match {min_match}%). "
                "Try lowering the minimum or changing filters."
            )
        else:
            # Dashboard metrics
            best_score = filtered[0]["_match"]["score"]
            high_count = sum(1 for j in filtered if j["_match"]["score"] >= 70)

            st.success(f"Found {len(filtered)} matching jobs from {len(all_jobs)} total")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Jobs Found", len(filtered))
            m2.metric("Best Match", f"{best_score}%")
            m3.metric("🔥 High Priority", high_count)
            m4.metric("Applications", len(st.session_state.applied_jobs))

            # Export button
            csv_data = export_jobs_csv(filtered)
            st.download_button(
                "📥 Export results to CSV",
                csv_data,
                "careeros_results.csv",
                "text/csv",
            )

            # Claude analysis button
            if CLAUDE_API_KEY:
                analyze_top = st.checkbox("🤖 Analyze top 5 with Claude AI")
            else:
                analyze_top = False

            st.divider()
            st.header("🎯 Recommended Jobs")

            # Display jobs
            for idx, job in enumerate(filtered[:30]):
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

                with st.container(border=True):
                    st.subheader(f"{idx + 1}. {title}")
                    st.write(f"**{priority} — Match: {s}%**")
                    st.progress(s / 100)

                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.write(f"🏢 **Company:** {company}")
                        st.write(f"📍 **Location:** {job_loc}")
                    with col_info2:
                        st.write(f"🌐 **Source:** {source}")
                        st.write(
                            f"💰 **Salary:** {salary}"
                            if salary
                            else "💰 **Salary:** Not specified"
                        )

                    # Match reasons
                    if match["reasons"]:
                        with st.expander("✅ Why this matches", expanded=False):
                            for r in match["reasons"]:
                                st.success(f"✓ {r}")

                    # Warnings
                    if match["warnings"]:
                        with st.expander("⚠️ Check before applying", expanded=False):
                            for w in match["warnings"]:
                                st.warning(f"⚠ {w}")

                    # Description preview
                    if desc:
                        with st.expander("📄 Job description preview"):
                            st.write(desc[:900])

                    # Action buttons
                    btn_col1, btn_col2 = st.columns([1, 1])
                    if valid_url(link):
                        with btn_col1:
                            st.link_button("📩 View & Apply", link)
                    with btn_col2:
                        job_id = job.get("redirect_url", str(idx))
                        if job_id in st.session_state.applied_jobs:
                            st.write("✅ Applied")
                        else:
                            if st.button(
                                "✅ Mark as applied",
                                key=f"apply_{idx}_{hash(job_id)}",
                            ):
                                st.session_state.applied_jobs.add(job_id)
                                st.rerun()

                    # Claude analysis
                    if analyze_top and idx < 5:
                        with st.spinner(f"Analyzing with Claude..."):
                            analysis = analyze_with_claude(job)
                        st.info(analysis)

# =========================================================
# PROFILE SECTION
# =========================================================
st.divider()
st.header("🎯 Your Job Search Profile")
st.write(f"**Candidate:** {PROFILE['name']}")
st.write(f"📍 **Location:** {PROFILE['location']}, {PROFILE['country']}")
st.write("🗣️ **Languages:** Arabic / English / Romanian (Beginner)")
st.write(f"🎓 **Education:** {PROFILE['education']}")
st.write(f"💼 **Experience:** {PROFILE['experience_years']}+ years")
st.write(
    f"💰 **Target Salary:** "
    f"{PROFILE['target_salary_min']:,} – "
    f"{PROFILE['target_salary_max']:,} RON"
)
st.info(
    "Next phase: AI job analysis, CV matching, "
    "tailored CV versions, cover letters, "
    "application tracking and follow-up reminders."
)

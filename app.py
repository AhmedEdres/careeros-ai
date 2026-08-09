import streamlit as st
import requests
import time
import re
import html
import unicodedata

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Careeros AI",
    page_icon="🎯",
    layout="wide"
)

# =========================================================
# API SETTINGS
# =========================================================

ADZUNA_APP_ID = st.secrets.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = st.secrets.get("ADZUNA_APP_KEY", "")
JOOBLE_API_KEY = st.secrets.get("JOOBLE_API_KEY", "")
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
        "operations",
        "client management",
        "financial compliance",
        "customer service",
        "customer support",
        "excel",
        "sap",
        "erp",
        "sql",
        "administration",
        "logistics",
        "arabic",
        "english"
    ],
    "target_salary_min": 5000,
    "target_salary_max": 7000
}

# =========================================================
# TEXT HELPERS
# =========================================================

def normalize_text(text):
    """
    Converts text to lowercase and removes Romanian accents.
    Example: Timișoara becomes timisoara.
    """
    text = str(text or "")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    return text.lower()


def clean_html_text(text):
    """
    Removes HTML from job descriptions and makes them readable.
    """
    text = html.unescape(str(text or ""))
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_company_name(company):
    """
    Jooble usually gives a company name as text.
    This also handles unexpected dictionary values safely.
    """
    if isinstance(company, dict):
        return company.get("display_name", "Company not listed")

    return str(company or "Company not listed")


# =========================
# ADZUNA SEARCH
# =========================

def search_jobs(keywords, location, results_per_page=20):

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return None, "Adzuna API credentials are missing. Check Streamlit Secrets."

    url = "https://api.adzuna.com/v1/api/jobs/ro/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": keywords,
        "where": location,
        "content-type": "application/json",
        "sort_by": "date"
    }

    headers = {
        "User-Agent": "Ahmed-CareerOS/1.0",
        "Accept": "application/json"
    }

    for attempt in range(3):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=25
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("results", []), None

            if response.status_code == 401:
                return None, (
                    "Adzuna rejected the App ID/API Key (HTTP 401). "
                    "Check ADZUNA_APP_ID and ADZUNA_APP_KEY in Streamlit Secrets."
                )

            if response.status_code == 403:
                return None, (
                    "Adzuna denied access (HTTP 403). "
                    "Check that the API account/key is active."
                )

            if response.status_code == 503:
                if attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue
                return None, (
                    "Adzuna is temporarily unavailable (HTTP 503). "
                    "Please wait a few minutes and try Search Jobs again."
                )

            return None, f"Adzuna returned HTTP {response.status_code}."

        except requests.exceptions.Timeout:
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            return None, "The request to Adzuna timed out. Please try again."

        except requests.exceptions.RequestException as e:
            return None, f"Connection error while contacting Adzuna: {e}"

    return None, "Adzuna search failed after several attempts."

# =========================================================
# JOOBLE: ROMANIA JOB SEARCH
# =========================================================

def search_jooble_jobs(keywords, location, results_per_page=20):
    """
    Search Jooble for Romania / Timișoara jobs.

    Results are converted into one common CareerOS format,
    so Jooble and Remotive jobs can be displayed together.
    """

    if not JOOBLE_API_KEY:
        return [], (
            "Jooble API key is missing. "
            "Add JOOBLE_API_KEY to Streamlit Secrets."
        )

    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"

    payload = {
        "keywords": keywords,
        "location": location
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Ahmed-CareerOS/1.0"
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 401:
            return [], (
                "Jooble rejected the API key (HTTP 401). "
                "Check JOOBLE_API_KEY in Streamlit Secrets."
            )

        if response.status_code == 403:
            return [], (
                "Jooble denied access (HTTP 403). "
                "Check your Jooble API account."
            )

        if response.status_code != 200:
            return [], (
                f"Jooble returned HTTP {response.status_code}. "
                "Please try again later."
            )

        data = response.json()
        jooble_jobs = data.get("jobs", [])

        normalized_jobs = []

        for job in jooble_jobs[:results_per_page]:

            company_name = safe_company_name(
                job.get("company", "Company not listed")
            )

            title = job.get("title", "Job title not available")
            job_location = job.get("location", location)
            description = job.get("snippet", "")
            link = job.get("link", "")

            # Jooble sometimes provides salary as text.
            salary_text = job.get("salary", "")

            normalized_jobs.append({
                "title": title,
                "company": {
                    "display_name": company_name
                },
                "location": {
                    "display_name": job_location
                },
                "description": description,
                "redirect_url": link,
                "salary_text": salary_text,
                "salary_min": None,
                "salary_max": None,
                "source": "Jooble Romania",
                "category": {
                    "label": ""
                }
            })

        return normalized_jobs, None

    except requests.exceptions.Timeout:
        return [], "Jooble request timed out. Please try again."

    except requests.exceptions.RequestException as error:
        return [], f"Connection error while contacting Jooble: {error}"

    except ValueError:
        return [], "Jooble returned an invalid response."


# =========================================================
# REMOTIVE: REMOTE JOB SEARCH
# =========================================================

def search_remotive_jobs(keywords, results_per_page=20):
    """
    Search remote jobs from Remotive.

    No API key is required for Remotive.
    Jobs are filtered locally based on the entered keywords.
    """

    url = "https://remotive.com/api/remote-jobs"

    headers = {
        "User-Agent": "Ahmed-CareerOS/1.0",
        "Accept": "application/json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            return [], (
                f"Remotive returned HTTP {response.status_code}. "
                "Please try again later."
            )

        data = response.json()
        remotive_jobs = data.get("jobs", [])

        # Extract useful words from the search text.
        # Example: "arabic customer support"
        # becomes: ["arabic", "customer", "support"]
        search_words = [
            word.lower()
            for word in re.findall(r"[a-zA-Z]+", keywords)
            if len(word) >= 3
        ]

        normalized_jobs = []

        for job in remotive_jobs:

            title = job.get("title", "")
            company = job.get("company_name", "")
            description = job.get("description", "")
            category = job.get("category", "")
            candidate_location = job.get(
                "candidate_required_location",
                "Remote"
            )

            searchable_text = normalize_text(
                f"{title} {company} {description} {category}"
            )

            # Show a job when it matches at least one keyword.
            # This gives wider results than requiring every word.
            if search_words:
                if not any(
                    word in searchable_text
                    for word in search_words
                ):
                    continue

            normalized_jobs.append({
                "title": title or "Job title not available",
                "company": {
                    "display_name": company or "Company not listed"
                },
                "location": {
                    "display_name": f"Remote — {candidate_location}"
                },
                "description": description,
                "redirect_url": job.get("url", ""),
                "salary_text": job.get("salary", ""),
                "salary_min": None,
                "salary_max": None,
                "source": "Remotive",
                "category": {
                    "label": category
                }
            })

            if len(normalized_jobs) >= results_per_page:
                break

        return normalized_jobs, None

    except requests.exceptions.Timeout:
        return [], "Remotive request timed out. Please try again."

    except requests.exceptions.RequestException as error:
        return [], f"Connection error while contacting Remotive: {error}"

    except ValueError:
        return [], "Remotive returned an invalid response."


# =========================================================
# REMOVE DUPLICATE JOBS
# =========================================================

def remove_duplicate_jobs(jobs):
    """
    Removes duplicate jobs using normalized title + company.
    """

    unique_jobs = []
    seen_jobs = set()

    for job in jobs:
        title = normalize_text(job.get("title", ""))
        company = normalize_text(
            job.get("company", {}).get("display_name", "")
        )

        job_key = f"{title}|{company}"

        if job_key not in seen_jobs:
            seen_jobs.add(job_key)
            unique_jobs.append(job)

    return unique_jobs


# =========================================================
# MATCHING ENGINE
# =========================================================

def calculate_match(job):
    """
    Score each job against Ahmed's profile.
    Returns score, strengths and warnings.
    """

    title = job.get("title", "")
    description = job.get("description", "")
    company = job.get("company", {}).get("display_name", "")
    category = job.get("category", {}).get("label", "")

    text = normalize_text(
        f"{title} {description} {company} {category}"
    )

    location_text = normalize_text(
        job.get("location", {}).get("display_name", "")
    )

    score = 0
    reasons = []
    warnings = []

    # Arabic is a high-value differentiator for Ahmed.
    if "arabic" in text or "araba" in text:
        score += 30
        reasons.append("Arabic language is explicitly relevant")

    # English.
    if "english" in text or "engleza" in text:
        score += 15
        reasons.append("English language is relevant")

    # Operations / customer support.
    operations_words = [
        "operations",
        "operational",
        "coordinator",
        "administrator",
        "back office",
        "customer support",
        "customer service",
        "customer care",
        "client service",
        "client support",
        "client management",
        "call center"
    ]

    if any(word in text for word in operations_words):
        score += 15
        reasons.append("Operations / customer-service relevance")

    # Financial / legal / compliance experience.
    finance_words = [
        "finance",
        "financial",
        "accounting",
        "accounts payable",
        "accounts receivable",
        "tax",
        "compliance",
        "invoice",
        "procurement",
        "legal",
        "audit",
        "banking",
        "collection"
    ]

    if any(word in text for word in finance_words):
        score += 15
        reasons.append("Finance / compliance / legal relevance")

    # Logistics / warehouse.
    logistics_words = [
        "logistics",
        "warehouse",
        "depot",
        "supply chain",
        "inventory",
        "transport",
        "purchasing"
    ]

    if any(word in text for word in logistics_words):
        score += 10
        reasons.append("Logistics / warehouse relevance")

    # Software skills.
    if "sap" in text:
        score += 10
        reasons.append("SAP relevance")

    if "erp" in text:
        score += 8
        reasons.append("ERP relevance")

    if "excel" in text:
        score += 5
        reasons.append("Excel relevance")

    # Location preference.
    if "timisoara" in location_text:
        score += 15
        reasons.append("Timișoara location")

    elif "remote" in location_text:
        score += 10
        reasons.append("Remote opportunity")

    # Romanian language warning.
    romanian_requirement_words = [
        "romanian fluent",
        "fluent romanian",
        "romanian language required",
        "romanian required",
        "limba romana",
        "romana avansat",
        "romanian c1",
        "romanian b2"
    ]

    if any(word in text for word in romanian_requirement_words):
        score -= 10
        warnings.append(
            "Romanian may be required at a higher level than Beginner"
        )

    # Remote eligibility warning.
    remote_location_words = [
        "united states",
        "usa only",
        "canada only",
        "uk only",
        "india only"
    ]

    if (
        "remote" in location_text
        and any(word in location_text for word in remote_location_words)
    ):
        score -= 10
        warnings.append(
            "Check if this remote job accepts applicants living in Romania"
        )

    score = max(0, min(score, 100))

    return score, reasons, warnings


# =========================================================
# PAGE HEADER
# =========================================================

st.title("🎯 Careeros AI")
st.subheader("AI-Powered Job Search & Application Assistant")

st.write(
    "Search Romanian and remote jobs, rank them against Ahmed's "
    "profile, and prepare high-quality applications."
)

# =========================================================
# SIDEBAR SETTINGS
# =========================================================

st.sidebar.header("⚙️ Search Settings")

location = st.sidebar.text_input(
    "Romania location",
    "Timisoara"
)

keywords = st.sidebar.text_input(
    "Keywords",
    "customer support"
)

max_results = st.sidebar.slider(
    "Number of results per source",
    min_value=5,
    max_value=50,
    value=20
)

search_remote = st.sidebar.checkbox(
    "Include Remote jobs (Remotive)",
    value=True
)

st.sidebar.divider()

st.sidebar.markdown("### 💡 Suggested searches")

st.sidebar.caption(
    """
Try one search at a time:

• arabic customer support  
• customer service english  
• operations specialist  
• back office  
• financial operations  
• accounts receivable  
• logistics coordinator  
• sap excel  
"""
)

# =========================================================
# SEARCH BUTTON
# =========================================================

st.divider()

if st.button("🔎 Search Jobs", type="primary"):

    all_jobs = []
    search_errors = []

    with st.spinner(
        "Searching Romania and Remote job listings..."
    ):

        # -------------------------
        # Jooble: Romania search
        # -------------------------

        jooble_jobs, jooble_error = search_jooble_jobs(
            keywords,
            location,
            max_results
        )

        if jooble_error:
            search_errors.append(f"Jooble: {jooble_error}")

        elif jooble_jobs:
            all_jobs.extend(jooble_jobs)

        # -------------------------
        # Remotive: Remote search
        # -------------------------

        if search_remote:

            remotive_jobs, remotive_error = search_remotive_jobs(
                keywords,
                max_results
            )

            if remotive_error:
                search_errors.append(
                    f"Remotive: {remotive_error}"
                )

            elif remotive_jobs:
                all_jobs.extend(remotive_jobs)

    # Do not stop if only one source has an error.
    for error_message in search_errors:
        st.warning(error_message)

    # Remove repeated advertisements.
    all_jobs = remove_duplicate_jobs(all_jobs)

    if not all_jobs:

        st.warning(
            "No jobs were found from the active sources. "
            "Try simpler keywords: customer support, operations, "
            "finance, logistics, Arabic, or English."
        )

    else:

        scored_jobs = []

        for job in all_jobs:

            score, reasons, warnings = calculate_match(job)

            job["_score"] = score
            job["_reasons"] = reasons
            job["_warnings"] = warnings

            scored_jobs.append(job)

        # Highest match first.
        scored_jobs.sort(
            key=lambda job: job["_score"],
            reverse=True
        )

        best_score = scored_jobs[0]["_score"]

        high_priority_count = len([
            job
            for job in scored_jobs
            if job["_score"] >= 70
        ])

        st.success(
            f"Found {len(scored_jobs)} unique jobs from active sources."
        )

        # =================================================
        # DASHBOARD METRICS
        # =================================================

        metric_1, metric_2, metric_3, metric_4 = st.columns(4)

        metric_1.metric("Jobs Found", len(scored_jobs))
        metric_2.metric("Best Match", f"{best_score}%")
        metric_3.metric("High Priority", high_priority_count)
        metric_4.metric("Applications", "0")

        st.divider()
        st.header("🎯 Recommended Jobs")

        # =================================================
        # DISPLAY JOBS
        # =================================================

        for index, job in enumerate(scored_jobs):

            title = job.get("title", "Unknown position")

            company = job.get(
                "company",
                {}
            ).get(
                "display_name",
                "Unknown company"
            )

            job_location = job.get(
                "location",
                {}
            ).get(
                "display_name",
                "Unknown location"
            )

            source = job.get("source", "Unknown source")
            score = job["_score"]
            reasons = job["_reasons"]
            warnings = job["_warnings"]

            description = clean_html_text(
                job.get("description", "")
            )

            salary_text = job.get("salary_text", "")
            link = job.get("redirect_url", "")

            if score >= 70:
                priority = "🔥 HIGH PRIORITY"
            elif score >= 45:
                priority = "🟡 POSSIBLE MATCH"
            else:
                priority = "⚪ LOW PRIORITY"

            with st.container(border=True):

                st.subheader(f"{index + 1}. {title}")

                st.write(
                    f"**{priority} — Match Score: {score}%**"
                )

                st.progress(score / 100)

                st.write(f"🏢 **Company:** {company}")
                st.write(f"📍 **Location:** {job_location}")
                st.write(f"🌐 **Source:** {source}")

                if salary_text:
                    st.write(f"💰 **Salary listed:** {salary_text}")
                else:
                    st.write("💰 **Salary:** Not specified")

                if reasons:

                    st.write("**Why this may match your profile:**")

                    for reason in reasons:
                        st.success(f"✓ {reason}")

                if warnings:

                    st.write("**Check before applying:**")

                    for warning in warnings:
                        st.warning(f"⚠ {warning}")

                if description:

                    st.write("**Job description preview:**")
                    st.write(description[:700])

                if link:

                    st.link_button(
                        "📩 View Original Job & Apply",
                        link
                    )

# =========================================================
# PROFILE SECTION
# =========================================================

st.divider()

st.header("🎯 Your Job Search Profile")

st.write(f"**Candidate:** {PROFILE['name']}")

st.write(
    f"📍 **Location:** {PROFILE['location']}, "
    f"{PROFILE['country']}"
)

st.write(
    "🗣️ **Languages:** Arabic / English / Romanian (Beginner)"
)

st.write(
    f"🎓 **Education:** {PROFILE['education']}"
)

st.write(
    f"💼 **Experience:** {PROFILE['experience_years']}+ years"
)

st.write(
    f"💰 **Target Salary:** "
    f"{PROFILE['target_salary_min']:,} – "
    f"{PROFILE['target_salary_max']:,} RON"
)

st.info(
    "Next planned features: CV matching, tailored CV versions, "
    "cover-letter generation, application tracking, and follow-up reminders."
)

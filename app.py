import streamlit as st
import requests
import re
import html
import unicodedata
from urllib.parse import urlparse

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
# IMPORTANT:
# Put the real values ONLY in Streamlit Secrets.
#
# [secrets.toml]
# ADZUNA_APP_ID = "your_id"
# ADZUNA_APP_KEY = "your_key"
# JOOBLE_API_KEY = "your_jooble_key"

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
        "english",
        "tax",
        "banking",
        "accounting",
    ],
    "target_salary_min": 5000,
    "target_salary_max": 7000,
}

# =========================================================
# TEXT HELPERS
# =========================================================
def normalize_text(text):
    text = str(text or "")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        c for c in text if not unicodedata.combining(c)
    )
    return text.lower()


def clean_html_text(text):
    text = html.unescape(str(text or ""))
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_company_name(company):
    if isinstance(company, dict):
        return str(company.get("display_name", "") or "Company not listed")
    return str(company or "Company not listed")


def normalize_location(location):
    """
    Jooble works better when the country is explicit.
    Example: Timisoara -> Timisoara, Romania
    """
    location = str(location or "").strip()

    if not location:
        return "Timisoara, Romania"

    normalized = normalize_text(location)

    if normalized in {
        "timisoara",
        "timisoara romania",
        "timis",
        "timis romania",
    }:
        return "Timisoara, Romania"

    if "romania" not in normalized and (
        "timisoara" in normalized or normalized == "timis"
    ):
        return f"{location}, Romania"

    return location


def is_romania_location(location):
    text = normalize_text(location)
    return (
        "romania" in text
        or "timisoara" in text
        or "bucharest" in text
        or "bucuresti" in text
    )


def valid_url(url):
    try:
        parsed = urlparse(str(url))
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


# =========================================================
# ADZUNA
# =========================================================
def search_adzuna_jobs(keywords, location, results_per_page=20):
    """
    Adzuna is kept as an optional source.

    Important:
    The Adzuna API uses country-specific endpoints. The current
    Romania workflow should not depend on Adzuna because the
    Romanian endpoint may return no data / may not be available
    for the account. Jooble is the primary Romania source.

    If the user searches a non-Romanian country where their
    Adzuna account supports the country code, this function can
    be used.
    """

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return [], "Adzuna credentials are not configured."

    # We intentionally skip Adzuna for Romanian searches.
    # This prevents a non-working Romania endpoint from making
    # the application look broken.
    if is_romania_location(location):
        return [], "Adzuna skipped for Romania; using Jooble as the primary local source."

    # Country code can be entered separately in the UI for future
    # international searches. For now this fallback uses gb.
    country_code = "gb"

    url = (
        f"https://api.adzuna.com/v1/api/jobs/"
        f"{country_code}/search/1"
    )

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
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=25,
        )

        if response.status_code != 200:
            return [], f"Adzuna returned HTTP {response.status_code}."

        data = response.json()
        results = data.get("results", [])

        normalized_jobs = []

        for job in results[:results_per_page]:
            normalized_jobs.append({
                "title": job.get("title", "Job title not available"),
                "company": {
                    "display_name": safe_company_name(
                        job.get("company", {})
                    )
                },
                "location": {
                    "display_name": job.get(
                        "location", {}
                    ).get(
                        "display_name",
                        location
                    )
                    if isinstance(job.get("location", {}), dict)
                    else str(job.get("location", location))
                },
                "description": job.get("description", ""),
                "redirect_url": job.get("redirect_url", ""),
                "salary_text": (
                    f"{job.get('salary_min')} - {job.get('salary_max')}"
                    if job.get("salary_min") is not None
                    or job.get("salary_max") is not None
                    else ""
                ),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "source": "Adzuna",
                "category": {
                    "label": safe_company_name(
                        job.get("category", {})
                    )
                    if isinstance(job.get("category", {}), dict)
                    else str(job.get("category", ""))
                },
            })

        return normalized_jobs, None

    except requests.exceptions.Timeout:
        return [], "Adzuna request timed out."
    except requests.exceptions.RequestException as error:
        return [], f"Adzuna connection error: {error}"
    except ValueError:
        return [], "Adzuna returned invalid JSON."


# =========================================================
# JOOBLE — PRIMARY ROMANIA SOURCE
# =========================================================
def search_jooble_jobs(keywords, location, results_per_page=20):
    """
    Jooble REST API.

    Official format:
    POST https://jooble.org/api/{api_key}

    Payload supports keywords, location, radius, page,
    ResultOnPage and companysearch.
    """

    if not JOOBLE_API_KEY:
        return [], (
            "Jooble API key is missing. "
            "Add JOOBLE_API_KEY to Streamlit Secrets."
        )

    search_location = normalize_location(location)

    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"

    payload = {
        "keywords": keywords.strip(),
        "location": search_location,
        "radius": "40",
        "page": "1",
        "ResultOnPage": str(results_per_page),
        "companysearch": "false",
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Ahmed-CareerOS/1.0",
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=35,
        )

        if response.status_code == 401:
            return [], (
                "Jooble rejected the API key (HTTP 401). "
                "Check JOOBLE_API_KEY in Streamlit Secrets."
            )

        if response.status_code == 403:
            return [], (
                "Jooble denied access (HTTP 403). "
                "The API key may be invalid, inactive, or restricted."
            )

        if response.status_code == 404:
            return [], (
                "Jooble endpoint was not found (HTTP 404). "
                "Check the API key and Jooble API account."
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
            return [], "Jooble returned an unexpected response format."

        normalized_jobs = []

        for job in jooble_jobs[:results_per_page]:
            if not isinstance(job, dict):
                continue

            company = safe_company_name(
                job.get("company", "Company not listed")
            )

            job_location = (
                job.get("location")
                or search_location
            )

            normalized_jobs.append({
                "title": job.get(
                    "title",
                    "Job title not available"
                ),
                "company": {
                    "display_name": company
                },
                "location": {
                    "display_name": str(job_location)
                },
                "description": job.get("snippet", ""),
                "redirect_url": job.get("link", ""),
                "salary_text": job.get("salary", ""),
                "salary_min": None,
                "salary_max": None,
                "source": (
                    f"Jooble"
                    + (
                        f" / {job.get('source')}"
                        if job.get("source")
                        else ""
                    )
                ),
                "category": {
                    "label": job.get("type", "")
                },
                "jooble_id": job.get("id"),
                "updated": job.get("updated", ""),
            })

        return normalized_jobs, None

    except requests.exceptions.Timeout:
        return [], "Jooble request timed out. Please try again."

    except requests.exceptions.RequestException as error:
        return [], f"Connection error while contacting Jooble: {error}"

    except ValueError:
        return [], "Jooble returned invalid JSON."


# =========================================================
# REMOTIVE
# =========================================================
def search_remotive_jobs(keywords, results_per_page=20):
    """
    Remotive is used for remote positions.
    No API key is required.
    """

    url = "https://remotive.com/api/remote-jobs"

    headers = {
        "User-Agent": "Ahmed-CareerOS/1.0",
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=35,
        )

        if response.status_code != 200:
            return [], (
                f"Remotive returned HTTP {response.status_code}."
            )

        data = response.json()
        remotive_jobs = data.get("jobs", [])

        search_words = [
            word.lower()
            for word in re.findall(
                r"[a-zA-Z]+",
                keywords
            )
            if len(word) >= 3
        ]

        normalized_jobs = []

        for job in remotive_jobs:
            if not isinstance(job, dict):
                continue

            title = job.get("title", "")
            company = job.get("company_name", "")
            description = job.get("description", "")
            category = job.get("category", "")
            candidate_location = job.get(
                "candidate_required_location",
                "Remote"
            )

            searchable_text = normalize_text(
                f"{title} {company} "
                f"{description} {category}"
            )

            # Require at least one search word.
            # If the user leaves keywords empty, show remote jobs.
            if search_words and not any(
                word in searchable_text
                for word in search_words
            ):
                continue

            normalized_jobs.append({
                "title": title or "Job title not available",
                "company": {
                    "display_name": (
                        company or "Company not listed"
                    )
                },
                "location": {
                    "display_name": (
                        f"Remote — {candidate_location}"
                    )
                },
                "description": description,
                "redirect_url": job.get("url", ""),
                "salary_text": job.get("salary", ""),
                "salary_min": None,
                "salary_max": None,
                "source": "Remotive",
                "category": {
                    "label": category
                },
            })

            if len(normalized_jobs) >= results_per_page:
                break

        return normalized_jobs, None

    except requests.exceptions.Timeout:
        return [], "Remotive request timed out."

    except requests.exceptions.RequestException as error:
        return [], f"Connection error while contacting Remotive: {error}"

    except ValueError:
        return [], "Remotive returned invalid JSON."


# =========================================================
# REMOVE DUPLICATES
# =========================================================
def remove_duplicate_jobs(jobs):
    unique_jobs = []
    seen_jobs = set()

    for job in jobs:
        title = normalize_text(job.get("title", ""))

        company = normalize_text(
            safe_company_name(job.get("company", {}))
        )

        link = str(
            job.get("redirect_url", "")
            or ""
        ).strip().lower()

        # Prefer URL when available; otherwise title + company.
        if link:
            job_key = f"url|{link}"
        else:
            job_key = f"title_company|{title}|{company}"

        if job_key not in seen_jobs:
            seen_jobs.add(job_key)
            unique_jobs.append(job)

    return unique_jobs


# =========================================================
# MATCHING ENGINE
# =========================================================
def calculate_match(job):
    title = job.get("title", "")
    description = job.get("description", "")
    company = safe_company_name(
        job.get("company", {})
    )
    category = job.get("category", {}).get(
        "label", ""
    )

    text = normalize_text(
        f"{title} {description} "
        f"{company} {category}"
    )

    location_text = normalize_text(
        job.get("location", {}).get(
            "display_name",
            ""
        )
    )

    score = 0
    reasons = []
    warnings = []

    # -------------------------
    # Languages
    # -------------------------
    if "arabic" in text or "arabe" in text:
        score += 30
        reasons.append(
            "Arabic language is explicitly relevant"
        )

    if "english" in text or "engleza" in text:
        score += 15
        reasons.append(
            "English language is relevant"
        )

    # -------------------------
    # Operations / customer
    # -------------------------
    operations_words = [
        "operations",
        "operational",
        "coordinator",
        "administrator",
        "administration",
        "back office",
        "customer support",
        "customer service",
        "customer care",
        "client service",
        "client support",
        "client management",
        "call center",
    ]

    if any(word in text for word in operations_words):
        score += 15
        reasons.append(
            "Operations / customer-service relevance"
        )

    # -------------------------
    # Finance / legal
    # -------------------------
    finance_words = [
        "finance",
        "financial",
        "accounting",
        "accounts payable",
        "accounts receivable",
        "tax",
        "taxation",
        "compliance",
        "invoice",
        "procurement",
        "legal",
        "audit",
        "banking",
        "bank",
        "collection",
        "treasury",
    ]

    if any(word in text for word in finance_words):
        score += 15
        reasons.append(
            "Finance / compliance / legal relevance"
        )

    # -------------------------
    # Logistics / warehouse
    # -------------------------
    logistics_words = [
        "logistics",
        "warehouse",
        "depot",
        "supply chain",
        "inventory",
        "transport",
        "purchasing",
        "procurement",
    ]

    if any(word in text for word in logistics_words):
        score += 10
        reasons.append(
            "Logistics / warehouse relevance"
        )

    # -------------------------
    # Tools
    # -------------------------
    if "sap" in text:
        score += 10
        reasons.append("SAP relevance")

    if "erp" in text:
        score += 8
        reasons.append("ERP relevance")

    if "excel" in text or "microsoft excel" in text:
        score += 5
        reasons.append("Excel relevance")

    if "sql" in text:
        score += 5
        reasons.append("SQL relevance")

    # -------------------------
    # Location
    # -------------------------
    if "timisoara" in location_text:
        score += 15
        reasons.append("Timișoara location")

    elif "remote" in location_text:
        score += 10
        reasons.append("Remote opportunity")

    # -------------------------
    # Romanian requirement
    # -------------------------
    romanian_requirement_words = [
        "romanian fluent",
        "fluent romanian",
        "romanian language required",
        "romanian required",
        "limba romana",
        "limba română",
        "romana avansat",
        "romanian c1",
        "romanian b2",
        "romana c1",
        "romana b2",
    ]

    if any(
        normalize_text(word) in text
        for word in romanian_requirement_words
    ):
        score -= 10
        warnings.append(
            "Romanian may be required at a higher level than Beginner"
        )

    # -------------------------
    # Remote eligibility
    # -------------------------
    remote_location_words = [
        "united states",
        "usa only",
        "canada only",
        "uk only",
        "india only",
    ]

    if (
        "remote" in location_text
        and any(
            word in location_text
            for word in remote_location_words
        )
    ):
        score -= 10
        warnings.append(
            "Check whether this remote job accepts applicants living in Romania"
        )

    score = max(
        0,
        min(score, 100)
    )

    return score, reasons, warnings


# =========================================================
# HEADER
# =========================================================
st.title("🎯 Careeros AI")
st.subheader(
    "AI-Powered Job Search & Application Assistant"
)

st.write(
    "Search Romanian and remote jobs, combine multiple sources, "
    "rank them against Ahmed's profile, and open the original "
    "job posting."
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("⚙️ Search Settings")

location = st.sidebar.text_input(
    "Location",
    "Timisoara"
)

keywords = st.sidebar.text_input(
    "Keywords",
    "customer support"
)

max_results = st.sidebar.slider(
    "Results per source",
    min_value=5,
    max_value=50,
    value=20
)

search_jooble = st.sidebar.checkbox(
    "🇷🇴 Jooble — Romania",
    value=True
)

search_remote = st.sidebar.checkbox(
    "🌍 Remotive — Remote",
    value=True
)

search_adzuna = st.sidebar.checkbox(
    "🌐 Adzuna — international / test",
    value=False
)

st.sidebar.divider()

st.sidebar.markdown("### 💡 Suggested searches")

st.sidebar.caption(
    """
Try one search at a time:

• arabic customer support
• arabic english customer service
• customer support
• operations specialist
• operations coordinator
• back office
• financial operations
• accounts payable
• accounts receivable
• tax
• banking
• accounting
• logistics coordinator
• warehouse
• SAP Excel
"""
)

st.sidebar.divider()

st.sidebar.markdown("### 🔐 API status")

st.sidebar.write(
    f"Jooble: {'✅ configured' if JOOBLE_API_KEY else '❌ missing'}"
)

st.sidebar.write(
    f"Adzuna: {'✅ configured' if ADZUNA_APP_ID and ADZUNA_APP_KEY else '⚪ not configured'}"
)

st.sidebar.write(
    "Remotive: ✅ no key required"
)

# =========================================================
# SEARCH
# =========================================================
st.divider()

if st.button("🔎 Search Jobs", type="primary"):

    all_jobs = []
    search_errors = []
    source_counts = []

    with st.spinner(
        "Searching Jooble, Remotive and selected international sources..."
    ):

        # -------------------------
        # JOOBLE
        # -------------------------
        if search_jooble:
            jooble_jobs, jooble_error = search_jooble_jobs(
                keywords,
                location,
                max_results
            )

            if jooble_error:
                # The "skipped" Adzuna message is intentionally not
                # relevant here; Jooble errors should always be visible.
                search_errors.append(
                    f"Jooble: {jooble_error}"
                )
            else:
                all_jobs.extend(jooble_jobs)
                source_counts.append(
                    f"Jooble: {len(jooble_jobs)}"
                )

        # -------------------------
        # REMOTIVE
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
            else:
                all_jobs.extend(remotive_jobs)
                source_counts.append(
                    f"Remotive: {len(remotive_jobs)}"
                )

        # -------------------------
        # ADZUNA
        # -------------------------
        if search_adzuna:
            adzuna_jobs, adzuna_error = search_adzuna_jobs(
                keywords,
                location,
                max_results
            )

            if adzuna_error:
                # For Romania, this explains why Adzuna is not used
                # without treating it as a failure of the app.
                if not (
                    is_romania_location(location)
                    and "skipped for Romania" in adzuna_error
                ):
                    search_errors.append(
                        f"Adzuna: {adzuna_error}"
                    )
            else:
                all_jobs.extend(adzuna_jobs)
                source_counts.append(
                    f"Adzuna: {len(adzuna_jobs)}"
                )

    # =====================================================
    # SOURCE DIAGNOSTICS
    # =====================================================
    if source_counts:
        st.info(
            " | ".join(source_counts)
        )

    for error_message in search_errors:
        st.warning(error_message)

    # =====================================================
    # NORMALIZE / DEDUPLICATE
    # =====================================================
    all_jobs = remove_duplicate_jobs(
        all_jobs
    )

    if not all_jobs:

        st.error(
            "No jobs were returned from the selected sources."
        )

        st.markdown(
            """
**For Timișoara, check these first:**

1. Jooble API key is present in Streamlit Secrets.
2. The secret name is exactly `JOOBLE_API_KEY`.
3. Try a simple search such as `customer support`.
4. Try `arabic` or `operations`.
5. Make sure the location is `Timisoara`.
"""
        )

    else:

        # =================================================
        # SCORE JOBS
        # =================================================
        scored_jobs = []

        for job in all_jobs:
            score, reasons, warnings = calculate_match(
                job
            )

            job["_score"] = score
            job["_reasons"] = reasons
            job["_warnings"] = warnings

            scored_jobs.append(job)

        scored_jobs.sort(
            key=lambda job: job["_score"],
            reverse=True
        )

        best_score = scored_jobs[0]["_score"]

        high_priority_count = sum(
            1
            for job in scored_jobs
            if job["_score"] >= 70
        )

        # =================================================
        # DASHBOARD
        # =================================================
        st.success(
            f"Found {len(scored_jobs)} unique jobs "
            "from the active sources."
        )

        metric_1, metric_2, metric_3, metric_4 = st.columns(4)

        metric_1.metric(
            "Jobs Found",
            len(scored_jobs)
        )

        metric_2.metric(
            "Best Match",
            f"{best_score}%"
        )

        metric_3.metric(
            "High Priority",
            high_priority_count
        )

        metric_4.metric(
            "Applications",
            "0"
        )

        st.divider()
        st.header("🎯 Recommended Jobs")

        # =================================================
        # DISPLAY JOBS
        # =================================================
        for index, job in enumerate(
            scored_jobs
        ):

            title = job.get(
                "title",
                "Unknown position"
            )

            company = safe_company_name(
                job.get("company", {})
            )

            job_location = job.get(
                "location",
                {}
            ).get(
                "display_name",
                "Unknown location"
            )

            source = job.get(
                "source",
                "Unknown source"
            )

            score = job["_score"]
            reasons = job["_reasons"]
            warnings = job["_warnings"]

            description = clean_html_text(
                job.get("description", "")
            )

            salary_text = job.get(
                "salary_text",
                ""
            )

            link = job.get(
                "redirect_url",
                ""
            )

            if score >= 70:
                priority = "🔥 HIGH PRIORITY"
            elif score >= 45:
                priority = "🟡 POSSIBLE MATCH"
            else:
                priority = "⚪ LOW PRIORITY"

            with st.container(border=True):

                st.subheader(
                    f"{index + 1}. {title}"
                )

                st.write(
                    f"**{priority} — Match Score: {score}%**"
                )

                st.progress(
                    score / 100
                )

                st.write(
                    f"🏢 **Company:** {company}"
                )

                st.write(
                    f"📍 **Location:** {job_location}"
                )

                st.write(
                    f"🌐 **Source:** {source}"
                )

                if salary_text:
                    st.write(
                        f"💰 **Salary listed:** {salary_text}"
                    )
                else:
                    st.write(
                        "💰 **Salary:** Not specified"
                    )

                if reasons:
                    st.write(
                        "**Why this may match your profile:**"
                    )

                    for reason in reasons:
                        st.success(
                            f"✓ {reason}"
                        )

                if warnings:
                    st.write(
                        "**Check before applying:**"
                    )

                    for warning in warnings:
                        st.warning(
                            f"⚠ {warning}"
                        )

                if description:
                    st.write(
                        "**Job description preview:**"
                    )

                    st.write(
                        description[:900]
                    )

                if valid_url(link):
                    st.link_button(
                        "📩 View Original Job & Apply",
                        link
                    )

# =========================================================
# PROFILE
# =========================================================
st.divider()

st.header("🎯 Your Job Search Profile")

st.write(
    f"**Candidate:** {PROFILE['name']}"
)

st.write(
    f"📍 **Location:** "
    f"{PROFILE['location']}, "
    f"{PROFILE['country']}"
)

st.write(
    "🗣️ **Languages:** "
    "Arabic / English / Romanian (Beginner)"
)

st.write(
    f"🎓 **Education:** "
    f"{PROFILE['education']}"
)

st.write(
    f"💼 **Experience:** "
    f"{PROFILE['experience_years']}+ years"
)

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

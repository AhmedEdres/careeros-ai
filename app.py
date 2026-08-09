import streamlit as st
import requests
import time
import re

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Careeros AI",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Careeros AI")
st.subheader("AI-Powered Job Search & Application Assistant")

st.write(
    "Smart job search, matching and application assistance "
    "for the Romanian and European job market."
)

# =========================
# CANDIDATE PROFILE
# =========================

PROFILE = {
    "name": "Ahmed",
    "location": "Timisoara",
    "languages": ["Arabic", "English", "Romanian"],
    "romanian_level": "Beginner",
    "education": "Master's Degree in Law",
    "experience_years": 10,
    "skills": [
        "operations",
        "client management",
        "financial compliance",
        "customer service",
        "Excel",
        "SAP",
        "SQL",
        "administration",
        "logistics",
        "Arabic",
        "English"
    ],
    "target_salary_min": 5000,
    "target_salary_max": 7000
}

# =========================
# SIDEBAR
# =========================

st.sidebar.header("⚙️ Search Settings")

location = st.sidebar.text_input(
    "Location",
    "Timisoara"
)

keywords = st.sidebar.text_input(
    "Keywords",
    "Arabic English Customer Support Operations Logistics Finance"
)

max_results = st.sidebar.slider(
    "Number of jobs",
    min_value=5,
    max_value=50,
    value=20
)

# =========================
# API SETTINGS
# =========================

ADZUNA_APP_ID = st.secrets["ADZUNA_APP_ID"]
ADZUNA_APP_KEY = st.secrets["ADZUNA_APP_KEY"]

# =========================
# JOB SEARCH FUNCTION
# =========================

def search_jobs(keywords, location, results_per_page=20):

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return None, "Adzuna API credentials are missing. Check Streamlit Secrets."

    url = "https://api.adzuna.com/v1/api/jobs/pl/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": keywords,
        "where": "Warsaw",
        "content-type": "application/json",
        "sort_by": "date"
    }

    headers = {
        "User-Agent": "Ahmed-CareerOS/1.0",
        "Accept": "application/json"
    }

    # Retry three times because Adzuna can temporarily return HTTP 503.
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
                # Do not show Adzuna's full HTML error page.
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

# =========================
# MATCHING ENGINE
# =========================

def calculate_match(job):

    text = (
        str(job.get("title", "")) + " " +
        str(job.get("description", "")) + " " +
        str(job.get("category", {}).get("label", "")) + " " +
        str(job.get("company", {}).get("display_name", ""))
    ).lower()

    score = 0
    reasons = []

    # Languages
    if "arabic" in text:
        score += 20
        reasons.append("Arabic language match")

    if "english" in text:
        score += 15
        reasons.append("English language match")

    # Operations
    operations_words = [
        "operations",
        "operational",
        "coordinator",
        "administrator",
        "back office",
        "customer support",
        "customer service"
    ]

    if any(word in text for word in operations_words):
        score += 15
        reasons.append("Operations / customer-service experience")

    # Finance / administration
    finance_words = [
        "finance",
        "financial",
        "accounting",
        "tax",
        "compliance",
        "procurement",
        "invoice"
    ]

    if any(word in text for word in finance_words):
        score += 10
        reasons.append("Finance / compliance background")

    # Logistics
    logistics_words = [
        "logistics",
        "warehouse",
        "depot",
        "supply chain",
        "inventory"
    ]

    if any(word in text for word in logistics_words):
        score += 10
        reasons.append("Logistics / warehouse relevance")

    # SAP / Excel
    if "sap" in text:
        score += 10
        reasons.append("SAP relevance")

    if "excel" in text:
        score += 5
        reasons.append("Excel relevance")

    # Location
    location_text = str(
        job.get("location", {})
        .get("display_name", "")
    ).lower()

    if "timisoara" in location_text:
        score += 10
        reasons.append("Timișoara location")

    # Salary
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")

    if salary_max and salary_max >= PROFILE["target_salary_min"]:
        score += 5
        reasons.append("Salary may fit target")

    score = min(score, 100)

    return score, reasons

# =========================
# SEARCH BUTTON
# =========================

st.divider()

if st.button("🔎 Search Jobs", type="primary"):

    with st.spinner("Testing Adzuna job listings in Warsaw..."):

        jobs, error = search_jobs(
            "customer service",
            "Warsaw",
            20
        )

    if error:

        st.error(error)

        if "credentials" in error.lower():
            st.info(
                "You need to add ADZUNA_APP_ID and "
                "ADZUNA_APP_KEY to Streamlit Secrets."
            )

    elif not jobs:

        st.warning(
            "No jobs found for this search. "
            "Try broader keywords or another location."
        )
    else:

        # Calculate matches
        scored_jobs = []

        for job in jobs:

            score, reasons = calculate_match(job)

            job["_score"] = score
            job["_reasons"] = reasons

            scored_jobs.append(job)

        # Sort by match score
        scored_jobs.sort(
            key=lambda x: x["_score"],
            reverse=True
        )

        # =========================
        # DASHBOARD
        # =========================

        best_score = scored_jobs[0]["_score"]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Jobs Found",
                len(scored_jobs)
            )

        with col2:
            st.metric(
                "Best Match",
                f"{best_score}%"
            )

        with col3:
            st.metric(
                "Applications",
                "0"
            )

        st.divider()

        st.header("🎯 Recommended Jobs")

        # =========================
        # DISPLAY JOBS
        # =========================

        for index, job in enumerate(scored_jobs):

            title = job.get(
                "title",
                "Unknown position"
            )

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

            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")

            if salary_min or salary_max:

                salary_text = (
                    f"{salary_min or '?'} - "
                    f"{salary_max or '?'} RON"
                )

            else:

                salary_text = "Salary not specified"

            score = job["_score"]

            with st.container(border=True):

                st.subheader(
                    f"{index + 1}. {title}"
                )

                st.write(
                    f"🏢 **Company:** {company}"
                )

                st.write(
                    f"📍 **Location:** {job_location}"
                )

                st.write(
                    f"💰 **Salary:** {salary_text}"
                )

                st.write(
                    f"🎯 **Match Score:** {score}%"
                )

                if job["_reasons"]:

                    st.write("**Why it matches:**")

                    for reason in job["_reasons"]:
                        st.write(f"• {reason}")

                description = job.get(
                    "description",
                    ""
                )

                if description:

                    clean_description = re.sub(
                        "<.*?>",
                        " ",
                        description
                    )

                    st.write(
                        clean_description[:700] + "..."
                    )

                link = job.get(
                    "redirect_url",
                    ""
                )

                if link:

                    st.link_button(
                        "📩 View & Apply",
                        link
                    )

# =========================
# PROFILE
# =========================

st.divider()

st.header("🎯 Your Job Search Profile")

st.write(f"**Candidate:** {PROFILE['name']}")

st.write(
    f"📍 **Location:** {PROFILE['location']}, Romania"
)

st.write(
    "🗣️ **Languages:** "
    "Arabic / English / Romanian (beginner)"
)

st.write(
    f"🎓 **Education:** {PROFILE['education']}"
)

st.write(
    f"💼 **Experience:** "
    f"{PROFILE['experience_years']}+ years"
)

st.write(
    f"💰 **Target Salary:** "
    f"{PROFILE['target_salary_min']:,} - "
    f"{PROFILE['target_salary_max']:,} RON"
)

st.info(
    "The next version will add AI analysis, "
    "CV matching, application-letter generation "
    "and job prioritization."
)

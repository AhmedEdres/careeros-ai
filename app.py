import streamlit as st
import requests
import re
import html
import unicodedata
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
from typing import List, Dict, Tuple, Optional

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="CareerOS AI",
    page_icon="🎯",
    layout="wide"
)

# =========================================================
# SECRETS & API KEYS
# =========================================================
ADZUNA_APP_ID = st.secrets.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = st.secrets.get("ADZUNA_APP_KEY", "")
JOOBLE_API_KEY = st.secrets.get("JOOBLE_API_KEY", "")
CLAUDE_API_KEY = st.secrets.get("CLAUDE_API_KEY", "")  # اختياري

# =========================================================
# AHMED PROFILE (محدث)
# =========================================================
PROFILE = {
    "name": "Ahmed",
    "location": "Timisoara",
    "country": "Romania",
    "languages": ["Arabic", "English", "Romanian"],
    "romanian_level": "Beginner",   # مبتدئ
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
    # إضافة تفضيلات
    "preferred_locations": ["Timisoara", "Romania", "Remote"],
    "preferred_categories": ["Finance", "Accounting", "Tax", "Legal",
                             "Compliance", "Administration", "Customer Support",
                             "Back Office", "Logistics"],
}

# =========================================================
# TEXT HELPERS (نفس السابق مع تعديلات طفيفة)
# =========================================================
def normalize_text(text):
    text = str(text or "")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
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
    location = str(location or "").strip()
    if not location:
        return "Timisoara, Romania"
    normalized = normalize_text(location)
    if normalized in {"timisoara", "timisoara romania", "timis", "timis romania"}:
        return "Timisoara, Romania"
    if "romania" not in normalized and ("timisoara" in normalized or normalized == "timis"):
        return f"{location}, Romania"
    return location

def is_romania_location(location):
    text = normalize_text(location)
    return any(place in text for place in ["romania", "timisoara", "bucharest", "bucuresti"])

def valid_url(url):
    try:
        parsed = urlparse(str(url))
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except:
        return False

# =========================================================
# SEARCH FUNCTIONS (بدون تغيير جوهري، مع إضافة caching)
# =========================================================
@st.cache_data(ttl=3600, show_spinner=False)
def search_jooble_jobs(keywords, location, results_per_page=20):
    # ... (نفس الكود السابق، لكن أضفنا cache)
    if not JOOBLE_API_KEY:
        return [], "Jooble API key missing."
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
    headers = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Ahmed-CareerOS/1.0"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=35)
        if response.status_code != 200:
            return [], f"Jooble HTTP {response.status_code}"
        data = response.json()
        jobs = data.get("jobs", [])
        normalized = []
        for job in jobs[:results_per_page]:
            normalized.append({
                "title": job.get("title", "Unknown"),
                "company": {"display_name": safe_company_name(job.get("company", "N/A"))},
                "location": {"display_name": str(job.get("location", search_location))},
                "description": job.get("snippet", ""),
                "redirect_url": job.get("link", ""),
                "salary_text": job.get("salary", ""),
                "salary_min": None,
                "salary_max": None,
                "source": "Jooble",
                "category": {"label": job.get("type", "")},
            })
        return normalized, None
    except Exception as e:
        return [], f"Jooble error: {e}"

@st.cache_data(ttl=3600, show_spinner=False)
def search_remotive_jobs(keywords, results_per_page=20):
    # ... (نفس السابق)
    url = "https://remotive.com/api/remote-jobs"
    headers = {"User-Agent": "Ahmed-CareerOS/1.0", "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=35)
        if response.status_code != 200:
            return [], f"Remotive HTTP {response.status_code}"
        data = response.json()
        jobs = data.get("jobs", [])
        search_words = [w.lower() for w in re.findall(r"[a-zA-Z]+", keywords) if len(w) >= 3]
        normalized = []
        for job in jobs:
            if not isinstance(job, dict): continue
            title = job.get("title", "")
            company = job.get("company_name", "")
            description = job.get("description", "")
            category = job.get("category", "")
            candidate_location = job.get("candidate_required_location", "Remote")
            searchable = normalize_text(f"{title} {company} {description} {category}")
            if search_words and not any(w in searchable for w in search_words):
                continue
            normalized.append({
                "title": title or "Unknown",
                "company": {"display_name": company or "N/A"},
                "location": {"display_name": f"Remote — {candidate_location}"},
                "description": description,
                "redirect_url": job.get("url", ""),
                "salary_text": job.get("salary", ""),
                "salary_min": None,
                "salary_max": None,
                "source": "Remotive",
                "category": {"label": category},
            })
            if len(normalized) >= results_per_page:
                break
        return normalized, None
    except Exception as e:
        return [], f"Remotive error: {e}"

# Adzuna (اختياري) – نحتفظ به لكن نضيف cache
@st.cache_data(ttl=3600, show_spinner=False)
def search_adzuna_jobs(keywords, location, results_per_page=20):
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return [], "Adzuna credentials missing."
    if is_romania_location(location):
        return [], "Adzuna skipped for Romania (use Jooble)."
    country_code = "gb"   # يمكن تخصيصه لاحقاً
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID, "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page, "what": keywords,
        "where": location, "content-type": "application/json", "sort_by": "date"
    }
    headers = {"User-Agent": "Ahmed-CareerOS/1.0", "Accept": "application/json"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=25)
        if response.status_code != 200:
            return [], f"Adzuna HTTP {response.status_code}"
        data = response.json()
        results = data.get("results", [])
        normalized = []
        for job in results[:results_per_page]:
            normalized.append({
                "title": job.get("title", "Unknown"),
                "company": {"display_name": safe_company_name(job.get("company", {}))},
                "location": {"display_name": job.get("location", {}).get("display_name", location) if isinstance(job.get("location"), dict) else str(job.get("location", location))},
                "description": job.get("description", ""),
                "redirect_url": job.get("redirect_url", ""),
                "salary_text": f"{job.get('salary_min')} - {job.get('salary_max')}" if job.get('salary_min') is not None else "",
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "source": "Adzuna",
                "category": {"label": safe_company_name(job.get("category", {})) if isinstance(job.get("category"), dict) else str(job.get("category", ""))},
            })
        return normalized, None
    except Exception as e:
        return [], f"Adzuna error: {e}"

# =========================================================
# REMOVE DUPLICATES
# =========================================================
def remove_duplicate_jobs(jobs):
    unique = []
    seen = set()
    for job in jobs:
        title = normalize_text(job.get("title", ""))
        company = normalize_text(safe_company_name(job.get("company", {})))
        link = str(job.get("redirect_url", "")).strip().lower()
        if link:
            key = f"url|{link}"
        else:
            key = f"title_company|{title}|{company}"
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique

# =========================================================
# ADVANCED MATCHING ENGINE (محور التطوير)
# =========================================================
def calculate_match_detailed(job: Dict) -> Dict:
    """
    إرجاع قاموس يحتوي على:
      - score: int (0-100)
      - reasons: list[str]
      - warnings: list[str]
      - dimensions: dict (تفصيل لكل عامل)
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
    loc_norm = normalize_text(location_text)

    # ============ الأبعاد ============
    dims = {}
    reasons = []
    warnings = []
    score = 0

    # 1. الموقع (أقصى 20 نقطة)
    location_score = 0
    if "timisoara" in loc_norm or "timișoara" in loc_norm:
        location_score = 20
        reasons.append("📍 الموقع: Timișoara (ممتاز)")
    elif "romania" in loc_norm:
        location_score = 15
        reasons.append("🇷🇴 الموقع: رومانيا (جيد)")
    elif "remote" in loc_norm:
        location_score = 10
        reasons.append("🏠 الموقع: عن بُعد (مقبول)")
    else:
        location_score = 5
        reasons.append("🌍 الموقع: خارج رومانيا (قد يكون غير مناسب)")
    score += location_score
    dims["location"] = location_score

    # 2. اللغة العربية (أقصى 15)
    arabic_score = 0
    if "arabic" in text or "arabe" in text or "عربي" in text:
        arabic_score = 15
        reasons.append("🗣️ اللغة العربية مطلوبة (مطابقة تامة)")
    else:
        # ليست مطلوبة لكن قد تكون ميزة إضافية
        arabic_score = 5
        reasons.append("🗣️ اللغة العربية غير مذكورة (ليست عائقاً)")
    score += arabic_score
    dims["arabic"] = arabic_score

    # 3. اللغة الإنجليزية (أقصى 10)
    eng_score = 0
    if "english" in text or "engleza" in text:
        eng_score = 10
        reasons.append("🇬🇧 اللغة الإنجليزية مطلوبة (ممتاز)")
    else:
        eng_score = 5
        reasons.append("🇬🇧 اللغة الإنجليزية غير مذكورة (غالباً مقبولة)")
    score += eng_score
    dims["english"] = eng_score

    # 4. المهارات الأساسية (العمليات، المالية، الضرائب، إلخ) – أقصى 25
    skill_score = 0
    # مهارات العمليات/الدعم
    ops_words = ["operations", "operational", "coordinator", "administrator", "administration",
                 "back office", "customer support", "customer service", "customer care",
                 "client service", "client support", "client management", "call center"]
    # مالية/امتثال
    finance_words = ["finance", "financial", "accounting", "accounts payable", "accounts receivable",
                     "tax", "taxation", "compliance", "invoice", "procurement", "legal", "audit",
                     "banking", "bank", "collection", "treasury"]
    # لوجستيات
    logistics_words = ["logistics", "warehouse", "depot", "supply chain", "inventory", "transport",
                       "purchasing"]
    # أدوات
    tools_words = ["sap", "erp", "excel", "sql"]

    if any(w in text for w in ops_words):
        skill_score += 8
    if any(w in text for w in finance_words):
        skill_score += 10
    if any(w in text for w in logistics_words):
        skill_score += 4
    if any(w in text for w in tools_words):
        skill_score += 3

    # تحديد أقصى 25
    skill_score = min(skill_score, 25)
    if skill_score >= 15:
        reasons.append(f"💼 المهارات: تتطابق مع خبراتك ({skill_score}/25)")
    else:
        reasons.append(f"💼 المهارات: تطابق جزئي ({skill_score}/25)")
    score += skill_score
    dims["skills"] = skill_score

    # 5. الخبرة (أقصى 10) – نبحث عن مؤشرات خبرة
    exp_score = 0
    # نبحث عن أرقام مثل "5 years" أو "senior" إلخ
    if re.search(r"\b(?:senior|lead|manager|director|head)\b", text, re.I):
        exp_score = 10
        reasons.append("🧑‍💼 الخبرة: دور قيادي/خبير (يناسب 10+ سنوات)")
    elif re.search(r"\b(?:5\+|5 years|more than 5|over 5)\b", text):
        exp_score = 8
        reasons.append("🧑‍💼 الخبرة: تتطلب 5+ سنوات (قريب من خبرتك)")
    else:
        exp_score = 5
        reasons.append("🧑‍💼 الخبرة: لم تحدد بوضوح (افتراض مطابقة جزئية)")
    score += exp_score
    dims["experience"] = exp_score

    # 6. التعليم (أقصى 5)
    edu_score = 0
    if "law" in text or "legal" in text or "master" in text:
        edu_score = 5
        reasons.append("🎓 التعليم: يتناسب مع شهادتك في القانون")
    else:
        edu_score = 3
        reasons.append("🎓 التعليم: لا يتطلب شهادة قانون (لكن خبرتك تعوض)")
    score += edu_score
    dims["education"] = edu_score

    # 7. الراتب (أقصى 10) – إذا كان الراتب معلناً
    salary_score = 0
    if salary_min is not None and isinstance(salary_min, (int, float)):
        if salary_min >= PROFILE["target_salary_min"]:
            salary_score = 10
            reasons.append(f"💰 الراتب: {salary_min} ≥ {PROFILE['target_salary_min']} (مناسب)")
        elif salary_min >= PROFILE["target_salary_min"] * 0.8:
            salary_score = 7
            reasons.append(f"💰 الراتب: {salary_min} قريب من المستهدف")
        else:
            salary_score = 2
            reasons.append(f"💰 الراتب: {salary_min} أقل من المستهدف بكثير")
    else:
        # إذا لم يحدد، نعطي درجة متوسطة
        salary_score = 5
        reasons.append("💰 الراتب: غير محدد (افتراض متوسط)")
    score += salary_score
    dims["salary"] = salary_score

    # 8. متطلبات الرومانية – تحذير وليس درجة إيجابية
    romanian_required = False
    romanian_level_high = False
    romanian_patterns = ["romanian fluent", "fluent romanian", "romanian language required",
                         "romanian required", "limba romana", "limba română", "romana avansat",
                         "romanian c1", "romanian b2", "romana c1", "romana b2"]
    if any(p in text for p in romanian_patterns):
        romanian_required = True
        if "c1" in text or "c2" in text or "fluent" in text:
            romanian_level_high = True
            warnings.append("⚠️ تشترط الوظيفة مستوى عالٍ من الرومانية (C1/C2) – غير مناسب لمستوى Beginner")
            # نخصم 10 نقاط من المجموع
            score -= 10
        else:
            warnings.append("⚠️ تشترط الوظيفة اللغة الرومانية – قد تكون صعبة لمستوى Beginner")
            score -= 5
    dims["romanian_penalty"] = -5 if romanian_required and not romanian_level_high else (-10 if romanian_level_high else 0)

    # 9. مرونة عن بُعد – إذا كانت Remote ونصها يشير إلى قيود جغرافية
    if "remote" in loc_norm:
        restricted = ["united states", "usa only", "canada only", "uk only", "india only"]
        if any(r in loc_norm for r in restricted):
            warnings.append("🌍 الوظيفة عن بُعد لكنها تقتصر على دول معينة – تحقق من أهلية رومانيا")
            score -= 5
        else:
            reasons.append("🏠 وظيفة عن بُعد – مرونة جيدة")

    # التأكد من أن النتيجة بين 0 و 100
    score = max(0, min(100, score))

    return {
        "score": score,
        "reasons": reasons,
        "warnings": warnings,
        "dimensions": dims
    }

# =========================================================
# CLAUDE AI INTEGRATION (اختياري)
# =========================================================
def analyze_with_claude(job: Dict) -> str:
    """إرسال معلومات الوظيفة إلى Claude وتحليلها."""
    if not CLAUDE_API_KEY:
        return "⚠️ مفتاح Claude غير مضبوط. أضف CLAUDE_API_KEY في Secrets."

    # نبني نصاً موجزاً
    title = job.get("title", "Unknown")
    company = safe_company_name(job.get("company", {}))
    location = job.get("location", {}).get("display_name", "Unknown")
    description = job.get("description", "")[:1500]  # اختصاراً
    salary = job.get("salary_text", "غير محدد")

    prompt = f"""
    أنت مساعد توظيف ذكي. قم بتحليل هذه الوظيفة لصالح مرشح اسمه أحمد.
    ملف أحمد:
    - الخبرة: 10 سنوات في العمليات، إدارة العملاء، الامتثال المالي، الضرائب، المحاسبة، الدعم.
    - اللغات: العربية (لغة أم)، الإنجليزية (ممتازة)، الرومانية (مبتدئ).
    - التعليم: ماجستير في القانون.
    - الموقع: تيميشوارا، رومانيا.
    - الراتب المستهدف: 5000-7000 RON.

    معلومات الوظيفة:
    العنوان: {title}
    الشركة: {company}
    الموقع: {location}
    الراتب: {salary}
    الوصف: {description}

    أجب بالعربية، وقدم:
    1. نسبة مطابقة تقديرية (0-100%) مع شرح.
    2. أهم 3 نقاط قوة في هذه الوظيفة لأحمد.
    3. أهم 3 مخاطر أو تحديات.
    4. توصية: هل يتقدم أم لا؟ مع سبب.
    """

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"❌ فشل تحليل Claude: {e}"

# =========================================================
# STREAMLIT APP
# =========================================================
st.title("🎯 CareerOS AI")
st.subheader("محرك البحث الذكي للوظائف – مع تحليل متقدم")

# =========================================================
# SIDEBAR – الفلاتر والإعدادات
# =========================================================
with st.sidebar:
    st.header("⚙️ إعدادات البحث")

    keywords = st.text_input("🔍 كلمات البحث", "customer support")
    location = st.text_input("📍 الموقع الأساسي", "Timisoara")

    st.subheader("📌 تصفية النتائج")
    # 1. نوع الموقع
    location_filter = st.selectbox(
        "نوع الموقع",
        options=["الكل", "Timișoara", "Romania", "Remote", "أوروبا"],
        index=0
    )
    # 2. الفئة الوظيفية (متعددة الاختيار)
    categories = ["Finance", "Accounting", "Tax", "Legal", "Compliance",
                  "Administration", "Customer Support", "Back Office", "Logistics", "أخرى"]
    selected_categories = st.multiselect("الفئة الوظيفية", categories, default=[])

    # 3. متطلبات الرومانية
    romanian_filter = st.radio(
        "متطلبات الرومانية",
        options=["أي", "لا تشترط الرومانية", "تسمح بمبتدئ"],
        index=0
    )

    # 4. الحد الأدنى للمطابقة
    min_match = st.slider("الحد الأدنى لنسبة المطابقة", 0, 100, 50, 5)

    st.divider()
    st.subheader("🔗 مصادر البحث")
    search_jooble = st.checkbox("🇷🇴 Jooble", value=True)
    search_remote = st.checkbox("🌍 Remotive", value=True)
    search_adzuna = st.checkbox("🌐 Adzuna (تجريبي)", value=False)

    st.divider()
    st.write(f"👤 **أحمد** – {PROFILE['experience_years']}+ سنوات")
    st.write(f"📍 {PROFILE['location']}, {PROFILE['country']}")
    st.write(f"💰 المستهدف: {PROFILE['target_salary_min']:,} – {PROFILE['target_salary_max']:,} RON")

# =========================================================
# MAIN SEARCH LOGIC
# =========================================================
if st.button("🔎 ابحث عن وظائف", type="primary"):
    # بدء البحث المتوازي
    all_jobs = []
    errors = []
    with st.status("جاري البحث في المصادر...", expanded=True) as status:
        search_functions = []
        if search_jooble:
            search_functions.append(("Jooble", search_jooble_jobs, (keywords, location, 30)))
        if search_remote:
            search_functions.append(("Remotive", search_remotive_jobs, (keywords, 30)))
        if search_adzuna:
            search_functions.append(("Adzuna", search_adzuna_jobs, (keywords, location, 30)))

        if not search_functions:
            st.error("يرجى اختيار مصدر بحث واحد على الأقل.")
            st.stop()

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_source = {executor.submit(func, *args): name for name, func, args in search_functions}
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    jobs, err = future.result()
                    if err:
                        errors.append(f"{source}: {err}")
                        status.update(label=f"⚠️ {source} فشل", state="error")
                    else:
                        all_jobs.extend(jobs)
                        status.update(label=f"✅ {source}: {len(jobs)} وظيفة", state="running")
                except Exception as e:
                    errors.append(f"{source}: استثناء {e}")

    # عرض الأخطاء
    for err in errors:
        st.warning(err)

    if not all_jobs:
        st.error("لم يتم العثور على وظائف. جرب تعديل كلمات البحث أو المصادر.")
        st.stop()

    # إزالة التكرار
    all_jobs = remove_duplicate_jobs(all_jobs)
    st.success(f"✅ تم العثور على {len(all_jobs)} وظيفة فريدة")

    # =========================================================
    # حساب المطابقة لكل وظيفة
    # =========================================================
    scored_jobs = []
    for job in all_jobs:
        match = calculate_match_detailed(job)
        job["_match"] = match
        scored_jobs.append(job)

    # =========================================================
    # تطبيق الفلاتر
    # =========================================================
    filtered = []
    for job in scored_jobs:
        match = job["_match"]
        score = match["score"]
        # 1. الحد الأدنى للمطابقة
        if score < min_match:
            continue

        # 2. تصفية الموقع
        loc_text = job.get("location", {}).get("display_name", "").lower()
        if location_filter != "الكل":
            if location_filter == "Timișoara" and "timisoara" not in loc_text and "timișoara" not in loc_text:
                continue
            elif location_filter == "Romania" and "romania" not in loc_text:
                continue
            elif location_filter == "Remote" and "remote" not in loc_text:
                continue
            elif location_filter == "أوروبا" and not any(x in loc_text for x in ["europe", "europa", "germany", "france", "spain", "italy"]):
                continue

        # 3. تصفية الفئة
        if selected_categories:
            cat_text = job.get("category", {}).get("label", "").lower()
            title_text = job.get("title", "").lower()
            desc_text = job.get("description", "").lower()
            combined = f"{cat_text} {title_text} {desc_text}"
            found = any(cat.lower() in combined for cat in selected_categories)
            if not found:
                continue

        # 4. تصفية الرومانية
        if romanian_filter == "لا تشترط الرومانية":
            # نتحقق من وجود كلمات تشترط الرومانية
            text = normalize_text(f"{job.get('title','')} {job.get('description','')}")
            if any(w in text for w in ["romanian required", "limba romana", "romana"]):
                continue
        elif romanian_filter == "تسمح بمبتدئ":
            # نسمح فقط إذا لم تكن تشترط مستوى عالٍ
            text = normalize_text(f"{job.get('title','')} {job.get('description','')}")
            if "c1" in text or "c2" in text or "fluent" in text:
                continue

        filtered.append(job)

    st.info(f"📊 بعد الفلاتر: {len(filtered)} وظيفة")

    if not filtered:
        st.warning("لا توجد وظائف تطابق الفلاتر. حاول تخفيف الشروط.")
        st.stop()

    # =========================================================
    # ترتيب تنازلي حسب الدرجة
    # =========================================================
    filtered.sort(key=lambda j: j["_match"]["score"], reverse=True)

    # =========================================================
    # عرض النتائج
    # =========================================================
    st.header("🎯 أفضل الوظائف المناسبة لك")

    # أزرار للتحليل بـ Claude
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🤖 تحليل أفضل 5 بـ Claude"):
            st.session_state["analyze_with_claude"] = True
    with col2:
        st.write("(يتطلب مفتاح Claude API في Secrets)")

    # عرض الوظائف
    for idx, job in enumerate(filtered[:20]):  # عرض 20 فقط
        match = job["_match"]
        score = match["score"]
        title = job.get("title", "Unknown")
        company = safe_company_name(job.get("company", {}))
        location = job.get("location", {}).get("display_name", "N/A")
        source = job.get("source", "N/A")
        salary = job.get("salary_text", "غير محدد")
        description = clean_html_text(job.get("description", ""))[:500]
        link = job.get("redirect_url", "")

        with st.container(border=True):
            # رأس الوظيفة مع الدرجة
            st.subheader(f"{idx+1}. {title}")
            st.progress(score/100, text=f"المطابقة: {score}%")
            st.write(f"🏢 **{company}**  |  📍 {location}  |  🌐 {source}")
            if salary:
                st.write(f"💰 **الراتب:** {salary}")

            # أسباب المطابقة
            if match["reasons"]:
                with st.expander("✅ أسباب المطابقة", expanded=False):
                    for r in match["reasons"]:
                        st.success(f"✓ {r}")

            # تحذيرات
            if match["warnings"]:
                with st.expander("⚠️ تحذيرات", expanded=False):
                    for w in match["warnings"]:
                        st.warning(f"⚠ {w}")

            # وصف مختصر
            if description:
                with st.expander("📄 عرض الوصف"):
                    st.write(description)

            # أزرار الإجراء
            col1, col2, col3 = st.columns([1, 1, 2])
            if valid_url(link):
                with col1:
                    st.link_button("📩 التقديم", link)
            with col2:
                # زر تسجيل التقديم
                job_key = f"applied_{idx}_{job.get('redirect_url', idx)}"
                if st.button("✅ سجل أنني تقدمت", key=job_key):
                    if "applied" not in st.session_state:
                        st.session_state.applied = set()
                    st.session_state.applied.add(job.get("redirect_url", idx))
                    st.success("تم تسجيل التقديم!")

            # تحليل Claude (إذا طلب)
            if st.session_state.get("analyze_with_claude", False) and idx < 5:
                with st.spinner(f"جاري تحليل الوظيفة {idx+1} بـ Claude..."):
                    analysis = analyze_with_claude(job)
                st.info(analysis)

    # تحديث عدد الطلبات
    applied_count = len(st.session_state.get("applied", set()))
    st.sidebar.metric("📋 عدد الطلبات المسجلة", applied_count)

# =========================================================
# FOOTER – معلومات الملف الشخصي
# =========================================================
st.divider()
with st.expander("👤 ملف أحمد الشخصي (للرجوع)"):
    st.json(PROFILE)

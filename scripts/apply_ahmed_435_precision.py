from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def edit(path, fn):
    p = ROOT / path
    s = p.read_text(encoding='utf-8')
    n = fn(s)
    if n == s:
        raise SystemExit(f'No change made to {path}; patch pattern not found')
    p.write_text(n, encoding='utf-8')

# matching.py

def patch_matching(s):
    # Add Romanian country endonyms to the foreign-market maps.
    extra = {
        'olanda':'Netherlands','tara de jos':'Netherlands','germania':'Germany','ungaria':'Hungary',
        'italia':'Italy','franta':'France','franța':'France','belgia':'Belgium','spania':'Spain',
        'cehia':'Czechia','polonia':'Poland','austria':'Austria','grecia':'Greece','suedia':'Sweden',
        'danemarca':'Denmark','irlanda':'Ireland','portugalia':'Portugal','anglia':'UK','marea britanie':'UK',
    }
    marker = '_EXTRA_FOREIGN_MARKETS = {'
    insert = ''.join(f'    {k!r}: {v!r},\n' for k,v in extra.items())
    if "'olanda': 'Netherlands'" not in s:
        s = s.replace(marker, marker + '\n' + insert, 1)
    pretty_marker = '_PRETTY_MARKET = {'
    if "'olanda': 'Netherlands'" not in s.split(pretty_marker,1)[1].split('}',1)[0]:
        s = s.replace(pretty_marker, pretty_marker + '\n' + insert, 1)
    # Make the same endonyms visible to the generic Europe classifier.
    hook = '_PRETTY_MARKET = {'
    if '_AHMED_FOREIGN_ENDONYMS' not in s:
        addition = "\n# Romanian endonyms must be visible to every location classifier, not only the market gate.\n_AHMED_FOREIGN_ENDONYMS = " + repr(list(extra.keys())) + "\nfor _market_token in _AHMED_FOREIGN_ENDONYMS:\n    if _market_token not in LOCATION_SYNONYMS[\"Europe\"]:\n        LOCATION_SYNONYMS[\"Europe\"].append(_market_token)\n"
        # place after _PRETTY_MARKET closes, before _is_home_location
        s = s.replace('\n\ndef _is_home_location', addition + '\n\ndef _is_home_location', 1)

    old = re.search(r'def foreign_labour_market\(location_text: str, title: str = ""\) -> Optional\[str\]:.*?\n\ndef classify_remote_geography', s, re.S)
    if not old:
        raise SystemExit('foreign_labour_market block not found')
    new = '''def foreign_labour_market(location_text: str, title: str = "", description: str = "") -> Optional[str]:
    """Return the actual foreign labour market, with title country beating agency cities.

    Romanian recruiter/agency cities do not make a Netherlands/Germany/etc. job
    local when the job title explicitly names the foreign destination. A clear
    Romania/Timișoara statement in the title wins back to the home market.
    """
    loc = normalize_text(location_text)
    title_n = normalize_text(title)
    desc_n = normalize_text(description)[:400]

    title_markets = _countries_named_in(title_n)
    tagged = _title_market(title_n)
    if tagged and tagged not in title_markets:
        title_markets.append(tagged)
    if title_markets:
        if not _is_home_location(title_n):
            return title_markets[0]

    # A named foreign market in the location is authoritative unless the title
    # explicitly says the actual workplace is Romania/Timișoara.
    named = _countries_named_in(loc)
    if named:
        if _is_home_location(title_n):
            return None
        return named[0]

    if _is_home_location(loc):
        return None

    if desc_n:
        desc_markets = _countries_named_in(desc_n)
        if desc_markets and not _is_home_location(desc_n):
            return desc_markets[0]

    if not _is_open_region(loc):
        leftover = _leftover_place(location_text)
        if leftover and not _is_home_location(leftover):
            pretty = _PRETTY_MARKET.get(leftover, _EXTRA_FOREIGN_MARKETS.get(leftover))
            return pretty or leftover.title()
    return None


def classify_remote_geography'''
    s = s[:old.start()] + new + s[old.end():]

    # Pass description into the market gate.
    s = s.replace('market = foreign_labour_market(raw_location, raw_title)', 'market = foreign_labour_market(raw_location, raw_title, desc)', 1)
    # Foreign market must never get the home-location bonus during scoring.
    needle = '    remote_class = classify_remote_geography(loc, desc)\n    result.remote = remote_class\n\n'
    repl = '    remote_class = classify_remote_geography(loc, desc)\n    result.remote = remote_class\n    market = foreign_labour_market(loc, "", desc)\n    if market:\n        result.warnings.append(f"🚫 Foreign labour market: {market}")\n        return 0\n\n'
    if needle in s and 'market = foreign_labour_market(loc, "", desc)' not in s:
        s = s.replace(needle, repl, 1)

    # Do not treat 10 years as people-management evidence.
    if '_MANAGEMENT_EVIDENCE_FOR_MATCHING' not in s:
        s = s.replace('\n\ndef _score_experience', '''\n\n_MANAGEMENT_EVIDENCE_FOR_MATCHING = (\n    "managed a team", "managed team", "direct reports", "people management",\n    "staff management", "supervised staff", "supervised a team", "led a team",\n    "led teams", "team leadership", "hiring and performance", "performance reviews",\n    "workforce management", "p&l responsibility", "p&l ownership", "budget ownership",\n    "budget management", "department head", "managed employees", "managed staff",\n)\n\n\ndef _score_experience''', 1)
    old_exp = '''    if contains_any(title, SENIORITY_PATTERNS["leadership"]):
        score = 9
        result.reasons.append(f"🧑‍💼 Leadership role — fits {profile.experience_years}+ years")
'''
    new_exp = '''    if contains_any(title, SENIORITY_PATTERNS["leadership"]):
        has_management_evidence = any(term in full for term in _MANAGEMENT_EVIDENCE_FOR_MATCHING)
        score = 9 if has_management_evidence else 7
        if has_management_evidence:
            result.reasons.append(f"🧑‍💼 Leadership role — fits {profile.experience_years}+ years")
        else:
            result.warnings.append("⚠️ Management title detected, but people-management scope is not documented")
'''
    if old_exp in s:
        s = s.replace(old_exp, new_exp, 1)
    return s

edit('careeros/matching.py', patch_matching)

# driving.py

def patch_driving(s):
    if '_HEAVY_TITLE' not in s:
        s = s.replace('from .text import contains_any, normalize_text\n', '''from .text import contains_any, normalize_text\nimport re\n\n_HEAVY_TITLE = re.compile(\n    r"\\b(?:c\\s*[＋+&/]\\s*e|c\\s*e\\b|categoria\\s+c(?:e|\\+e)?|category\\s+c(?:e|\\+e)?|cat\\.?\\s*c(?:e|\\+e)?|"\n    r"categoria\\s+d|category\\s+d|cat\\.?\\s*d|d\\s*[＋+&/]\\s*e|permis\\s+(?:c|ce|c\\+e|d|de)\\b|"\n    r"sofer\\s+camion|șofer\\s+camion|truck\\s+driver|tir(?:\\s+driver)?|sofer\\s+autobuz|șofer\\s+autobuz|"\n    r"bus\\s+driver|coach\\s+driver|camion|autobuz|autocar)\\b", re.IGNORECASE)\n_HEAVY_LICENCE_PHRASE = re.compile(\n    r"(?:permis|licence|license|categoria|category|cat\\.?)\\s*(?:c\\s*[＋+&/]\\s*e|c\\s*e|ce|c\\b|d\\b|d\\s*[＋+&/]\\s*e)", re.IGNORECASE)\n\ndef is_heavy_role(job: Dict) -> bool:\n    title = normalize_text(str(job.get("title", "") or ""))\n    body = normalize_text(str(job.get("description", "") or ""))[:800]\n    if _HEAVY_TITLE.search(title):\n        return True\n    phrase = _HEAVY_LICENCE_PHRASE.search(f"{title} {body}")\n    if phrase:\n        b_only = re.search(r"(?:categoria|category|cat\\.?|permis)\\s*b\\b", f"{title} {body}")\n        if b_only and not re.search(r"(?:c\\s*[＋+&/]\\s*e|categoria\\s+c|category\\s+c|cat\\.?\\s*c|permis\\s+c|categoria\\s+d|category\\s+d)", f"{title} {body}"):\n            return False\n        return True\n    return False\n\n''', 1)
    old = 'def should_keep_despite_negative_title(job: Dict, profile, track: str = "") -> bool:\n    return bool(getattr(profile, "has_category_b_license", True)) and driver_path(job) in {"driver_fallback", "hybrid"}\n'
    new = '''def _b_compatible(job: Dict) -> bool:
    title, full = _text(job)
    if is_heavy_role(job):
        return False
    if contains_any(full, CATEGORY_B_PATTERNS):
        return True
    return contains_any(title, ("courier", "curier", "livrator", "van driver", "delivery driver", "route driver"))


def should_keep_despite_negative_title(job: Dict, profile, track: str = "") -> bool:
    return bool(getattr(profile, "has_category_b_license", True)) and driver_path(job) in {"driver_fallback", "hybrid"} and _b_compatible(job)
'''
    if old in s: s = s.replace(old, new, 1)
    # Make enrichment a no-op for heavy and foreign-market jobs.
    old_start = '''def enrich_match_result(job: Dict, result, profile, track: str = ""):
    path = driver_path(job)
    if path == "none":
        return result
'''
    new_start = '''def enrich_match_result(job: Dict, result, profile, track: str = ""):
    path = driver_path(job)
    if path == "none":
        return result
    if is_heavy_role(job) or getattr(result, "reject_reason", "") or getattr(result, "verdict", "") == "skip":
        return result
    location = normalize_text(str((job.get("location") or {}).get("display_name", "") or ""))
    title = normalize_text(str(job.get("title", "") or ""))
    foreign = contains_any(title, ("olanda", "germania", "netherlands", "germany", "franta", "france", "italia", "italy", "belgia", "belgium", "spania", "spain", "polonia", "poland", "grecia", "greece"))
    if foreign:
        return result
'''
    if old_start in s: s = s.replace(old_start, new_start, 1)
    # Remove the duplicate location assignment later.
    s = s.replace('    location = normalize_text(str((job.get("location") or {}).get("display_name", "") or ""))\n    local = any(x in location for x in ("timisoara", "timișoara", "timis", "romania"))', '    local = any(x in location for x in ("timisoara", "timișoara", "timis", "romania"))', 1)
    # Full Career Scan must preserve compliance officer; only logistics gets B.
    start = s.index('def configure_search_presets')
    s = s[:start] + '''def configure_search_presets(presets: Dict[str, list]) -> None:
    """Keep the professional Full Scan intact; add Category B only to logistics."""
    key = "🏭 Logistics & Production"
    if key in presets and "sofer categoria B" not in presets[key]:
        if len(presets[key]) < 7:
            presets[key].append("sofer categoria B")
        else:
            presets[key][-1] = "sofer categoria B"
'''
    return s

edit('careeros/driving.py', patch_driving)

# salary.py

def patch_salary(s):
    s = s.replace('''def _infer_period(amount: float, currency: Optional[str]) -> str:
    """Guess the period from magnitude when the text does not say."""
    if currency == "ron":
        if amount <= 400:
            return "hour"
        if amount >= 60_000:
            return "year"
        return "month"
''', '''def _infer_period(amount: float, currency: Optional[str]) -> str:
    """Conservative fallback period inference; never infer RON hourly from size alone."""
    if currency == "ron":
        if amount >= 60_000:
            return "year"
        return "month"
''', 1)
    old = '    if period is None:\n        period = _infer_period(min_amount, currency)\n\n    monthly_min = to_monthly_ron(min_amount, currency, period)'
    new = '''    if period is None:
        # A small RON number without an explicit salary period is usually board/card noise.
        if currency == "ron" and min_amount < 1500:
            return SalaryInfo(raw=raw, currency=currency, period=None, min_amount=min_amount, max_amount=max_amount)
        if currency == "eur" and min_amount < 300:
            return SalaryInfo(raw=raw, currency=currency, period=None, min_amount=min_amount, max_amount=max_amount)
        period = _infer_period(min_amount, currency)

    # Even with an explicit month marker, reject implausible RON/EUR monthly card junk.
    if period == "month" and ((currency == "ron" and min_amount < 1500) or (currency == "eur" and min_amount < 300)):
        return SalaryInfo(raw=raw, currency=currency, period=period, min_amount=min_amount, max_amount=max_amount)

    monthly_min = to_monthly_ron(min_amount, currency, period)'''
    if old not in s: raise SystemExit('salary period block not found')
    return s.replace(old, new, 1)
edit('careeros/salary.py', patch_salary)

# role intelligence

def patch_role(s):
    if '"it governance"' not in s:
        s = s.replace('''IT_TITLE = (
''', '''IT_TITLE = (
    "it governance", "it coordinator", "it locations", "it infrastructure", "it service", "it operations",
    "information security", "infosec", "cyber security", "cybersecurity", "quality coordinator emea - tires",
''', 1)
    if '_IT_GOVERNANCE_TITLE_RE' not in s:
        s = s.replace('''def _job_parts(job: Dict) -> Tuple[str, str]:
''', '''_IT_GOVERNANCE_TITLE_RE = re.compile(r"\\bit\\b.+\\b(governance|infrastructure|service|operations|coordinator|asset|locations?)\\b", re.IGNORECASE)


def _job_parts(job: Dict) -> Tuple[str, str]:
''', 1)
        s = s.replace('from typing import Dict, List, Tuple\n', 'from typing import Dict, List, Tuple\nimport re\n', 1)
    s = s.replace('it_title = contains_any(title, IT_TITLE)', 'it_title = contains_any(title, IT_TITLE) or bool(_IT_GOVERNANCE_TITLE_RE.search(title))', 1)
    return s
edit('careeros/role_intelligence.py', patch_role)

# quality.py

def patch_quality(s):
    s = s.replace('HIRING_CEILINGS = ((50, 65), (70, 75), (80, 85))', 'HIRING_CEILINGS = ((50, 49), (60, 59), (70, 69))', 1)
    marker = 'def calibrate_result(result: MatchResult, job: Optional[Dict] = None, profile=None) -> MatchResult:\n    """Apply recruiter-realism guardrails without changing score semantics."""\n'
    if marker not in s: raise SystemExit('quality calibrate marker not found')
    guard = '''    # SKIP/reject_reason is terminal. Never let later calibration or the Category B
    # enricher turn a rejected role back into a ranked opportunity.
    if getattr(result, "verdict", "") == "skip" or getattr(result, "reject_reason", ""):
        result.score = min(int(getattr(result, "score", 0) or 0), 34)
        result.verdict_label, result.verdict = "🔴 SKIP", "skip"
        return result
'''
    if guard not in s:
        s = s.replace(marker, marker + guard, 1)
    old = '''    # Never force an 80+ score after a realism guardrail.  Previously this
    # exception could restore a high score after a meaningful mismatch.
'''
    # Add the green-band guard after ceiling loop and before confidence caps.
    needle = '''    for minimum_hiring, ceiling in HIRING_CEILINGS:
        if result.hiring_score < minimum_hiring:
            score = min(score, ceiling)
            break

'''
    add = '''    for minimum_hiring, ceiling in HIRING_CEILINGS:
        if result.hiring_score < minimum_hiring:
            score = min(score, ceiling)
            break

    specialized_family = _specialized_family(job)
    if management_penalty or specialized_family in {"it_technical", "software_data", "engineering"}:
        score = min(score, 69)

'''
    if needle in s: s = s.replace(needle, add, 1)
    return s
edit('careeros/quality.py', patch_quality)

# search.py

def patch_search(s):
    needle = '''        match = calculate_match(job, profile, track)
        job["_match"] = match

        if match.score < options.min_score:
'''
    repl = '''        match = calculate_match(job, profile, track)
        job["_match"] = match

        # Terminal role-intelligence SKIP/rejects are never ranked as cards.
        if getattr(match, "verdict", "") == "skip" or getattr(match, "reject_reason", ""):
            stats["rejected_hard"] += 1
            continue

        if match.score < options.min_score:
'''
    if needle in s: s=s.replace(needle,repl,1)
    return s
edit('careeros/search.py', patch_search)

# __init__.py heavy driver hard gate

def patch_init(s):
    if '_HEAVY_TITLE_RE' not in s:
        insert = '''\n_HEAVY_TITLE_RE = re.compile(\n    r"\\b(?:c\\s*[＋+&/]\\s*e|c\\s*e\\b|categoria\\s+c(?:e|\\+e)?|category\\s+c(?:e|\\+e)?|cat\\.?\\s*c(?:e|\\+e)?|"
    r"categoria\\s+d|category\\s+d|cat\\.?\\s*d|d\\s*[＋+&/]\\s*e|permis\\s+(?:c|ce|c\\+e|d|de)\\b|"
    r"sofer\\s+camion|șofer\\s+camion|truck\\s+driver|tir(?:\\s+driver)?|sofer\\s+autobuz|șofer\\s+autobuz|"
    r"bus\\s+driver|coach\\s+driver|camion|autobuz|autocar)\\b", re.IGNORECASE)\n\n_HEAVY_LICENCE_RE = re.compile(r"(?:permis|licence|license|categoria|category|cat\\.?)\\s*(?:c\\s*[＋+&/]\\s*e|c\\s*e|ce|c\\b|d\\b|d\\s*[＋+&/]\\s*e)", re.IGNORECASE)\n\ndef _is_heavy_driver_role(job) -> bool:\n    title = normalize_text(str(job.get("title", "") or ""))\n    desc = normalize_text(str(job.get("description", "") or ""))[:800]\n    if _HEAVY_TITLE_RE.search(title):\n        return True\n    if _HEAVY_LICENCE_RE.search(f"{title} {desc}"):\n        return True\n    return False\n'''
        s = s.replace('\n\ndef _title_foreign_market(job) -> str:\n', insert + '\n\ndef _title_foreign_market(job) -> str:\n', 1)
    needle = '    market = _title_foreign_market(job)\n    if market:\n'
    repl = '    if _is_heavy_driver_role(job):\n        return False, "🔴 Heavy-vehicle driver role requires C/C+E/D/TIR licence"\n\n    market = _title_foreign_market(job)\n    if market:\n'
    if needle in s and 'Heavy-vehicle driver role requires' not in s: s=s.replace(needle,repl,1)
    # Foreign market detector now lives in matching and sees descriptions; keep the title helper as a fast path.
    return s
edit('careeros/__init__.py', patch_init)

# Hipo hygiene

def patch_hipo(s):
    # salary noise filter
    old = '''        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
'''
    new = '''        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value_text = match.group(0)
            numbers = re.findall(r"\\d[\\d\\s.,]*\\d|\\d", value_text)
            try:
                numeric = float(re.sub(r"[.,](?=\\d{3}(?:\\D|$))", "", numbers[0]).replace(" ", "")) if numbers else 0
            except ValueError:
                numeric = 0
            normalized = normalize_text(value_text)
            if ("ron" in normalized or "lei" in normalized) and numeric < 1500:
                continue
            if "eur" in normalized and numeric < 300:
                continue
            return value_text
'''
    if old in s: s=s.replace(old,new,1)
    # company heading cleanup
    old_company = '''def _company(card, title: str) -> str:
    selectors = (
'''
    new_company = '''def _company(card, title: str) -> str:
    title_n = normalize_text(title)
    if "jobs from hipo" in title_n:
        at = re.search(r"@\\s*([^|]+)$", title)
        return at.group(1).strip() if at else ""
    selectors = (
'''
    if old_company in s:s=s.replace(old_company,new_company,1)
    s=s.replace('''            if value and normalize_text(value) != normalize_text(title):
                return value
''','''            value_n = normalize_text(value)
            if value and value_n != normalize_text(title) and "jobs from hipo" not in value_n:
                return value
''',1)
    # location token extraction
    old_loc = '''def _location(card, fallback: str) -> str:
    blob = _text(card)
    lines = [part.strip() for part in re.split(r"\\s{2,}|\\n", blob) if part.strip()]
    for line in lines:
        low = normalize_text(line)
        if any(token in low for token in _LOCATION_TOKENS):
            return line[:220]
    return fallback or "Romania"
'''
    new_loc = '''def _location(card, fallback: str) -> str:
    blob = _text(card)
    low_blob = normalize_text(blob)
    # Prefer an explicit city token and never return the whole card blob.
    for token in _LOCATION_TOKENS:
        if re.search(rf"(?<![a-z]){re.escape(normalize_text(token))}(?![a-z])", low_blob):
            pretty = "Timișoara" if normalize_text(token) in {"timisoara", "timișoara"} else token.title()
            if "remote" in low_blob and "hybrid" in low_blob:
                return f"Hybrid / {pretty}"
            if "remote" in low_blob:
                return f"Remote / {pretty}"
            return pretty
    fallback_n = normalize_text(fallback or "Romania")
    return "Timișoara" if fallback_n in {"timisoara", "timișoara"} else (fallback or "Romania")
'''
    if old_loc in s:s=s.replace(old_loc,new_loc,1)
    # title cleanup in parser
    old_title = '''        title = _text(link)
        if not title or len(title) > 220:
'''
    new_title = '''        title = _text(link)
        title = _DATE_RE.sub("", title).strip()
        title = re.sub(r"\\s+Jobs from Hipo.*$", "", title, flags=re.IGNORECASE).strip()
        if not title or len(title) > 220:
'''
    if old_title in s:s=s.replace(old_title,new_title,1)
    return s
edit('careeros/sources/hipo.py', patch_hipo)

# app copy: location variants, and defensive UI skip check.
def patch_app(s):
    s=s.replace('same role posted for {job[\'variant_count\']} countries{extra}', 'same role seen in {job[\'variant_count\']} locations{extra}', 1)
    old='''    match = job["_match"]
    url = job.get("redirect_url", "")
'''
    new='''    match = job["_match"]
    if getattr(match, "reject_reason", "") or getattr(match, "verdict", "") == "skip":
        return
    url = job.get("redirect_url", "")
'''
    if old in s:s=s.replace(old,new,1)
    return s
edit('app.py', patch_app)

# version marker
edit('careeros/__init__.py', lambda s: s.replace('__version__ = "4.3.5"','__version__ = "4.3.6"',1))

# Regression tests.
test = r'''from careeros import DEFAULT_PROFILE, calculate_match, hard_filter_job
from careeros.salary import parse_salary
from careeros.matching import foreign_labour_market
from careeros.search import CAREER_PRESETS


def job(title, location, description="", salary=""):
    return {
        "title": title,
        "description": description,
        "location": {"display_name": location},
        "company": {"display_name": "X"},
        "salary_text": salary,
        "category": {"label": ""},
    }


def test_ce_olanda_is_hard_rejected_even_when_agency_lists_timisoara():
    keep, reason = hard_filter_job(job("Sofer profesionist C+E - Olanda", "Timișoara, Iași (Iași), Brașov și alte 2 orașe", "C+E licence required; 3000 EUR net", "3000 - 3500 EUR"), DEFAULT_PROFILE)
    assert keep is False
    assert any(x in reason.lower() for x in ("heavy-vehicle", "olanda", "netherlands"))


def test_camion_ce_germania_is_hard_rejected():
    assert hard_filter_job(job("Sofer camion Categoria C+E -Germania", "Timișoara, România"), DEFAULT_PROFILE)[0] is False


def test_autobuz_olanda_is_hard_rejected():
    assert hard_filter_job(job("SOFER AUTOBUZ - OLANDA", "Timișoara, România"), DEFAULT_PROFILE)[0] is False


def test_category_b_local_driver_still_allowed():
    keep, reason = hard_filter_job(job("Șofer categoria B", "Timișoara", "Permis categoria B. Livrari locale."), DEFAULT_PROFILE)
    assert keep is True, reason


def test_title_olanda_is_foreign_market_despite_timisoara_location():
    assert foreign_labour_market("Timișoara, Iași, Brașov", "Sofer profesionist C+E - Olanda") in {"Netherlands", "Olanda"}


def test_it_governance_is_hard_rejected():
    keep, reason = hard_filter_job(job("Senior Regional IT Governance and Quality Coordinator EMEA - Tires", "Timisoara", "IT governance, quality systems, EMEA tires."), DEFAULT_PROFILE)
    assert keep is False
    assert any(x in reason.lower() for x in ("it", "engineering", "track"))


def test_operations_manager_without_team_evidence_is_not_strong():
    result = calculate_match(job("Operations Manager @Continental", "Timisoara", "Operations manager for the plant. English required. 5 years experience. Operations, production, SAP. " * 6, "40 Ron"), DEFAULT_PROFILE)
    assert result.score <= 69
    assert getattr(result, "verdict", "") not in {"strong", "apply"}
    assert result.salary is None or not result.salary.has_value


def test_forty_ron_is_not_a_salary():
    assert parse_salary("40 Ron").has_value is False


def test_real_local_salaries_still_parse():
    assert parse_salary("8000 RON net").has_value
    assert parse_salary("1.100 EUR").has_value


def test_transport_coordinator_local_is_kept():
    j = job("Transport coordinator", "Timișoara", "Category B required. Coordinate deliveries.", "8000 RON net")
    keep, reason = hard_filter_job(j, DEFAULT_PROFILE)
    assert keep is True, reason
    assert calculate_match(j, DEFAULT_PROFILE).score >= 55


def test_local_customer_support_is_kept():
    keep, reason = hard_filter_job(job("Customer Support Specialist", "Timișoara, România", "Customer support. English required."), DEFAULT_PROFILE)
    assert keep is True, reason


def test_compliance_officer_timisoara_is_kept():
    keep, reason = hard_filter_job(job("Compliance Officer EMEA (m/f/d)", "Timisoara", "Compliance, regulatory, English required. Romanian is a plus."), DEFAULT_PROFILE)
    assert keep is True, reason


def test_full_scan_still_includes_compliance_officer():
    queries = CAREER_PRESETS["🔥 Full Career Scan (recommended)"]
    assert "compliance officer" in queries
    assert "sofer categoria B" not in queries
'''
ptest = ROOT / 'tests/test_ahmed_live_top10.py'
ptest.write_text(test, encoding='utf-8')

print('patch staged')

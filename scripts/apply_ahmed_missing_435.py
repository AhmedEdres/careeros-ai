from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def edit(path, fn):
    p = ROOT / path
    s = p.read_text(encoding='utf-8')
    n = fn(s)
    if n == s:
        raise SystemExit(f'No change made to {path}; pattern may already be fixed or patch is stale')
    p.write_text(n, encoding='utf-8')


def matching(s):
    # Romanian endonyms missing from the Europe map.
    additions = {
        'olanda':'Netherlands','tara de jos':'Netherlands','germania':'Germany','ungaria':'Hungary',
        'italia':'Italy','franta':'France','franța':'France','belgia':'Belgium','spania':'Spain',
        'cehia':'Czechia','polonia':'Poland','austria':'Austria','grecia':'Greece','suedia':'Sweden',
        'danemarca':'Denmark','irlanda':'Ireland','portugalia':'Portugal','anglia':'UK','marea britanie':'UK',
    }
    if '"olanda": "Netherlands"' not in s:
        s = s.replace('    "india": "India",', '    "olanda": "Netherlands",\n' + ''.join(f'    "{k}": "{v}",\n' for k,v in additions.items() if k != 'olanda') + '    "india": "India",', 1)
    pretty = s[s.index('_PRETTY_MARKET = {'):s.index('}\n\n\ndef _is_home_location', s.index('_PRETTY_MARKET = {'))]
    missing_pretty = ''.join(f'    "{k}": "{v}",\n' for k,v in additions.items() if f'"{k}":' not in pretty)
    if missing_pretty:
        s = s.replace('_PRETTY_MARKET = {', '_PRETTY_MARKET = {\n' + missing_pretty, 1)

    pattern = r'def foreign_labour_market\(location_text: str, title: str = ""\) -> Optional\[str\]:.*?\n\ndef classify_remote_geography'
    replacement = '''def foreign_labour_market(location_text: str, title: str = "", description: str = "") -> Optional[str]:
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


def classify_remote_geography'''
    s, count = re.subn(pattern, replacement, s, flags=re.S)
    if count != 1:
        raise SystemExit('foreign_labour_market replacement failed')
    # Pass description through the hard gate.
    s = s.replace('market = foreign_labour_market(raw_location, raw_title)', 'market = foreign_labour_market(raw_location, raw_title, desc)', 1)
    # Location scoring must never award a Romanian bonus to a foreign labour market.
    needle = '    result.remote = remote_class\n\n    if home and contains_phrase(loc, home):'
    repl = '    result.remote = remote_class\n    market = foreign_labour_market(loc, "", desc)\n    if market:\n        result.warnings.append(f"🚫 Foreign labour market: {market}")\n        return 0\n\n    if home and contains_phrase(loc, home):'
    if needle in s and 'market = foreign_labour_market(loc, "", desc)' not in s:
        s = s.replace(needle, repl, 1)
    return s
edit('careeros/matching.py', matching)


def init(s):
    # Heavy licence gate is title-first and independent of agency location.
    if '_AHMED_HEAVY_TITLE_RE' not in s:
        block = '''\n_AHMED_HEAVY_TITLE_RE = re.compile(\n    r"\\b(?:c\\s*[＋+&/]\\s*e|c\\s*e\\b|categoria\\s+c(?:e|\\+e)?|category\\s+c(?:e|\\+e)?|cat\\.?\\s*c(?:e|\\+e)?|"\n    r"categoria\\s+d|category\\s+d|cat\\.?\\s*d|d\\s*[＋+&/]\\s*e|permis\\s+(?:c|ce|c\\+e|d|de)\\b|"\n    r"sofer\\s+camion|șofer\\s+camion|truck\\s+driver|tir(?:\\s+driver)?|sofer\\s+autobuz|șofer\\s+autobuz|"\n    r"bus\\s+driver|coach\\s+driver|camion|autobuz|autocar)\\b", re.IGNORECASE)\n\n_AHMED_HEAVY_LICENCE_RE = re.compile(\n    r"(?:permis|licence|license|categoria|category|cat\\.?)\\s*(?:c\\s*[＋+&/]\\s*e|c\\s*e|ce|c\\b|d\\b|d\\s*[＋+&/]\\s*e)", re.IGNORECASE)\n\ndef _is_heavy_driver_role(job) -> bool:\n    title = normalize_text(str(job.get("title", "") or ""))\n    desc = normalize_text(str(job.get("description", "") or ""))[:800]\n    if _AHMED_HEAVY_TITLE_RE.search(title):\n        return True\n    if _AHMED_HEAVY_LICENCE_RE.search(f"{title} {desc}"):\n        if re.search(r"(?:categoria|category|cat\\.?|permis)\\s*b\\b", f"{title} {desc}") and not re.search(r"(?:c\\s*[＋+&/]\\s*e|categoria\\s+c|category\\s+c|cat\\.?\\s*c|permis\\s+c|categoria\\s+d|category\\s+d)", f"{title} {desc}"):\n            return False\n        return True\n    return False\n'''
        s = s.replace('\n\ndef _title_foreign_market(job)', block + '\n\ndef _title_foreign_market(job)', 1)
    marker = '    market = _title_foreign_market(job)\n    if market:\n'
    if 'Heavy-vehicle driver role' not in s:
        s = s.replace(marker, '    if _is_heavy_driver_role(job):\n        return False, "🔴 Heavy-vehicle driver role requires C/C+E/D/TIR licence"\n\n' + marker, 1)
    return s
edit('careeros/__init__.py', init)


def driving(s):
    if 'def is_heavy_role(' not in s:
        s = s.replace('from .text import contains_any, normalize_text\n', '''from .text import contains_any, normalize_text\nimport re\n\n_HEAVY_TITLE = re.compile(r"\\b(?:c\\s*[＋+&/]\\s*e|c\\s*e\\b|categoria\\s+c(?:e|\\+e)?|category\\s+c(?:e|\\+e)?|cat\\.?\\s*c(?:e|\\+e)?|categoria\\s+d|category\\s+d|cat\\.?\\s*d|d\\s*[＋+&/]\\s*e|permis\\s+(?:c|ce|c\\+e|d|de)\\b|sofer\\s+camion|șofer\\s+camion|truck\\s+driver|tir(?:\\s+driver)?|sofer\\s+autobuz|șofer\\s+autobuz|bus\\s+driver|coach\\s+driver|camion|autobuz|autocar)\\b", re.IGNORECASE)\n_HEAVY_LICENCE_PHRASE = re.compile(r"(?:permis|licence|license|categoria|category|cat\\.?)\\s*(?:c\\s*[＋+&/]\\s*e|c\\s*e|ce|c\\b|d\\b|d\\s*[＋+&/]\\s*e)", re.IGNORECASE)\n\ndef is_heavy_role(job: Dict) -> bool:\n    title, full = _text(job)\n    if _HEAVY_TITLE.search(title):\n        return True\n    if _HEAVY_LICENCE_PHRASE.search(full):\n        if contains_any(full, CATEGORY_B_PATTERNS) and not re.search(r"(?:categoria|category|cat\\.?|permis)\\s*(?:c|ce|c\\+e|d)\\b", full):\n            return False\n        return True\n    return False\n\n''', 1)
    s = s.replace('return bool(getattr(profile, "has_category_b_license", True)) and driver_path(job) in {"driver_fallback", "hybrid"}', 'return bool(getattr(profile, "has_category_b_license", True)) and driver_path(job) in {"driver_fallback", "hybrid"} and not is_heavy_role(job) and (contains_any(_text(job)[1], CATEGORY_B_PATTERNS) or contains_any(_text(job)[0], ("courier", "curier", "livrator", "van driver", "delivery driver", "route driver")))', 1)
    old = '''    if path == "none":
        return result
    if not getattr(profile, "has_category_b_license", True):
'''
    new = '''    if path == "none":
        return result
    if is_heavy_role(job) or getattr(result, "reject_reason", "") or getattr(result, "verdict", "") == "skip":
        return result
    title = normalize_text(str(job.get("title", "") or ""))
    if contains_any(title, ("olanda", "germania", "netherlands", "germany", "franta", "france", "italia", "italy", "belgia", "belgium", "spania", "spain", "polonia", "poland", "grecia", "greece")):
        return result
    if not getattr(profile, "has_category_b_license", True):
'''
    if old in s:s=s.replace(old,new,1)
    # Full Scan must keep compliance officer. Add B only to logistics.
    pattern = r'def configure_search_presets\(presets: Dict\[str, list\]\) -> None:.*?\n(?=\Z)'
    replacement = '''def configure_search_presets(presets: Dict[str, list]) -> None:
    """Preserve the six professional Full Scan queries; B-driver is logistics-only."""
    key = "🏭 Logistics & Production"
    if key in presets and "sofer categoria B" not in presets[key]:
        if len(presets[key]) < 7:
            presets[key].append("sofer categoria B")
        else:
            presets[key][-1] = "sofer categoria B"
'''
    s, count = re.subn(pattern, replacement, s, flags=re.S)
    if count != 1: raise SystemExit('driving configure_search_presets replacement failed')
    return s
edit('careeros/driving.py', driving)


def quality(s):
    s = s.replace('HIRING_CEILINGS = ((50, 65), (70, 75), (80, 85))', 'HIRING_CEILINGS = ((50, 49), (60, 59), (70, 69))', 1)
    marker = 'def calibrate_result(result: MatchResult, job: Optional[Dict] = None, profile=None) -> MatchResult:\n    """Apply recruiter-realism guardrails without changing score semantics."""\n'
    if 'result.verdict_label, result.verdict = "🔴 SKIP", "skip"' not in s[s.index('def calibrate_result'):s.index('def calibrate_jobs')]:
        s=s.replace(marker, marker + '''    # SKIP/reject_reason is terminal. Never let calibration or the driver enricher
    # resurrect a rejected role into a ranked card.
    if getattr(result, "verdict", "") == "skip" or getattr(result, "reject_reason", ""):
        result.score = min(int(getattr(result, "score", 0) or 0), 34)
        result.verdict_label, result.verdict = "🔴 SKIP", "skip"
        return result
''', 1)
    needle='''    for minimum_hiring, ceiling in HIRING_CEILINGS:
        if result.hiring_score < minimum_hiring:
            score = min(score, ceiling)
            break

'''
    add=needle + '''    if management_penalty or _specialized_family(job) in {"it_technical", "software_data", "engineering"}:
        score = min(score, 69)

'''
    if 'score = min(score, 69)' not in s and needle in s:s=s.replace(needle, add, 1)
    return s
edit('careeros/quality.py', quality)


def role(s):
    if '"it governance"' not in s:
        s=s.replace('IT_TITLE = (\n', 'IT_TITLE = (\n    "it governance", "it coordinator", "it locations", "it infrastructure", "it service", "it operations", "information security", "infosec", "quality coordinator emea - tires",\n', 1)
    if '_IT_GOVERNANCE_TITLE_RE' not in s:
        s=s.replace('from typing import Dict, List, Tuple\n', 'from typing import Dict, List, Tuple\nimport re\n', 1)
        s=s.replace('def _job_parts(job: Dict) -> Tuple[str, str]:\n', '_IT_GOVERNANCE_TITLE_RE = re.compile(r"\\bit\\b.+\\b(governance|infrastructure|service|operations|coordinator|asset|locations?)\\b", re.IGNORECASE)\n\ndef _job_parts(job: Dict) -> Tuple[str, str]:\n', 1)
    s=s.replace('it_title = contains_any(title, IT_TITLE)', 'it_title = contains_any(title, IT_TITLE) or bool(_IT_GOVERNANCE_TITLE_RE.search(title))', 1)
    return s
edit('careeros/role_intelligence.py', role)


def salary(s):
    old='''def _infer_period(amount: float, currency: Optional[str]) -> str:
    """Guess the period from magnitude when the text does not say."""
    if currency == "ron":
        if amount <= 400:
            return "hour"
        if amount >= 60_000:
            return "year"
        return "month"
'''
    new='''def _infer_period(amount: float, currency: Optional[str]) -> str:
    """Conservative fallback period inference; never infer RON hourly from size alone."""
    if currency == "ron":
        if amount >= 60_000:
            return "year"
        return "month"
'''
    if old in s:s=s.replace(old,new,1)
    old2='''    if period is None:
        period = _infer_period(min_amount, currency)

    monthly_min = to_monthly_ron(min_amount, currency, period)
'''
    new2='''    if period is None:
        if currency == "ron" and min_amount < 1500:
            return SalaryInfo(raw=raw, currency=currency, period=None, min_amount=min_amount, max_amount=max_amount)
        if currency == "eur" and min_amount < 300:
            return SalaryInfo(raw=raw, currency=currency, period=None, min_amount=min_amount, max_amount=max_amount)
        period = _infer_period(min_amount, currency)

    if period == "month" and ((currency == "ron" and min_amount < 1500) or (currency == "eur" and min_amount < 300)):
        return SalaryInfo(raw=raw, currency=currency, period=period, min_amount=min_amount, max_amount=max_amount)

    monthly_min = to_monthly_ron(min_amount, currency, period)
'''
    if old2 not in s: raise SystemExit('salary inference block not found')
    return s.replace(old2,new2,1)
edit('careeros/salary.py', salary)


def search(s):
    needle='''        match = calculate_match(job, profile, track)
        job["_match"] = match

        if match.score < options.min_score:
'''
    repl='''        match = calculate_match(job, profile, track)
        job["_match"] = match

        if getattr(match, "verdict", "") == "skip" or getattr(match, "reject_reason", ""):
            stats["rejected_hard"] += 1
            continue

        if match.score < options.min_score:
'''
    if needle in s:s=s.replace(needle,repl,1)
    return s
edit('careeros/search.py', search)


def hipo(s):
    old='''        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
'''
    new='''        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value_text = match.group(0)
            nums = re.findall(r"\\d[\\d\\s.,]*\\d|\\d", value_text)
            try:
                numeric = float(nums[0].replace(".", "").replace(",", "").replace(" ", "")) if nums else 0
            except ValueError:
                numeric = 0
            norm = normalize_text(value_text)
            if ("ron" in norm or "lei" in norm) and numeric < 1500:
                continue
            if "eur" in norm and numeric < 300:
                continue
            return value_text
'''
    if old in s:s=s.replace(old,new,1)
    oldc='''def _company(card, title: str) -> str:
    selectors = (
'''
    newc='''def _company(card, title: str) -> str:
    title_n = normalize_text(title)
    if "jobs from hipo" in title_n:
        at = re.search(r"@\\s*([^|]+)$", title)
        return at.group(1).strip() if at else ""
    selectors = (
'''
    if oldc in s:s=s.replace(oldc,newc,1)
    s=s.replace('if value and normalize_text(value) != normalize_text(title):\n                return value', 'if value and normalize_text(value) != normalize_text(title) and "jobs from hipo" not in normalize_text(value):\n                return value', 1)
    oldl='''def _location(card, fallback: str) -> str:
    blob = _text(card)
    lines = [part.strip() for part in re.split(r"\\s{2,}|\\n", blob) if part.strip()]
    for line in lines:
        low = normalize_text(line)
        if any(token in low for token in _LOCATION_TOKENS):
            return line[:220]
    return fallback or "Romania"
'''
    newl='''def _location(card, fallback: str) -> str:
    blob = _text(card)
    low_blob = normalize_text(blob)
    for token in _LOCATION_TOKENS:
        token_n = normalize_text(token)
        if re.search(rf"(?<![a-z]){re.escape(token_n)}(?![a-z])", low_blob):
            pretty = "Timișoara" if token_n in {"timisoara", "timișoara"} else token.title()
            if "hybrid" in low_blob:
                return f"Hybrid / {pretty}"
            if "remote" in low_blob:
                return f"Remote / {pretty}"
            return pretty
    return fallback or "Romania"
'''
    if oldl in s:s=s.replace(oldl,newl,1)
    oldt='''        title = _text(link)
        if not title or len(title) > 220:
'''
    newt='''        title = _text(link)
        title = _DATE_RE.sub("", title).strip()
        title = re.sub(r"\\s+Jobs from Hipo.*$", "", title, flags=re.IGNORECASE).strip()
        if not title or len(title) > 220:
'''
    if oldt in s:s=s.replace(oldt,newt,1)
    return s
edit('careeros/sources/hipo.py', hipo)


def app(s):
    s=s.replace("same role posted for {job['variant_count']} countries{extra}", "same role seen in {job['variant_count']} locations{extra}", 1)
    old='''def render_job_card(index: int, job: Dict) -> None:
    match = job["_match"]
'''
    new='''def render_job_card(index: int, job: Dict) -> None:
    match = job["_match"]
    if getattr(match, "reject_reason", "") or getattr(match, "verdict", "") == "skip":
        return
'''
    if old in s:s=s.replace(old,new,1)
    return s
edit('app.py', app)

# Live regression suite.
test = r'''from careeros import DEFAULT_PROFILE, calculate_match, hard_filter_job
from careeros.salary import parse_salary
from careeros.matching import foreign_labour_market
from careeros.search import CAREER_PRESETS


def job(title, location, description="", salary=""):
    return {"title": title, "description": description, "location": {"display_name": location}, "company": {"display_name": "X"}, "salary_text": salary, "category": {"label": ""}}


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
    j=job("Transport coordinator", "Timișoara", "Category B required. Coordinate deliveries.", "8000 RON net")
    keep, reason=hard_filter_job(j, DEFAULT_PROFILE)
    assert keep is True, reason
    assert calculate_match(j, DEFAULT_PROFILE).score >= 55


def test_local_customer_support_is_kept():
    keep, reason=hard_filter_job(job("Customer Support Specialist", "Timișoara, România", "Customer support. English required."), DEFAULT_PROFILE)
    assert keep is True, reason


def test_compliance_officer_timisoara_is_kept():
    keep, reason=hard_filter_job(job("Compliance Officer EMEA (m/f/d)", "Timisoara", "Compliance, regulatory, English required. Romanian is a plus."), DEFAULT_PROFILE)
    assert keep is True, reason


def test_full_scan_still_includes_compliance_officer():
    queries=CAREER_PRESETS["🔥 Full Career Scan (recommended)"]
    assert "compliance officer" in queries
    assert "sofer categoria B" not in queries
'''
Path(ROOT/'tests/test_ahmed_live_top10.py').write_text(test, encoding='utf-8')
print('Ahmed patch prepared')

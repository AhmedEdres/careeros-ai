from careeros import CAREER_PRESETS
from careeros.ahmed_recall import _normalise_hipo_job
from careeros.search import MAX_QUERIES, SearchRequest


def test_full_scan_expands_high_value_ahmed_role_synonyms():
    queries = CAREER_PRESETS["🔥 Full Career Scan (recommended)"]
    assert len(queries) == 8
    assert "operations specialist" in queries
    assert "customer service" in queries
    assert "compliance officer" in queries
    assert "arabic customer support" in queries
    assert "sofer categoria B" not in queries


def test_full_scan_eight_queries_survive_search_cap():
    assert MAX_QUERIES >= 8
    request = SearchRequest(preset="🔥 Full Career Scan (recommended)", keywords="")
    assert request.resolved_queries() == CAREER_PRESETS["🔥 Full Career Scan (recommended)"]
    assert len(request.resolved_queries()) == 8


def test_hipo_heading_does_not_become_company_or_location():
    job = {
        "title": "Operations Manager @Continental",
        "company": {"display_name": "Jobs from Hipo in Timisoara"},
        "location": {
            "display_name": "Operations Manager @Continental Jobs from Hipo in Timisoara 13-08-2026 Hybrid"
        },
        "description": "Operations Manager @Continental Jobs from Hipo in Timisoara 13-08-2026 Hybrid",
        "salary_text": "40 Ron",
    }
    cleaned = _normalise_hipo_job(job)
    assert cleaned["company"]["display_name"] == "Continental"
    assert cleaned["location"]["display_name"] in {"Timisoara", "Hybrid / Timisoara"}
    assert cleaned["salary_text"] == ""


def test_hipo_real_salary_is_preserved():
    job = {
        "title": "Customer Support Specialist",
        "company": {"display_name": "UPFIT"},
        "location": {"display_name": "800 - 1100 Bulevardul Cetatii, Timisoara, Romania"},
        "description": "Customer support. English required.",
        "salary_text": "1.100 EUR",
    }
    cleaned = _normalise_hipo_job(job)
    assert cleaned["company"]["display_name"] == "UPFIT"
    assert cleaned["location"]["display_name"] == "800 - 1100 Bulevardul Cetatii, Timisoara, Romania"
    assert cleaned["salary_text"] == "1.100 EUR"

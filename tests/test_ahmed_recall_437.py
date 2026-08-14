from careeros import DEFAULT_PROFILE, CAREER_PRESETS, hard_filter_job
from careeros.search import SearchRequest


def job(title, location="Timișoara", description="", salary=""):
    return {
        "title": title,
        "description": description,
        "location": {"display_name": location},
        "company": {"display_name": "X"},
        "salary_text": salary,
        "category": {"label": ""},
    }


def test_full_scan_has_broad_ahmed_recall_queries():
    expected_core = {
        "operations coordinator",
        "operations specialist",
        "financial operations",
        "back office",
        "order management",
        "customer support",
        "customer service",
        "arabic customer support",
        "compliance officer",
        "tax compliance",
        "tax specialist",
        "logistics coordinator",
    }
    expected_romanian = {
        "coordonator operatiuni",
        "specialist administrativ",
        "specialist back office",
        "specialist conformitate",
        "specialist fiscal",
        "suport clienti",
        "serviciu clienti",
        "coordonator logistica",
    }
    queries = SearchRequest(
        preset="🔥 Full Career Scan (recommended)",
        keywords="",
    ).resolved_queries()
    query_set = set(queries)

    # 4.3.8 deliberately expands recall with Romanian titles used by local
    # boards; the English/core queries remain mandatory anchors.
    assert expected_core <= query_set
    assert expected_romanian <= query_set
    assert "compliance officer" in CAREER_PRESETS["🔥 Full Career Scan (recommended)"]


def test_tehnician_service_it_is_hard_rejected():
    keep, reason = hard_filter_job(
        job(
            "Tehnician Service IT",
            "Timișoara",
            "Service IT, troubleshooting hardware and network equipment.",
            "5000 - 7000 RON",
        ),
        DEFAULT_PROFILE,
    )
    assert keep is False
    assert "it" in reason.lower() or "technical" in reason.lower() or "track" in reason.lower()


def test_real_local_operations_role_is_not_blocked_by_it_body_mentions():
    keep, reason = hard_filter_job(
        job(
            "Operations Coordinator",
            "Timișoara",
            "Coordinate daily operations and reporting. Use IT systems, SAP and Excel.",
            "6000 RON net",
        ),
        DEFAULT_PROFILE,
    )
    assert keep is True, reason

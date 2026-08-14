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
    expected = {
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
    queries = SearchRequest(
        preset="🔥 Full Career Scan (recommended)",
        keywords="",
    ).resolved_queries()
    assert set(queries) == expected
    assert len(queries) == 12
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

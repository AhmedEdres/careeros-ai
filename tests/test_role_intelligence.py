from careeros.matching import hard_filter_job
from careeros.profile import Profile


def make_job(title, description="", location="Timisoara, Romania"):
    return {
        "title": title,
        "description": description,
        "location": {"display_name": location},
        "company": {"display_name": "ACME"},
        "category": {"label": ""},
        "salary_text": "",
        "salary_min": None,
        "salary_max": None,
        "redirect_url": "https://example.com/job/1",
        "source": "Test",
    }


def test_senior_cro_manager_is_not_a_recommended_role():
    keep, reason = hard_filter_job(
        make_job(
            "Senior CRO Manager",
            "Lead revenue growth, commercial strategy, sales operations and executive reporting."
        ),
        Profile(),
    )
    assert not keep
    assert "career track" in reason


def test_sales_manager_is_not_a_recommended_role():
    keep, reason = hard_filter_job(make_job("Sales Manager"), Profile())
    assert not keep
    assert "career track" in reason


def test_marketing_manager_is_not_a_recommended_role():
    keep, reason = hard_filter_job(make_job("Marketing Manager"), Profile())
    assert not keep
    assert "career track" in reason


def test_hr_manager_is_not_a_recommended_role():
    keep, reason = hard_filter_job(make_job("HR Manager"), Profile())
    assert not keep
    assert "career track" in reason


def test_finance_and_operations_roles_remain_available():
    for title in [
        "EDD Analyst",
        "Senior Accountant",
        "Operations Specialist",
        "Customer Support Specialist",
        "Tax Compliance Officer",
    ]:
        keep, reason = hard_filter_job(make_job(title), Profile())
        assert keep, f"{title!r} was unexpectedly rejected: {reason}"


def test_sales_language_in_description_does_not_reject_good_operations_role():
    keep, reason = hard_filter_job(
        make_job(
            "Operations Specialist",
            "Support sales operations with order processing, reporting and customer cases."
        ),
        Profile(),
    )
    assert keep, reason


def test_logistics_production_titles_remain_available():
    for title in [
        "Production Operator",
        "Warehouse Operator",
        "Logistics Coordinator",
        "Supply Chain Specialist",
    ]:
        keep, reason = hard_filter_job(make_job(title), Profile())
        assert keep, f"{title!r} was unexpectedly rejected: {reason}"

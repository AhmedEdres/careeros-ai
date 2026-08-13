from careeros.matching import calculate_match, hard_filter_job
from careeros.profile import Profile
from careeros.role_intelligence import assess_role


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


def test_account_manager_sales_function_is_rejected():
    job = make_job(
        "Account Manager",
        "Own a sales quota, prospect new clients, manage pipeline, cold calling and close deals."
    )
    assessment = assess_role(job)
    assert assessment.family == "sales_revenue"
    keep, reason = hard_filter_job(job, Profile())
    assert not keep
    assert "career track" in reason


def test_account_manager_operations_function_is_kept():
    job = make_job(
        "Account Manager",
        "Manage client cases, order processing, account administration and service delivery."
    )
    assessment = assess_role(job)
    assert assessment.family == "client_operations"
    keep, reason = hard_filter_job(job, Profile())
    assert keep, reason


def test_account_manager_without_function_evidence_is_kept_but_penalised():
    job = make_job("Account Manager", "Manage a portfolio of accounts and maintain relationships.")
    assessment = assess_role(job)
    assert assessment.family == "ambiguous_account"
    result = calculate_match(job, Profile())
    assert result.score < 70
    assert any("ambiguous" in warning.lower() for warning in result.warnings)


def test_senior_accountant_is_adjacent_not_direct():
    job = make_job(
        "Senior Accountant",
        "Prepare reconciliations, general ledger, month-end close and financial reporting."
    )
    assessment = assess_role(job)
    assert assessment.family == "accounting"
    result = calculate_match(job, Profile())
    assert any("accounting is adjacent" in warning.lower() for warning in result.warnings)
    assert any("directness gap" in name.lower() for name, _ in result.adjustments)


def test_sales_words_inside_operations_description_do_not_trigger_sales_gate():
    job = make_job(
        "Operations Specialist",
        "Support sales operations through order processing, reporting and customer case management."
    )
    assessment = assess_role(job)
    assert assessment.family != "sales_revenue"
    keep, reason = hard_filter_job(job, Profile())
    assert keep, reason

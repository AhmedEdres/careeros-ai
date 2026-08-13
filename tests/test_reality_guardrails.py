from careeros import calculate_match
from careeros.profile import Profile


def make_job(title="Operations Specialist", description="operations, SAP and Excel. English required.", location="Timisoara, Romania"):
    return {
        "title": title,
        "description": description,
        "location": {"display_name": location},
        "company": {"display_name": "ACME"},
        "category": {"label": ""},
        "salary_text": "",
        "redirect_url": "https://example.com/job/1",
        "source": "Test",
    }


def test_operations_manager_without_people_management_is_treated_as_stretch():
    profile = Profile()
    job = make_job(
        title="Operations Manager",
        description=(
            "Operations manager. English required. 5 years of experience. "
            "Operations, compliance, logistics, customer support, shared services. "
            "Romanian is a plus. " * 8
        ),
    )
    result = calculate_match(job, profile)
    assert result.match_score >= 80
    assert result.hiring_score <= 65
    assert result.score <= 75
    assert any("Management scope" in risk for risk in result.hiring_risks)


def test_management_evidence_restores_a_real_management_role():
    plain = Profile()
    manager = Profile(highlights=["Managed a team of 12 employees and owned department budget for 4 years"])
    job = make_job(
        title="Operations Manager",
        description=(
            "Manage a team of 10 and own the department budget. Operations, SAP and Excel. "
            "English required."
        ),
    )
    plain_result = calculate_match(job, plain)
    manager_result = calculate_match(job, manager)
    assert manager_result.hiring_score > plain_result.hiring_score
    assert manager_result.score > plain_result.score


def test_case_manager_is_not_mistaken_for_people_management():
    result = calculate_match(
        make_job(
            title="Compliance Case Manager",
            description="Handle compliance cases, documentation and customer communication. English required.",
        ),
        Profile(),
    )
    assert not any("Management scope" in risk for risk in result.hiring_risks)


def test_mandatory_pmp_without_evidence_is_penalised():
    result = calculate_match(
        make_job(
            title="Project Manager",
            description="PMP certification required. Manage projects and stakeholders. English required.",
        ),
        Profile(),
    )
    assert any("certification gate" in risk for risk in result.hiring_risks) or result.verdict == "skip"
    assert any("Mandatory certification gap" in label for label, _ in result.adjustments)


def test_preferred_pmp_does_not_trigger_hard_penalty():
    result = calculate_match(
        make_job(
            title="Operations Specialist",
            description="PMP certification preferred. Operations and Excel. English required.",
        ),
        Profile(),
    )
    assert not any("certification gate" in risk for risk in result.hiring_risks)

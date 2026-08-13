from careeros import DEFAULT_PROFILE, calculate_match


def _job(title, description="Strong English role in Timisoara.", location="Timisoara, Romania"):
    return {
        "title": title,
        "description": description,
        "location": location,
        "company": "Test Company",
        "salary_text": "",
        "age_days": 1,
    }


def test_senior_it_coordinator_is_not_ranked_as_a_normal_strong_fit():
    job = _job(
        "Senior IT Locations Coordinator",
        "Coordinate IT infrastructure locations, network services and technical vendors. "
        "Senior IT experience is required. English required.",
    )
    result = calculate_match(job, DEFAULT_PROFILE, "⚙️ Operations & Back Office")

    assert result.score < 80
    assert result.verdict == "skip" and result.reject_reason
    assert any(label == "Specialist-transfer realism" for label, _ in result.adjustments)


def test_operations_manager_is_limited_when_management_scope_is_not_documented():
    job = _job(
        "Operations Manager",
        "Manage a team of 15 employees, direct reports, workforce planning and KPI reviews. "
        "English required.",
    )
    result = calculate_match(job, DEFAULT_PROFILE, "⚙️ Operations & Back Office")

    assert result.hiring_score < 70
    assert result.score <= 75
    assert any("Management scope" in risk for risk in result.hiring_risks)


def test_compliance_role_remains_viable_without_false_specialist_penalty():
    job = _job(
        "Compliance Officer",
        "Review regulatory compliance cases, tax documentation, controls and internal procedures. "
        "English required. Romanian is a plus.",
    )
    result = calculate_match(job, DEFAULT_PROFILE, "💰 Finance & Compliance")

    assert result.score >= 60 and result.score <= 69
    assert not any("IT/technical specialism" in risk for risk in result.hiring_risks)


def test_freight_forwarder_is_stretch_not_impossible():
    job = _job(
        "Senior Freight Forwarder",
        "Manage international freight forwarding shipments, customs documentation and carriers. "
        "English required.",
    )
    result = calculate_match(job, DEFAULT_PROFILE, "🏭 Logistics & Production")

    assert 50 <= result.score < 80
    assert any("Freight/trade specialism" in risk for risk in result.hiring_risks)

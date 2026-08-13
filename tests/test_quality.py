from careeros import calculate_match
from careeros.profile import Profile
from careeros.quality import deduplicate_display_jobs


def make_job(title="Operations Coordinator", company="ACME", location="Timisoara, Romania", description="operations and customer support"):
    return {
        "title": title,
        "description": description,
        "location": {"display_name": location},
        "company": {"display_name": company},
        "redirect_url": f"https://example.com/{company}/{title}",
        "source": "Test",
    }


def test_reality_blend_prevents_match_score_from_dominating():
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
    assert result.hiring_score < result.match_score
    assert result.score < result.match_score
    assert result.score <= 92


def test_low_confidence_cannot_claim_near_perfect_fit():
    profile = Profile()
    job = make_job(title="Operations Specialist", description="operations specialist")
    result = calculate_match(job, profile)
    assert result.confidence == "low"
    assert result.score <= 88


def test_cross_source_duplicate_with_different_url_is_collapsed():
    a = make_job(description="Operations coordinator. English required. Excel and SAP. " * 10)
    b = dict(a)
    b["redirect_url"] = "https://another-board.example/jobs/123"
    b["source"] = "AnotherBoard"
    jobs, removed = deduplicate_display_jobs([a, b])
    assert len(jobs) == 1
    assert removed == 1
    assert "Test" in jobs[0]["source"]
    assert "AnotherBoard" in jobs[0]["source"]


def test_same_role_different_company_is_not_collapsed_without_strong_description_match():
    a = make_job(company="Company A", description="Operations coordinator in Timișoara. " * 5)
    b = make_job(company="Company B", description="Customer support specialist in Timișoara. " * 5)
    jobs, removed = deduplicate_display_jobs([a, b])
    assert len(jobs) == 2
    assert removed == 0

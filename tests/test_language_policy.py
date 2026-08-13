from careeros.matching import hard_filter_job
from careeros.profile import Profile


def make_job(description: str):
    return {
        "title": "Compliance Officer",
        "description": description,
        "location": {"display_name": "Timisoara, Romania"},
        "company": {"display_name": "Example"},
        "category": {"label": ""},
        "redirect_url": "https://example.com/job/1",
        "source": "Test",
    }


def test_english_required_without_level_is_allowed_for_b2():
    keep, reason = hard_filter_job(make_job("English required. Compliance and operations."), Profile())
    assert keep, reason


def test_fluent_english_without_explicit_cefr_is_not_hard_rejected():
    keep, reason = hard_filter_job(make_job("Fluent English language skills. Law degree preferred."), Profile())
    assert keep, reason


def test_c1_preferred_is_not_a_hard_rejection():
    keep, reason = hard_filter_job(make_job("English C1 preferred; B2 acceptable. Compliance."), Profile())
    assert keep, reason


def test_c1_required_is_rejected_for_b2_candidate():
    keep, reason = hard_filter_job(make_job("English C1 required. Compliance."), Profile())
    assert not keep
    assert "above B2" in reason

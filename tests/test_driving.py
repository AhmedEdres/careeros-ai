from careeros import calculate_match, hard_filter_job
from careeros.driving import driver_path
from careeros.profile import Profile


def job(title, description="", location="Timisoara, Romania"):
    return {
        "title": title,
        "description": description,
        "location": {"display_name": location},
        "company": {"display_name": "ACME"},
        "category": {"label": ""},
        "salary_text": "",
        "salary_min": None,
        "salary_max": None,
        "redirect_url": "https://example.com/driver",
    }


def test_category_b_driver_survives_wrong_track_gate():
    profile = Profile()
    keep, _ = hard_filter_job(job("Șofer categoria B", "Permis categoria B. Livrari locale."), profile)
    assert keep


def test_pure_driver_is_marked_as_fallback():
    profile = Profile()
    result = calculate_match(job("Șofer categoria B", "Permis categoria B. Livrari locale."), profile)
    assert driver_path(job("Șofer categoria B")) == "driver_fallback"
    assert result.track == "🚗 Driver Category B fallback"
    assert result.score <= 68
    assert any("Category B" in text for text in result.reasons)


def test_hybrid_category_b_role_can_rank_higher():
    profile = Profile()
    result = calculate_match(job(
        "Logistics Coordinator / Field Agent",
        "Category B required. Coordinate deliveries and field operations.",
    ), profile)
    assert driver_path(job("Logistics Coordinator / Field Agent")) == "hybrid"
    assert result.track == "🚗 Hybrid / Field fallback"
    assert result.score <= 78

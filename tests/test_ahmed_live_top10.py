from careeros import DEFAULT_PROFILE, calculate_match, hard_filter_job
from careeros.salary import parse_salary
from careeros.matching import foreign_labour_market
from careeros.search import CAREER_PRESETS
from careeros.driving import enrich_match_result


def job(title, location, description="", salary=""):
    return {"title": title, "description": description, "location": {"display_name": location}, "company": {"display_name": "X"}, "salary_text": salary, "category": {"label": ""}}


def test_ce_olanda_is_hard_rejected_even_when_agency_lists_timisoara():
    keep, reason = hard_filter_job(job("Sofer profesionist C+E - Olanda", "Timișoara, Iași (Iași), Brașov și alte 2 orașe", "C+E licence required; 3000 EUR net", "3000 - 3500 EUR"), DEFAULT_PROFILE)
    assert keep is False
    assert any(x in reason.lower() for x in ("heavy-vehicle", "olanda", "netherlands"))


def test_camion_ce_germania_is_hard_rejected():
    assert hard_filter_job(job("Sofer camion Categoria C+E -Germania", "Timișoara, România"), DEFAULT_PROFILE)[0] is False


def test_autobuz_olanda_is_hard_rejected():
    assert hard_filter_job(job("SOFER AUTOBUZ - OLANDA", "Timișoara, România"), DEFAULT_PROFILE)[0] is False


def test_category_b_local_driver_still_allowed():
    keep, reason = hard_filter_job(job("Șofer categoria B", "Timișoara", "Permis categoria B. Livrari locale."), DEFAULT_PROFILE)
    assert keep is True, reason


def test_title_olanda_is_foreign_market_despite_timisoara_location():
    assert foreign_labour_market("Timișoara, Iași, Brașov", "Sofer profesionist C+E - Olanda") in {"Netherlands", "Olanda"}


def test_it_governance_is_hard_rejected():
    keep, reason = hard_filter_job(job("Senior Regional IT Governance and Quality Coordinator EMEA - Tires", "Timisoara", "IT governance, quality systems, EMEA tires."), DEFAULT_PROFILE)
    assert keep is False
    assert any(x in reason.lower() for x in ("it", "engineering", "track"))


def test_operations_manager_without_team_evidence_is_not_strong():
    result = calculate_match(job("Operations Manager @Continental", "Timisoara", "Operations manager for the plant. English required. 5 years experience. Operations, production, SAP. " * 6, "40 Ron"), DEFAULT_PROFILE)
    assert result.score <= 69
    assert getattr(result, "verdict", "") not in {"strong", "apply"}
    assert result.salary is None or not result.salary.has_value


def test_manager_title_does_not_claim_people_management():
    result = calculate_match(
        job("Operations Manager", "Timișoara", "Operations, production and SAP. No team-management evidence."),
        DEFAULT_PROFILE,
    )
    assert not any("Leadership role — fits" in reason for reason in result.reasons)
    assert any("management" in warning.lower() for warning in result.warnings + result.hiring_risks)


def test_heavy_driver_enricher_is_a_noop():
    result = calculate_match(job("Sofer camion Categoria C+E - Germania", "Timișoara", "C+E licence required"), DEFAULT_PROFILE)
    before = (result.score, result.track, result.verdict, result.reject_reason)
    enriched = enrich_match_result(job("Sofer camion Categoria C+E - Germania", "Timișoara", "C+E licence required"), result, DEFAULT_PROFILE)
    assert (enriched.score, enriched.track, enriched.verdict, enriched.reject_reason) == before


def test_forty_ron_is_not_a_salary():
    assert parse_salary("40 Ron").has_value is False


def test_real_local_salaries_still_parse():
    assert parse_salary("8000 RON net").has_value
    assert parse_salary("1.100 EUR").has_value


def test_transport_coordinator_local_is_kept():
    j=job("Transport coordinator", "Timișoara", "Category B required. Coordinate deliveries.", "8000 RON net")
    keep, reason=hard_filter_job(j, DEFAULT_PROFILE)
    assert keep is True, reason
    assert calculate_match(j, DEFAULT_PROFILE).score >= 55


def test_local_customer_support_is_kept():
    keep, reason=hard_filter_job(job("Customer Support Specialist", "Timișoara, România", "Customer support. English required."), DEFAULT_PROFILE)
    assert keep is True, reason


def test_compliance_officer_timisoara_is_kept():
    keep, reason=hard_filter_job(job("Compliance Officer EMEA (m/f/d)", "Timisoara", "Compliance, regulatory, English required. Romanian is a plus."), DEFAULT_PROFILE)
    assert keep is True, reason


def test_full_scan_still_includes_compliance_officer():
    queries=CAREER_PRESETS["🔥 Full Career Scan (recommended)"]
    assert "compliance officer" in queries
    assert "sofer categoria B" not in queries

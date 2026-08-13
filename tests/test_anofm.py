"""ANOFM adapter tests; all network traffic is mocked."""

import json
from unittest.mock import MagicMock

from careeros.sources.anofm import fetch_anofm


def fake_response(payload, status=200):
    response = MagicMock()
    response.status_code = status
    response.json.return_value = payload
    response.text = json.dumps(payload)
    return response


def test_anofm_parses_structured_requirements_and_keeps_timisoara():
    session = MagicMock()
    session.post.return_value = fake_response({
        "rows": [{
            "id": 3316179,
            "title": "Operator producție",
            "employer_name": "ACME SRL",
            "county_name": "Timiș",
            "locality_name": "MUNICIPIUL TIMISOARA",
            "cor": "932906",
            "domain_name": "Industrie",
            "education_level": "Gimnazial",
            "experience": "Fără experiență",
            "languages": "Engleză - A1",
            "driving_license": "B",
            "valid_for_eu": "Da",
            "contract_type": "Durată nedeterminată",
            "work_schedule": "Normă întreagă",
            "salary_min": 4300,
            "salary_max": 5000,
            "benefits": "Bonuri de masă",
            "responsibilities": "Production and assembly work",
            "created_at": "2026-08-10 10:00:00",
            "valid_until": "2026-08-31",
        }]
    })

    result = fetch_anofm(
        keywords="production operator",
        location="Timisoara",
        limit=10,
        phrases=["production operator"],
        session=session,
    )

    assert result.ok and result.count == 1
    job = result.jobs[0]
    assert job["title"] == "Operator producție"
    assert job["company"]["display_name"] == "ACME SRL"
    assert "Engleză - A1" in job["description_text"]
    assert "Fără experiență" in job["description_text"]
    assert job["anofm_id"] == "3316179"
    assert job["redirect_url"].endswith("/3316179")
    assert job["salary_min"] == 4300.0
    assert job["salary_max"] == 5000.0


def test_anofm_drops_other_locations_before_scoring():
    session = MagicMock()
    session.post.return_value = fake_response({
        "rows": [
            {
                "id": 1,
                "title": "Customer Support Agent",
                "employer_name": "Timisoara Co",
                "county_name": "Timiș",
                "locality_name": "TIMISOARA",
                "responsibilities": "customer support",
            },
            {
                "id": 2,
                "title": "Customer Support Agent",
                "employer_name": "Bucharest Co",
                "county_name": "Municipiul București",
                "locality_name": "BUCURESTI",
                "responsibilities": "customer support",
            },
        ]
    })

    result = fetch_anofm(
        keywords="customer support",
        location="Timisoara",
        limit=10,
        phrases=["customer support"],
        session=session,
    )

    assert [j["anofm_id"] for j in result.jobs] == ["1"]


def test_anofm_accepts_datagrid_data_shape():
    session = MagicMock()
    session.post.return_value = fake_response({
        "data": [{
            "job_id": 7,
            "occupation_name": "Back Office Specialist",
            "company_name": "Example SRL",
            "location": "Timiș > Timișoara",
            "description": "back office operations",
        }]
    })

    result = fetch_anofm(
        keywords="back office",
        location="Timisoara",
        limit=5,
        phrases=["back office"],
        session=session,
    )

    assert result.ok and result.count == 1
    assert result.jobs[0]["anofm_id"] == "7"

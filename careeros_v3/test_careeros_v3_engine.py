from careeros_v3_engine import rank_jobs


def test_wrong_technical_role_does_not_rank_high():
    data = rank_jobs([
        {"title": "Tier III Service Desk Engineer", "company": "Example", "location": "Timisoara, Romania", "description": "English required. Windows, Linux, networking, Active Directory, ticketing. 3 years experience.", "redirect_url": "https://example.com/1", "source": "fixture"},
        {"title": "Senior Accountant", "company": "Example", "location": "Timisoara, Romania", "description": "English. Accounting, tax, compliance, SAP, Excel, reporting. 5 years experience.", "salary_text": "6000 RON", "redirect_url": "https://example.com/2", "source": "fixture"},
    ])
    jobs = data["jobs"]
    assert jobs[0].title == "Senior Accountant"
    tech = next(j for j in jobs if j.title.startswith("Tier III"))
    assert tech.career_family == "Technical / Engineering"
    assert tech.score <= 24
    assert jobs[0].score > tech.score


def test_country_locked_remote_is_rejected():
    data = rank_jobs([{
        "title": "Arabic Customer Support", "company": "Example", "location": "Remote — UK only", "description": "Arabic and English required.", "redirect_url": "https://example.com/3", "source": "fixture"
    }])
    assert data["stats"]["rejected_location"] == 1
    assert not data["jobs"]


def test_country_locked_remote_in_description_is_rejected():
    data = rank_jobs([{
        "title": "Arabic Customer Support", "company": "Example", "location": "Remote", "description": "Arabic and English required. Remote — Germany only.", "redirect_url": "https://example.com/3b", "source": "fixture"
    }])
    assert data["stats"]["rejected_location"] == 1
    assert not data["jobs"]


def test_required_german_is_rejected():
    data = rank_jobs([{
        "title": "Customer Service Specialist", "company": "Example", "location": "Timisoara, Romania", "description": "German B2 required, English preferred.", "redirect_url": "https://example.com/4", "source": "fixture"
    }])
    assert data["stats"]["rejected_language"] == 1
    assert not data["jobs"]


def test_duplicate_urls_merge_sources():
    data = rank_jobs([
        {"title": "Operations Specialist", "company": "Acme", "location": "Timisoara, Romania", "description": "Operations and Excel", "redirect_url": "https://example.com/job/5?utm_source=a", "source": "A"},
        {"title": "Operations Specialist", "company": "Acme", "location": "Timisoara, Romania", "description": "Operations, Excel, SAP", "redirect_url": "https://example.com/job/5?utm_source=b", "source": "B"},
    ])
    assert data["stats"]["duplicates_removed"] == 1
    assert data["jobs"][0].duplicate_count == 2


def test_arabic_operations_role_is_strong():
    data = rank_jobs([{
        "title": "Arabic Operations Specialist", "company": "Shared Services", "location": "Timisoara, Romania", "description": "Arabic speaker, English, operations, back office, client management, Excel, compliance. Minimum 3 years experience.", "salary_text": "6500 RON", "redirect_url": "https://example.com/6", "source": "fixture"
    }])
    job = data["jobs"][0]
    assert job.career_family in {"Arabic-Speaking Roles", "Operations & Back Office"}
    assert job.score >= 60


def test_unknown_experience_does_not_grant_free_points():
    data = rank_jobs([{
        "title": "Operations Coordinator", "company": "Example", "location": "Timisoara, Romania", "description": "Operations, English.", "redirect_url": "https://example.com/7", "source": "fixture"
    }])
    job = data["jobs"][0]
    assert job.dimensions["experience"] == 0


def test_word_boundary_prevents_false_tax_match():
    data = rank_jobs([{
        "title": "Taxi Dispatcher", "company": "Example", "location": "Timisoara, Romania", "description": "English and customer service.", "redirect_url": "https://example.com/8", "source": "fixture"
    }])
    job = data["jobs"][0]
    assert job.career_family != "Finance & Compliance"


def test_high_family_fit_can_reach_high_score():
    data = rank_jobs([{
        "title": "Arabic Compliance Operations Specialist", "company": "Example", "location": "Timisoara, Romania", "description": "Arabic speaker, English, compliance, regulatory, financial operations, back office, case management, Excel, SAP, reporting. Minimum 5 years experience.", "salary_text": "6000 RON", "redirect_url": "https://example.com/9", "source": "fixture"
    }])
    job = data["jobs"][0]
    assert job.family_fit >= 75
    assert job.score >= 75
    assert job.match_tier in {"good", "strong"}

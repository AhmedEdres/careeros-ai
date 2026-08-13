from careeros_v3_engine import rank_jobs


def test_wrong_technical_role_does_not_rank_high():
    data = rank_jobs([
        {"title": "Tier III Service Desk Engineer", "company": "Example", "location": "Timisoara, Romania", "description": "English required. Windows, Linux, networking, Active Directory, ticketing. 3 years experience.", "redirect_url": "https://example.com/1", "source": "fixture"},
        {"title": "Senior Accountant", "company": "Example", "location": "Timisoara, Romania", "description": "English. Accounting, tax, compliance, SAP, Excel, reporting. 5 years experience.", "salary_text": "6000 RON", "redirect_url": "https://example.com/2", "source": "fixture"},
    ])
    jobs = data["jobs"]
    assert jobs[0].title == "Senior Accountant"
    assert jobs[1].career_family == "Technical / Engineering"
    assert jobs[0].score > jobs[1].score


def test_country_locked_remote_is_rejected():
    data = rank_jobs([{
        "title": "Arabic Customer Support", "company": "Example", "location": "Remote — UK only", "description": "Arabic and English required.", "redirect_url": "https://example.com/3", "source": "fixture"
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

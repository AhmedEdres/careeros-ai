from careeros.sources.romania_boards import _parse_bestjobs, _parse_ejobs, _parse_linkedin


def test_parse_ejobs_card():
    html = '''
    <h2 class="job-card-content-middle__title">
      <a href="/job/customer-support-123">Customer Support Specialist</a>
    </h2>
    <div>
      <h3>Example SRL</h3>
      <div class="job-card-content-middle__info">Timișoara</div>
      <span>5000 - 6000 RON net</span>
    </div>
    '''
    jobs = _parse_ejobs(html, 5, "https://www.ejobs.ro")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Customer Support Specialist"
    assert jobs[0]["company"]["display_name"] == "Example SRL"
    assert "5000" in jobs[0]["salary_text"]


def test_parse_bestjobs_card():
    html = '''
    <div>
      <a class="absolute inset-0 z-1" href="/ro/loc-de-munca/example">x</a>
      <h2 class="line-clamp-2">Senior Accountant</h2>
      <div class="text-ink-medium">Example Shared Services</div>
      <div class="relative z-2">Timișoara, România</div>
      <span>5500 - 7000 RON</span>
    </div>
    '''
    jobs = _parse_bestjobs(html, 5, "https://www.bestjobs.eu")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Senior Accountant"
    assert jobs[0]["company"]["display_name"] == "Example Shared Services"
    assert "5500" in jobs[0]["salary_text"]


def test_parse_linkedin_card():
    html = '''
    <div class="base-card">
      <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/123">view</a>
      <h3 class="base-search-card__title">Operations Specialist</h3>
      <h4 class="base-search-card__subtitle">Example Europe</h4>
      <span class="job-search-card__location">Timișoara, Romania</span>
    </div>
    '''
    jobs = _parse_linkedin(html, 5, "https://www.linkedin.com")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Operations Specialist"
    assert jobs[0]["company"]["display_name"] == "Example Europe"
    assert "Timișoara" in jobs[0]["location"]["display_name"]

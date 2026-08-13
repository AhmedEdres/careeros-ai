from careeros.sources.hipo import _parse, _search_url


def test_hipo_search_url_targets_timisoara():
    url = _search_url("customer support", "Timisoara")
    assert "/Timisoara/customer-support" in url


def test_parse_hipo_job_detail_link():
    html = '''
    <div class="job-card">
      <a href="/locuri-de-munca/locuri_de_munca/269980/AUMOVIO-Romania/Privacy-Compliance-Officer-%28m/f/d%29">
        Privacy Compliance Officer (m/f/d)
      </a>
      <div class="company">AUMOVIO Romania</div>
      <div>Timisoara</div>
      <div>18-07-2026</div>
      <div>5000 - 7000 RON NET / luna</div>
    </div>
    '''
    jobs = _parse(html, 5, "Timisoara")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Privacy Compliance Officer (m/f/d)"
    assert jobs[0]["company"]["display_name"] == "AUMOVIO Romania"
    assert "Timisoara" in jobs[0]["location"]["display_name"]
    assert "5000" in jobs[0]["salary_text"]
    assert "hipo.ro/locuri-de-munca/locuri_de_munca/269980" in jobs[0]["redirect_url"]

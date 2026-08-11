"""Provider adapters and the search planner, exercised without real network calls."""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from careeros.search import SearchRequest, run_search
from careeros.sources.base import SourceResult, http_error_message
from careeros.sources.providers import (
    PROVIDERS,
    fetch_arbeitnow,
    fetch_jooble,
    fetch_remotive,
    fetch_source,
)


def fake_response(payload, status=200):
    response = MagicMock()
    response.status_code = status
    response.json.return_value = payload
    response.text = json.dumps(payload)
    return response


class TestJooble:
    def test_missing_key_is_skipped_not_failed(self):
        result = fetch_jooble("support", "Timisoara", api_key="")
        assert result.skipped and not result.jobs

    def test_parses_jobs(self):
        session = MagicMock()
        session.post.return_value = fake_response({
            "jobs": [{
                "title": "Support Agent", "company": "ACME", "location": "Timisoara",
                "snippet": "Great role", "link": "https://jooble.org/1",
                "salary": "5000 RON", "updated": "2026-08-01T10:00:00",
            }]
        })
        result = fetch_jooble("support", "Timisoara", api_key="k", pages=1, session=session)
        assert result.ok and result.count == 1
        job = result.jobs[0]
        assert job["title"] == "Support Agent"
        assert job["company"]["display_name"] == "ACME"
        assert job["age_days"] is not None

    def test_http_error_is_reported(self):
        session = MagicMock()
        session.post.return_value = fake_response({}, status=401)
        result = fetch_jooble("support", "Timisoara", api_key="bad", session=session)
        assert not result.ok and "401" in result.error


class TestRemotive:
    def test_parses_and_limits(self):
        session = MagicMock()
        session.get.return_value = fake_response({
            "jobs": [
                {"title": f"Role {i}", "company_name": "Co", "url": f"https://r.com/{i}",
                 "description": "text", "candidate_required_location": "Europe",
                 "publication_date": "2026-08-01"}
                for i in range(10)
            ]
        })
        result = fetch_remotive("support", limit=3, session=session)
        assert result.count == 3
        assert result.jobs[0]["remote"] is True


class TestArbeitnow:
    def test_client_side_keyword_filter(self):
        session = MagicMock()
        session.get.return_value = fake_response({
            "data": [
                {"title": "Customer Support Agent", "company_name": "A",
                 "url": "https://a.com/1", "description": "support", "tags": [], "location": "Berlin"},
                {"title": "Welder", "company_name": "B",
                 "url": "https://a.com/2", "description": "welding", "tags": [], "location": "Berlin"},
            ]
        })
        result = fetch_arbeitnow("customer support", limit=10, session=session)
        titles = [j["title"] for j in result.jobs]
        assert "Customer Support Agent" in titles
        assert "Welder" not in titles


class TestErrorHandling:
    def test_timeout_becomes_friendly_error(self):
        session = MagicMock()
        session.get.side_effect = requests.exceptions.Timeout()
        result = fetch_source("remotive", keywords="x", limit=5, session=session)
        assert not result.ok and "timed out" in result.error.lower()

    def test_connection_error(self):
        session = MagicMock()
        session.get.side_effect = requests.exceptions.ConnectionError()
        result = fetch_source("remotive", keywords="x", limit=5, session=session)
        assert not result.ok and "connect" in result.error.lower()

    def test_malformed_json(self):
        session = MagicMock()
        bad = MagicMock()
        bad.status_code = 200
        bad.json.side_effect = ValueError()
        session.get.return_value = bad
        result = fetch_source("remotive", keywords="x", limit=5, session=session)
        assert not result.ok and "malformed" in result.error.lower()

    def test_unknown_source(self):
        assert not fetch_source("nope").ok

    def test_never_raises(self):
        session = MagicMock()
        session.get.side_effect = RuntimeError("boom")
        result = fetch_source("remotive", keywords="x", limit=5, session=session)
        assert not result.ok

    def test_http_error_message_is_actionable(self):
        assert "API key" in http_error_message("Jooble", 401)
        assert "rate limit" in http_error_message("Jooble", 429).lower()


class TestSearchPlanner:
    def test_whole_board_sources_are_called_once(self):
        """Arbeitnow/Jobicy download the full board — never once per query."""
        calls = []

        def spy(key, **kwargs):
            calls.append((key, kwargs.get("keywords")))
            return SourceResult(source=key, jobs=[])

        with patch("careeros.search.fetch_source", side_effect=spy):
            request = SearchRequest(
                keywords="customer support",   # expands into several queries
                sources=["arbeitnow", "remotive"],
                expand_queries=True,
                secrets={},
            )
            report = run_search(request)

        arbeitnow_calls = [c for c in calls if c[0] == "arbeitnow"]
        remotive_calls = [c for c in calls if c[0] == "remotive"]
        assert len(arbeitnow_calls) == 1, "whole-board source must be fetched once"
        assert len(remotive_calls) == len(report.queries) > 1

    def test_report_aggregates_counts_and_errors(self):
        def spy(key, **kwargs):
            if key == "remotive":
                return SourceResult(source="Remotive", error="Remotive: boom")
            return SourceResult(source="Arbeitnow", jobs=[{
                "title": "X", "company": {"display_name": "C"},
                "location": {"display_name": "Remote"}, "description": "",
                "redirect_url": "https://a.com/1", "source": "Arbeitnow",
            }])

        with patch("careeros.search.fetch_source", side_effect=spy):
            report = run_search(SearchRequest(keywords="ops", sources=["arbeitnow", "remotive"]))

        assert report.counts_by_source.get("Arbeitnow", 0) >= 1
        assert any("boom" in e for e in report.errors)

    def test_no_sources_selected(self):
        report = run_search(SearchRequest(keywords="ops", sources=[]))
        assert report.jobs == [] and report.errors

    def test_preset_queries_used_when_no_keywords(self):
        request = SearchRequest(preset="💰 Finance & Compliance", keywords="")
        assert "tax compliance" in request.resolved_queries()

    def test_keywords_override_preset(self):
        request = SearchRequest(preset="💰 Finance & Compliance", keywords="warehouse")
        assert request.resolved_queries()[0] == "warehouse"


class TestProviderRegistry:
    def test_every_provider_has_metadata(self):
        for key, spec in PROVIDERS.items():
            assert spec.short_name and spec.label and callable(spec.fetch)

    def test_free_providers_need_no_keys(self):
        assert PROVIDERS["remotive"].needs_keys == []
        assert PROVIDERS["arbeitnow"].needs_keys == []

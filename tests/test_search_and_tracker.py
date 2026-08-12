import json

import pytest

from careeros.profile import Profile
from careeros.search import (
    FilterOptions,
    build_search_queries,
    deduplicate_jobs,
    score_and_filter,
)
from careeros.sources.base import days_since, make_job, parse_date
from careeros.tracker import ApplicationStore


def job(title="Operations Coordinator", url="https://example.com/1", company="ACME",
        location="Timisoara, Romania", description="customer support with excel", **kw):
    return make_job(
        title=title, company=company, location=location,
        description=description, url=url, source=kw.pop("source", "Test"), **kw
    )


class TestQueryBuilding:
    def test_expands_known_keyword(self):
        queries = build_search_queries("customer support", expand=True)
        assert "customer support" in queries
        assert len(queries) > 1

    def test_no_expansion_when_disabled(self):
        assert build_search_queries("customer support", expand=False) == ["customer support"]

    def test_caps_query_count(self):
        assert len(build_search_queries("customer support finance operations", True)) <= 6

    def test_empty_defaults(self):
        assert build_search_queries("", True) == ["operations"]


class TestDeduplication:
    def test_same_url_variants_collapse(self):
        jobs = [
            job(url="https://www.example.com/job/1?utm_source=a"),
            job(url="http://example.com/job/1/"),
        ]
        unique, removed = deduplicate_jobs(jobs)
        assert len(unique) == 1 and removed == 1

    def test_same_title_company_collapses(self):
        jobs = [
            job(url="https://a.com/1", description="short"),
            job(url="https://b.com/2", description="a much longer description " * 20),
        ]
        unique, removed = deduplicate_jobs(jobs)
        assert len(unique) == 1
        # The richer record wins and sources are merged.
        assert len(unique[0]["description"]) > 100
        assert unique[0]["duplicate_count"] == 2

    def test_different_jobs_kept(self):
        jobs = [job(title="A", url="https://a.com/1"), job(title="B", url="https://a.com/2")]
        unique, removed = deduplicate_jobs(jobs)
        assert len(unique) == 2 and removed == 0

    def test_merges_missing_salary(self):
        a = job(url="https://a.com/1", salary_text="")
        b = job(url="https://a.com/1", salary_text="5000 RON")
        unique, _ = deduplicate_jobs([a, b])
        assert unique[0]["salary_text"] == "5000 RON"

    def test_empty_input(self):
        assert deduplicate_jobs([]) == ([], 0)


class TestCampaignDeduplication:
    """One opening reposted per country must not occupy four result slots.

    Seen live: "Customer service manager (GR) / (CY) / (UK) / (PT)" from the
    same employer filled positions 1-4, all with identical scores.
    """

    def _campaign(self, countries):
        return [
            job(
                title=f"Customer service manager ({code})",
                company="ParcelHero",
                location=f"Remote — {name}",
                description="Customer service manager. Operations and logistics. English required.",
                url=f"https://jobicy.com/j/pc-{code.lower()}",
                source="Jobicy",
            )
            for code, name in countries
        ]

    def test_country_variants_collapse_into_one(self):
        jobs = self._campaign([("GR", "Greece"), ("CY", "Cyprus"),
                               ("UK", "UK"), ("PT", "Portugal")])
        unique, removed = deduplicate_jobs(jobs)
        assert len(unique) == 1
        assert removed == 3
        assert unique[0]["variant_count"] == 4

    def test_variant_locations_are_recorded(self):
        unique, _ = deduplicate_jobs(self._campaign([("GR", "Greece"), ("PT", "Portugal")]))
        assert len(unique[0]["variant_locations"]) == 2

    def test_most_eligible_variant_is_kept(self):
        jobs = self._campaign([("GR", "Greece"), ("RO", "Romania")])
        unique, _ = deduplicate_jobs(jobs)
        kept = unique[0]["location"]["display_name"]
        assert "Romania" in kept, "the variant he can actually work from must win"

    def test_different_roles_are_not_merged(self):
        jobs = self._campaign([("GR", "Greece")]) + [
            job(title="Back Office Specialist", company="Other Co",
                location="Timisoara, Romania", description="Back office.",
                url="https://x.com/9", source="Jooble")
        ]
        unique, removed = deduplicate_jobs(jobs)
        assert len(unique) == 2 and removed == 0

    def test_same_title_different_employer_is_not_merged(self):
        jobs = [
            job(title="Customer service manager (GR)", company="ParcelHero",
                location="Remote — Greece", description="A", url="https://x.com/1", source="Jobicy"),
            job(title="Customer service manager (GR)", company="Rival Ltd",
                location="Remote — Greece", description="B", url="https://x.com/2", source="Jobicy"),
        ]
        unique, _ = deduplicate_jobs(jobs)
        assert len(unique) == 2

    def test_kept_location_is_listed_among_variants(self):
        unique, _ = deduplicate_jobs(self._campaign([("GR", "Greece"), ("RO", "Romania")]))
        locations = unique[0]["variant_locations"]
        assert any("Romania" in loc for loc in locations)
        assert any("Greece" in loc for loc in locations)


class TestScoreAndFilter:
    def test_min_score_filter(self):
        jobs = [job(), job(title="Random unrelated role", url="https://x.com/2",
                           location="", description="")]
        kept, stats = score_and_filter(jobs, Profile(), FilterOptions(min_score=40))
        assert all(j["_match"].score >= 40 for j in kept)

    def test_location_filter(self):
        jobs = [job(location="Timisoara, Romania"), job(url="https://x.com/2", location="Berlin, Germany")]
        kept, _ = score_and_filter(jobs, Profile(), FilterOptions(min_score=0, location_filter="Romania"))
        assert len(kept) == 1

    def test_hide_applied(self):
        jobs = [job(url="https://example.com/1")]
        kept, stats = score_and_filter(
            jobs, Profile(),
            FilterOptions(min_score=0, hide_applied=True, applied_urls=["https://www.example.com/1?utm_source=x"]),
        )
        assert kept == [] and stats["filtered_applied"] == 1

    def test_sorting_by_score(self):
        jobs = [
            job(title="Unrelated", url="https://x.com/2", location="", description=""),
            job(title="Arabic Customer Support Specialist",
                description="arabic required english required excel sap, salary 6500 RON per month"),
        ]
        kept, _ = score_and_filter(jobs, Profile(), FilterOptions(min_score=0))
        assert kept[0]["_match"].score >= kept[-1]["_match"].score

    def test_salary_only_filter(self):
        jobs = [job(), job(url="https://x.com/2", salary_text="6000 RON per month")]
        kept, _ = score_and_filter(jobs, Profile(), FilterOptions(min_score=0, only_with_salary=True))
        assert len(kept) == 1

    def test_stats_are_reported(self):
        jobs = [job(title="Senior Java Developer")]
        kept, stats = score_and_filter(jobs, Profile(), FilterOptions(min_score=0))
        assert stats["rejected_hard"] == 1 and kept == []


class TestDateParsing:
    def test_iso_formats(self):
        assert parse_date("2026-01-15T10:30:00Z") is not None
        assert parse_date("2026-01-15") is not None

    def test_relative(self):
        assert days_since("3 days ago") == 3

    def test_invalid(self):
        assert parse_date("") is None
        assert parse_date("not a date") is None


class TestApplicationStore:
    def test_add_and_retrieve(self, tmp_path):
        store = ApplicationStore(path=str(tmp_path / "a.json"))
        store.add("https://example.com/1", title="Analyst", company="ACME", match_score=80)
        assert len(store) == 1
        assert "https://www.example.com/1?utm_source=x" in store  # canonical match

    def test_status_update(self, tmp_path):
        store = ApplicationStore(path=str(tmp_path / "a.json"))
        store.add("https://example.com/1", title="Analyst")
        store.update("https://example.com/1", status="Interview")
        assert store.get("https://example.com/1").status == "Interview"

    def test_remove(self, tmp_path):
        store = ApplicationStore(path=str(tmp_path / "a.json"))
        store.add("https://example.com/1")
        assert store.remove("https://example.com/1") is True
        assert len(store) == 0

    def test_persistence_roundtrip(self, tmp_path):
        path = str(tmp_path / "a.json")
        store = ApplicationStore(path=path)
        store.add("https://example.com/1", title="Analyst", company="ACME")
        reloaded = ApplicationStore.load(path)
        assert len(reloaded) == 1
        assert reloaded.get("https://example.com/1").title == "Analyst"

    def test_readonly_filesystem_does_not_raise(self):
        store = ApplicationStore(path="/proc/definitely-not-writable/a.json")
        store.add("https://example.com/1", title="Analyst")
        assert len(store) == 1          # still tracked in memory
        assert store.persistent is False

    def test_legacy_format_is_readable(self, tmp_path):
        path = tmp_path / "a.json"
        path.write_text(json.dumps({
            "https://example.com/1": {
                "title": "Old", "company": "X", "date": "2026-01-01 10:00",
                "status": "Applied", "notes": "",
            }
        }))
        store = ApplicationStore.load(str(path))
        assert store.get("https://example.com/1").applied_at == "2026-01-01 10:00"

    def test_stats(self, tmp_path):
        store = ApplicationStore(path=str(tmp_path / "a.json"))
        store.add("https://example.com/1")
        store.add("https://example.com/2")
        store.update("https://example.com/2", status="Interview")
        stats = store.stats()
        assert stats["Total"] == 2 and stats["Interview"] == 1 and stats["Active"] == 2

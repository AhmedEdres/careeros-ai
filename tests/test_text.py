import pytest

from careeros.text import (
    canonical_url,
    clean_html_text,
    contains_any,
    contains_phrase,
    normalize_location,
    normalize_text,
    safe_company_name,
    text_hash,
    truncate,
    valid_url,
)


class TestNormalizeText:
    def test_strips_romanian_diacritics(self):
        assert normalize_text("Timișoara") == "timisoara"
        assert normalize_text("TIMIȘOARA") == "timisoara"
        assert normalize_text("București") == "bucuresti"

    def test_collapses_whitespace(self):
        assert normalize_text("  back    office \n role ") == "back office role"

    def test_handles_none_and_numbers(self):
        assert normalize_text(None) == ""
        assert normalize_text(1500) == "1500"


class TestContainsPhrase:
    def test_whole_word_only(self):
        # The original bug: "eu" matched inside "deutschland".
        assert not contains_phrase("deutschland berlin", "eu")
        assert contains_phrase("remote eu only", "eu")

    def test_no_substring_false_positives(self):
        assert not contains_phrase("asterisk usage", "risk")
        assert not contains_phrase("sapient consulting", "sap")
        assert contains_phrase("we use sap daily", "sap")

    def test_flexible_separators(self):
        assert contains_phrase("back-office team", "back office")
        assert contains_phrase("back  office team", "back office")

    def test_contains_any(self):
        assert contains_any("customer support role", ["logistics", "customer support"])
        assert not contains_any("customer support role", ["logistics", "welding"])


class TestCleanHtml:
    def test_removes_tags_and_entities(self):
        html = "<p>Hello&nbsp;<b>world</b></p><script>evil()</script>"
        cleaned = clean_html_text(html)
        assert "evil" not in cleaned
        assert "Hello" in cleaned and "world" in cleaned
        assert "<" not in cleaned

    def test_preserves_block_structure(self):
        assert "\n" in clean_html_text("<li>One</li><li>Two</li>")


class TestCanonicalUrl:
    def test_strips_tracking_and_www(self):
        a = canonical_url("https://www.example.com/job/1?utm_source=x&gclid=y")
        b = canonical_url("http://example.com/job/1/")
        assert a == b

    def test_keeps_meaningful_query(self):
        assert "id=42" in canonical_url("https://example.com/job?id=42&utm_medium=cpc")

    def test_empty_input(self):
        assert canonical_url("") == ""
        assert canonical_url(None) == ""


class TestMisc:
    def test_safe_company_name(self):
        assert safe_company_name({"display_name": "ACME"}) == "ACME"
        assert safe_company_name("") == "Company not listed"
        assert safe_company_name(None) == "Company not listed"

    def test_normalize_location_adds_country(self):
        assert normalize_location("Timisoara") == "Timisoara, Romania"
        assert normalize_location("") == "Timisoara, Romania"
        assert normalize_location("Berlin") == "Berlin"

    def test_valid_url(self):
        assert valid_url("https://example.com/x")
        assert not valid_url("javascript:alert(1)")
        assert not valid_url("")

    def test_text_hash_ignores_punctuation_and_case(self):
        assert text_hash("Back-Office Agent!") == text_hash("back office agent")

    def test_truncate(self):
        assert truncate("hello world", 50) == "hello world"
        assert truncate("hello world", 7).endswith("…")


class TestCleanHtmlRobustness:
    """clean_html_text must never raise: sources send dicts, None and junk.

    The deployed build crashed with
    "AttributeError: 'dict' object has no attribute ..." inside this function.
    """

    @pytest.mark.parametrize("value", [
        None, "", {}, {"display_name": "x"}, [], 123, 4.5, True, b"bytes",
    ])
    def test_never_raises_on_odd_input(self, value):
        assert isinstance(clean_html_text(value), str)

    def test_nbsp_becomes_a_normal_space(self):
        assert "\u00a0" not in clean_html_text("<p>Hello&nbsp;world</p>")
        assert clean_html_text("<p>Hello&nbsp;world</p>") == "Hello world"

    def test_zero_width_space_removed(self):
        assert "\u200b" not in clean_html_text("a\u200bb")

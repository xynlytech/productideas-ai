from app.services.normalization import deduplicate_signals, is_junk, normalize_batch, normalize_text


class TestNormalizeText:
    def test_lowercase_and_strip(self):
        assert normalize_text("  Hello World  ") == "hello world"

    def test_collapse_spaces(self):
        assert normalize_text("too   many  spaces") == "too many spaces"


class TestIsJunk:
    def test_url_is_junk(self):
        assert is_junk("https://example.com") is True

    def test_short_text_is_junk(self):
        assert is_junk("ab") is True

    def test_normal_text_is_not_junk(self):
        assert is_junk("how to build a saas") is False


class TestNormalizeBatch:
    def test_removes_junk_and_deduplicates(self):
        signals = [
            {"query": "How to build SaaS", "source_type": "autocomplete"},
            {"query": "how to build saas", "source_type": "autocomplete"},
            {"query": "https://spam.com", "source_type": "autocomplete"},
            {"query": "ab", "source_type": "autocomplete"},
            {"query": "productivity tools 2026", "source_type": "trends"},
        ]
        result = normalize_batch(signals)
        queries = [s["query"] for s in result]
        assert len(result) == 2
        assert "how to build saas" in queries
        assert "productivity tools 2026" in queries


class TestDeduplicateSignals:
    def test_exact_dedup(self):
        signals = [
            {"query": "test query"},
            {"query": "test query"},
            {"query": "other query"},
        ]
        result = deduplicate_signals(signals)
        assert len(result) == 2

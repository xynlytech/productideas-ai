from app.services.clustering import _infer_category, cluster_signals


class TestClusterSignals:
    def test_empty_input(self):
        assert cluster_signals([]) == []

    def test_single_signal_produces_cluster(self):
        signals = [{"query": "ai productivity tool", "source_type": "autocomplete"}]
        clusters = cluster_signals(signals, min_samples=1)
        assert len(clusters) >= 1
        assert clusters[0]["label"] == "ai productivity tool"

    def test_similar_signals_cluster_together(self):
        signals = [
            {"query": "best ai writing tool", "source_type": "autocomplete"},
            {"query": "ai writing tools 2026", "source_type": "autocomplete"},
            {"query": "ai writing assistant", "source_type": "trends"},
            {"query": "completely unrelated cooking recipe", "source_type": "trends"},
        ]
        clusters = cluster_signals(signals, eps=0.5, min_samples=2)
        assert len(clusters) >= 1


class TestInferCategory:
    def test_saas_detection(self):
        assert _infer_category(["saas tool", "software platform"]) == "SaaS"

    def test_health_detection(self):
        assert _infer_category(["fitness app", "health tracking"]) == "Health & Wellness"

    def test_no_category(self):
        assert _infer_category(["xyzzy foobar baz"]) is None

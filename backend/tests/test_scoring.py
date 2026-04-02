from app.services.scoring import compute_opportunity_score, score_cluster


class TestComputeOpportunityScore:
    def test_high_scores_produce_high_output(self):
        result = compute_opportunity_score(
            demand_growth=90, query_volume=50000, pain_intensity=85,
            momentum=80, competition_saturation=20, confidence=90,
        )
        assert result["opportunity_score"] >= 70
        assert result["score_label"] in ("Very Strong", "Promising")

    def test_low_scores_produce_low_output(self):
        result = compute_opportunity_score(
            demand_growth=10, query_volume=50, pain_intensity=15,
            momentum=10, competition_saturation=90, confidence=20,
        )
        assert result["opportunity_score"] < 30
        assert result["score_label"] == "Low Priority"

    def test_score_clamped_to_100(self):
        result = compute_opportunity_score(
            demand_growth=200, query_volume=999999999, pain_intensity=200,
            momentum=200, competition_saturation=1, confidence=200,
        )
        assert result["opportunity_score"] <= 100

    def test_zero_volume_does_not_crash(self):
        result = compute_opportunity_score(
            demand_growth=50, query_volume=0, pain_intensity=50,
            momentum=50, competition_saturation=50, confidence=50,
        )
        assert result["opportunity_score"] >= 0

    def test_all_fields_present(self):
        result = compute_opportunity_score(
            demand_growth=60, query_volume=1000, pain_intensity=60,
            momentum=60, competition_saturation=40, confidence=70,
        )
        assert "opportunity_score" in result
        assert "demand_growth_score" in result
        assert "competition_score" in result
        assert "pain_intensity_score" in result
        assert "confidence_score" in result
        assert "momentum_score" in result
        assert "query_volume" in result
        assert "score_label" in result
        assert "ranking_reason" in result

    def test_confidence_caveats_generated(self):
        result = compute_opportunity_score(
            demand_growth=50, query_volume=10, pain_intensity=50,
            momentum=50, competition_saturation=90, confidence=20,
        )
        assert result["confidence_caveats"] is not None
        assert "Low confidence" in result["confidence_caveats"]


class TestScoreCluster:
    def test_score_cluster_returns_valid_dict(self):
        cluster_data = {
            "label": "ai productivity tools",
            "keywords": [
                {"keyword": "ai productivity", "weight": 0.9},
                {"keyword": "ai tools", "weight": 0.8},
            ],
            "signals": [
                {"source_type": "google_autocomplete", "query": "ai tools", "raw_data": {}},
                {"source_type": "google_trends", "query": "ai productivity", "raw_data": {}},
            ],
            "category": "Productivity",
        }
        result = score_cluster(cluster_data)
        assert "opportunity_score" in result
        assert 0 <= result["opportunity_score"] <= 100

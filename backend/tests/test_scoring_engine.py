import pytest
from app.services.engine.scoring import MeaningfulChangeEngine
from app.services.engine.trust_proof import TrustProofEngine

def test_normal_noise_scores_low():
    # Minor +0.2% move on low volume and normal volatility
    res = MeaningfulChangeEngine.calculate_attention_score(
        current_price=100.20,
        snapshot_price=100.00,
        volume=500_000,
        avg_volume_20d=1_000_000,
        atr_14d=2.00,
        day_high=100.50,
        day_low=99.80,
        benchmark_delta_pct=0.15,
        user_sensitivity_threshold=60
    )
    assert res.total_score <= 30
    assert res.classification == "normal"
    assert res.is_meaningful is False

def test_extreme_breakout_scores_high():
    # Big +6.5% move on 3.5x volume, breaking day high, diverging from market
    res = MeaningfulChangeEngine.calculate_attention_score(
        current_price=106.50,
        snapshot_price=100.00,
        volume=3_500_000,
        avg_volume_20d=1_000_000,
        atr_14d=1.80,
        day_high=106.50,
        day_low=99.50,
        benchmark_delta_pct=0.10,
        user_sensitivity_threshold=60
    )
    assert res.total_score >= 80
    assert res.classification == "high_attention"
    assert res.is_meaningful is True
    assert res.factors["snapshot_delta"].factor_score > 80
    assert res.factors["volume_anomaly"].factor_score > 75

def test_trust_proof_generation():
    breakdown = MeaningfulChangeEngine.calculate_attention_score(
        current_price=100.30,
        snapshot_price=100.00,
        volume=800_000,
        avg_volume_20d=1_000_000,
        atr_14d=2.50,
        day_high=101.00,
        day_low=99.50,
        benchmark_delta_pct=0.20,
        user_sensitivity_threshold=60
    )
    proof = TrustProofEngine.generate_proof(
        symbol="AAPL",
        company_name="Apple Inc.",
        breakdown=breakdown,
        current_price=100.30,
        snapshot_price=100.00,
        atr_14d=2.50,
        volume=800_000,
        avg_volume_20d=1_000_000
    )
    assert proof.symbol == "AAPL"
    assert proof.attention_score <= 30
    assert len(proof.reasons) >= 3
    assert "No alert was triggered" in proof.verdict

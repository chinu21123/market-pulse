from typing import Dict, Any, Tuple
from app.schemas.engine import AttentionScoreBreakdown, FactorItem

class MeaningfulChangeEngine:
    WEIGHTS = {
        "snapshot_delta": 0.30,
        "volatility_z_score": 0.25,
        "volume_anomaly": 0.20,
        "gap_extremes": 0.15,
        "market_divergence": 0.10,
    }

    @classmethod
    def calculate_attention_score(
        cls,
        current_price: float,
        snapshot_price: float,
        volume: float,
        avg_volume_20d: float,
        atr_14d: float,
        day_high: float,
        day_low: float,
        benchmark_delta_pct: float = 0.0,
        user_sensitivity_threshold: int = 60,
    ) -> AttentionScoreBreakdown:
        """
        Deterministically calculates the Attention Score (0-100)
        based on 5 objective quantitative signals.
        """
        if snapshot_price <= 0:
            snapshot_price = current_price

        # 1. Snapshot Delta Magnitude
        delta_pct = ((current_price - snapshot_price) / snapshot_price) * 100.0
        abs_delta = abs(delta_pct)
        if abs_delta < 0.5:
            f1_score = 10.0
            f1_desc = f"Small move ({abs_delta:.2f}%), within regular noise"
        elif abs_delta < 1.5:
            f1_score = 10.0 + ((abs_delta - 0.5) / 1.0) * 25.0
            f1_desc = f"Moderate move ({abs_delta:.2f}%)"
        elif abs_delta < 3.0:
            f1_score = 35.0 + ((abs_delta - 1.5) / 1.5) * 30.0
            f1_desc = f"Notable price movement ({abs_delta:.2f}%)"
        else:
            f1_score = min(100.0, 65.0 + (abs_delta - 3.0) * 15.0)
            f1_desc = f"Sharp price surge/drop ({abs_delta:.2f}%)"

        # 2. Volatility Deviation (Z-Score)
        expected_vol_pct = max(0.5, (atr_14d / current_price) * 100.0) if current_price > 0 else 1.5
        z_score = abs_delta / expected_vol_pct
        if z_score < 1.0:
            f2_score = max(5.0, z_score * 15.0)
            f2_desc = f"Within 1 standard ATR deviation ({z_score:.2f}σ)"
        elif z_score < 2.0:
            f2_score = 15.0 + (z_score - 1.0) * 30.0
            f2_desc = f"Elevated volatility ({z_score:.2f}σ)"
        elif z_score < 3.0:
            f2_score = 45.0 + (z_score - 2.0) * 30.0
            f2_desc = f"Abnormal volatility expansion ({z_score:.2f}σ)"
        else:
            f2_score = min(100.0, 75.0 + (z_score - 3.0) * 15.0)
            f2_desc = f"Extreme statistical outlier ({z_score:.2f}σ event)"

        # 3. Volume Anomaly Ratio
        expected_vol = max(1.0, avg_volume_20d)
        vol_ratio = volume / expected_vol if volume > 0 else 1.0
        if vol_ratio < 1.0:
            f3_score = max(5.0, vol_ratio * 15.0)
            f3_desc = f"Subdued volume ({vol_ratio:.2f}x average)"
        elif vol_ratio < 1.8:
            f3_score = 15.0 + ((vol_ratio - 1.0) / 0.8) * 25.0
            f3_desc = f"Normal trading pace ({vol_ratio:.2f}x average)"
        elif vol_ratio < 3.0:
            f3_score = 40.0 + ((vol_ratio - 1.8) / 1.2) * 35.0
            f3_desc = f"Elevated liquidity surge ({vol_ratio:.2f}x average)"
        else:
            f3_score = min(100.0, 75.0 + (vol_ratio - 3.0) * 15.0)
            f3_desc = f"Massive institutional volume spike ({vol_ratio:.2f}x average)"

        # 4. Gap and Intraday Extremes
        day_range = max(0.01, day_high - day_low)
        position_in_range = (current_price - day_low) / day_range if day_range > 0 else 0.5
        is_breakout = (position_in_range > 0.95 or position_in_range < 0.05) and abs_delta > 1.2
        if is_breakout:
            f4_score = 85.0
            f4_desc = "Testing or breaking session extreme limits"
        elif abs_delta > 1.8:
            f4_score = 55.0
            f4_desc = "Strong directional impulse in session channel"
        else:
            f4_score = 15.0
            f4_desc = "Normal oscillation within session channel"

        # 5. Sector / Market Divergence (vs SPY)
        divergence = abs(delta_pct - benchmark_delta_pct)
        if divergence < 0.6:
            f5_score = 10.0
            f5_desc = f"Moving in lockstep with broad market ({divergence:.2f}% diff)"
        elif divergence < 2.0:
            f5_score = 10.0 + ((divergence - 0.6) / 1.4) * 40.0
            f5_desc = f"Mild divergence from benchmark ({divergence:.2f}% diff)"
        else:
            f5_score = min(100.0, 50.0 + (divergence - 2.0) * 25.0)
            f5_desc = f"Idiosyncratic decoupling from benchmark ({divergence:.2f}% diff)"

        # Weighted Total
        w = cls.WEIGHTS
        total_raw = (
            w["snapshot_delta"] * f1_score +
            w["volatility_z_score"] * f2_score +
            w["volume_anomaly"] * f3_score +
            w["gap_extremes"] * f4_score +
            w["market_divergence"] * f5_score
        )
        total_score = max(0, min(100, int(round(total_raw))))

        # Classification
        if total_score <= 30:
            classification = "normal"
        elif total_score <= 60:
            classification = "worth_watching"
        elif total_score <= 80:
            classification = "significant"
        else:
            classification = "high_attention"

        is_meaningful = total_score >= user_sensitivity_threshold

        factors = {
            "snapshot_delta": FactorItem(
                name="snapshot_delta",
                label="Snapshot Price Delta",
                weight=w["snapshot_delta"],
                raw_value=round(delta_pct, 2),
                factor_score=round(f1_score, 1),
                weighted_score=round(w["snapshot_delta"] * f1_score, 1),
                description=f1_desc,
            ),
            "volatility_z_score": FactorItem(
                name="volatility_z_score",
                label="Volatility Deviation (σ)",
                weight=w["volatility_z_score"],
                raw_value=round(z_score, 2),
                factor_score=round(f2_score, 1),
                weighted_score=round(w["volatility_z_score"] * f2_score, 1),
                description=f2_desc,
            ),
            "volume_anomaly": FactorItem(
                name="volume_anomaly",
                label="Volume Pace Ratio",
                weight=w["volume_anomaly"],
                raw_value=round(vol_ratio, 2),
                factor_score=round(f3_score, 1),
                weighted_score=round(w["volume_anomaly"] * f3_score, 1),
                description=f3_desc,
            ),
            "gap_extremes": FactorItem(
                name="gap_extremes",
                label="Session Range & Extremes",
                weight=w["gap_extremes"],
                raw_value=round(position_in_range, 2),
                factor_score=round(f4_score, 1),
                weighted_score=round(w["gap_extremes"] * f4_score, 1),
                description=f4_desc,
            ),
            "market_divergence": FactorItem(
                name="market_divergence",
                label="Benchmark Divergence",
                weight=w["market_divergence"],
                raw_value=round(divergence, 2),
                factor_score=round(f5_score, 1),
                weighted_score=round(w["market_divergence"] * f5_score, 1),
                description=f5_desc,
            ),
        }

        return AttentionScoreBreakdown(
            total_score=total_score,
            classification=classification,
            threshold=user_sensitivity_threshold,
            is_meaningful=is_meaningful,
            factors=factors
        )

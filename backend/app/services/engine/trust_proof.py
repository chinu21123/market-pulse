from typing import List
from app.schemas.engine import AttentionScoreBreakdown, WhyNotAlertedProof

class TrustProofEngine:
    @staticmethod
    def generate_proof(
        symbol: str,
        company_name: str,
        breakdown: AttentionScoreBreakdown,
        current_price: float,
        snapshot_price: float,
        atr_14d: float,
        volume: float,
        avg_volume_20d: float,
    ) -> WhyNotAlertedProof:
        """
        Generates an audit trail of why a stock was NOT flagged as an alert,
        providing objective mathematical justification to build user trust.
        """
        delta_pct = ((current_price - snapshot_price) / snapshot_price) * 100.0 if snapshot_price > 0 else 0.0
        abs_delta = abs(delta_pct)
        expected_vol_pct = (atr_14d / current_price) * 100.0 if current_price > 0 else 1.5
        vol_ratio = volume / avg_volume_20d if avg_volume_20d > 0 else 1.0
        z_score = abs_delta / max(0.01, expected_vol_pct)

        reasons: List[str] = []

        # 1. Price movement reason
        if abs_delta < 1.0:
            reasons.append(
                f"Movement was only {delta_pct:+.2f}%, which is well below the meaningful movement threshold."
            )
        else:
            reasons.append(
                f"Movement was {delta_pct:+.2f}%, which while measurable, remains within standard statistical noise."
            )

        # 2. Volatility reason
        if z_score < 1.0:
            reasons.append(
                f"Volatility ratio is {z_score:.2f}σ. This is inside the expected 1-sigma daily ATR band (±{expected_vol_pct:.2f}%)."
            )
        elif z_score < 1.5:
            reasons.append(
                f"Volatility ratio ({z_score:.2f}σ) is slightly elevated but not statistically anomalous."
            )

        # 3. Volume reason
        if vol_ratio < 1.0:
            reasons.append(
                f"Trading volume ({vol_ratio:.2f}x average) is light. Large institutional participants are not driving this move."
            )
        elif vol_ratio < 1.5:
            reasons.append(
                f"Volume pace is normal ({vol_ratio:.2f}x 20-day average), indicating orderly market equilibrium."
            )

        # 4. Overall score context
        if breakdown.total_score < breakdown.threshold:
            reasons.append(
                f"Composite Attention Score evaluated to {breakdown.total_score}/100, below your active alert cutoff of {breakdown.threshold}."
            )
            verdict = (
                f"No alert was triggered because {symbol}'s movement is standard background fluctuation. "
                "Your attention is preserved for genuinely anomalous market events."
            )
        else:
            reasons.append(
                f"Composite Attention Score evaluated to {breakdown.total_score}/100, meeting or exceeding your active alert cutoff of {breakdown.threshold}."
            )
            verdict = f"{symbol} meets your current attention cutoff; review the factor breakdown above."

        return WhyNotAlertedProof(
            symbol=symbol,
            company_name=company_name,
            attention_score=breakdown.total_score,
            threshold=breakdown.threshold,
            price_delta_pct=round(delta_pct, 2),
            expected_volatility_pct=round(expected_vol_pct, 2),
            volume_ratio=round(vol_ratio, 2),
            z_score=round(z_score, 2),
            reasons=reasons,
            verdict=verdict
        )

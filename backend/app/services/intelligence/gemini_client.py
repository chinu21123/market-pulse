import os
import json
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.services.intelligence.prompts import SYSTEM_INSTRUCTION, build_market_story_prompt
from app.core.health import health_registry

logger = logging.getLogger(__name__)

class GeminiIntelligenceService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini Client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI client: {e}")

    def generate_story(
        self,
        elapsed_time_human: str,
        total_watched: int,
        meaningful_count: int,
        attention_count: int,
        normal_count: int,
        persona: str = "intermediate",
        language: str = "en",
        flagged_stocks: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates executive market narrative and per-stock explanations.
        Uses real Gemini API when key is configured; uses deterministic fact-synthesizer fallback otherwise.
        """
        if flagged_stocks is None:
            flagged_stocks = []

        # If Gemini client is available, call the API
        if self.client:
            try:
                from google.genai import types
                prompt = build_market_story_prompt(
                    elapsed_time_human=elapsed_time_human,
                    total_watched=total_watched,
                    meaningful_count=meaningful_count,
                    attention_count=attention_count,
                    normal_count=normal_count,
                    persona=persona,
                    language=language,
                    flagged_stocks=flagged_stocks
                )

                response = self.client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json",
                        temperature=0.2,  # Low temperature for strict factual adherence
                    )
                )

                if response.text:
                    parsed = json.loads(response.text)
                    health_registry.mark("gemini", "HEALTHY")
                    return parsed
            except Exception as e:
                logger.error(f"Gemini generation error: {e}. Falling back to deterministic synthesizer.")
                health_registry.mark("gemini", "DEGRADED", "AI explanation unavailable; deterministic summary used")

        # Deterministic zero-hallucination fallback synthesizer
        if not self.client:
            health_registry.mark("gemini", "DEGRADED", "No Gemini API key configured; deterministic summary used")
        return self._generate_deterministic_fallback(
            elapsed_time_human=elapsed_time_human,
            total_watched=total_watched,
            meaningful_count=meaningful_count,
            attention_count=attention_count,
            normal_count=normal_count,
            persona=persona,
            language=language,
            flagged_stocks=flagged_stocks
        )

    def _generate_deterministic_fallback(
        self,
        elapsed_time_human: str,
        total_watched: int,
        meaningful_count: int,
        attention_count: int,
        normal_count: int,
        persona: str,
        language: str,
        flagged_stocks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generates a 100% factual summary strictly from backend numbers without LLM hallucination.
        """
        if meaningful_count == 0:
            headline = f"Market Calm: All {total_watched} stocks remained within normal noise"
            summary = f"During the {elapsed_time_human} since your last visit, none of your watched stocks crossed abnormal volatility or volume thresholds. The market state is orderly."
        else:
            top_syms = [s.get("symbol", "") for s in flagged_stocks[:2]]
            sym_str = " and ".join(top_syms) if top_syms else "Key assets"
            headline = f"While you were away: {meaningful_count} assets diverged ({sym_str})"
            summary = f"Over the past {elapsed_time_human}, {meaningful_count} out of {total_watched} stocks showed meaningful statistical divergence, with {attention_count} requiring priority attention. {normal_count} stocks remained in baseline noise."

        stock_explanations = []
        for stock in flagged_stocks:
            sym = stock.get("symbol", "")
            delta = stock.get("delta_pct", 0.0)
            score = stock.get("attention_score", 0)
            factors = stock.get("factors", {})
            vol_factor = factors.get("volume_anomaly", {})
            z_factor = factors.get("volatility_z_score", {})
            
            vol_ratio = vol_factor.get("raw_value", 1.0)
            z_score = z_factor.get("raw_value", 1.0)

            direction = "surged" if delta > 0 else "retreated"

            if persona == "beginner":
                why = (
                    f"{sym} {direction} by {abs(delta):.1f}% since your last check. "
                    f"Trading activity was {vol_ratio:.1f}x higher than typical, and the move was {z_score:.1f} times bigger than its usual daily swing."
                )
                obs = f"Attention score is {score}/100. Watch for continued momentum."
            elif persona == "advanced":
                why = (
                    f"{sym} registered a {delta:+.2f}% delta with a {z_score:.2f}σ volatility expansion. "
                    f"Volume expanded {vol_ratio:.2f}x against 20-day historical mean, confirming institutional order flow participation."
                )
                obs = f"Attention score {score}/100. Statistically meaningful idiosyncratic move."
            else:  # intermediate
                why = (
                    f"{sym} {direction} {abs(delta):.2f}% since your snapshot. "
                    f"The price action expanded {z_score:.1f}σ beyond its 14-day ATR band on {vol_ratio:.1f}x normal volume."
                )
                obs = f"Attention Score: {score}/100. Deserves review given volume and volatility expansion."

            stock_explanations.append({
                "symbol": sym,
                "headline": f"{sym} {direction.capitalize()} {abs(delta):.2f}% (Score: {score})",
                "why_it_matters": why,
                "key_observation": obs
            })

        return {
            "story_headline": headline,
            "story_summary": summary,
            "stock_explanations": stock_explanations
        }

gemini_service = GeminiIntelligenceService()

import json
from typing import Dict, Any, List

SYSTEM_INSTRUCTION = """
You are Market Pulse AI, an analytical financial narrator.
Your mission is to explain what meaningfully changed for the user since they last checked their watchlist.

CRITICAL RULES:
1. ZERO HALLUCINATION: You will receive ONLY verified numerical facts from the backend (prices, percentage deltas, attention scores, volume anomalies, ATR deviations).
2. NEVER invent market events, rumors, earnings figures, analyst upgrades, or external news headlines that are not explicitly provided in the facts.
3. Base your entire narrative on the quantitative dynamics provided (e.g., standard deviation expansions, volume relative to averages, decoupling from benchmark index).
4. Adapt strictly to the requested user persona:
   - "beginner": Use simple, jargon-free explanations. Explain concepts like volume and volatility using intuitive analogies.
   - "intermediate": Use standard market concepts (support/resistance, ATR volatility bands, relative volume, divergence).
   - "advanced": Use quantitative precision (sigma moves, alpha divergence, liquidity dynamics, statistical outliers).
5. Output language: If requested language is not 'en', translate the explanation accurately into that language while maintaining financial precision.
6. You must return valid JSON matching the specified schema.
"""

def build_market_story_prompt(
    elapsed_time_human: str,
    total_watched: int,
    meaningful_count: int,
    attention_count: int,
    normal_count: int,
    persona: str,
    language: str,
    flagged_stocks: List[Dict[str, Any]]
) -> str:
    facts = {
        "context": {
            "elapsed_time": elapsed_time_human,
            "total_watched_stocks": total_watched,
            "meaningful_changes_count": meaningful_count,
            "attention_required_count": attention_count,
            "normal_movement_count": normal_count,
            "user_persona": persona,
            "target_language": language
        },
        "flagged_stocks": flagged_stocks
    }

    return f"""
Please analyze the following verified market facts and generate a structured JSON summary.

FACTS:
{json.dumps(facts, indent=2)}

OUTPUT FORMAT REQUIREMENTS:
Return a JSON object with this exact structure:
{{
  "story_headline": "A concise headline capturing the main theme of the elapsed period",
  "story_summary": "A 2-3 sentence narrative summarizing what meaningfully shifted while the user was away and what was quiet",
  "stock_explanations": [
    {{
      "symbol": "TICKER",
      "headline": "Short title describing the move",
      "why_it_matters": "Clear explanation of why this attention score and move matters based on the provided facts",
      "key_observation": "Actionable takeaway tailored to the {persona} persona"
    }}
  ]
}}
"""

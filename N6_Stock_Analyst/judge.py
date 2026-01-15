from __future__ import annotations

from typing import Any, Dict

from utils.json_parser import parse_json


def judge_n6_quality(llm: Any, analysis: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "summary": analysis.get("summary"),
        "price_move": analysis.get("price_move"),
        "trend": analysis.get("trend"),
        "indicators": analysis.get("indicators"),
        "volume_analysis": analysis.get("volume_analysis"),
        "risk_notes": analysis.get("risk_notes"),
        "llm_chart_analysis": analysis.get("llm_chart_analysis"),
    }
    prompt = (
        "You are a strict evaluator of technical analysis outputs.\n"
        "Score each item between 0 and 1 and return JSON only with keys:\n"
        "consistency, indicator_coverage, trend_consistency, advice_free, clarity, notes.\n"
        "- consistency: summary matches the structured data.\n"
        "- indicator_coverage: RSI/MACD/Bollinger are present and described.\n"
        "- trend_consistency: trend matches pct_change direction.\n"
        "- advice_free: 1 if no buy/sell advice, else 0.\n"
        "- clarity: concise and readable.\n"
        f"INPUT:\n{payload}"
    )

    try:
        response = llm.invoke(prompt)
        content = response.content if isinstance(response.content, str) else str(response.content)
        parsed = parse_json(content)
        if not isinstance(parsed, dict):
            raise ValueError("Judge output is not a dict.")
    except Exception as exc:
        return {
            "consistency": 0.0,
            "indicator_coverage": 0.0,
            "trend_consistency": 0.0,
            "advice_free": 0.0,
            "clarity": 0.0,
            "notes": f"judge_failed: {exc}",
        }

    return {
        "consistency": round(_clamp01(parsed.get("consistency")) * 100, 1),
        "indicator_coverage": round(_clamp01(parsed.get("indicator_coverage")) * 100, 1),
        "trend_consistency": round(_clamp01(parsed.get("trend_consistency")) * 100, 1),
        "advice_free": round(_clamp01(parsed.get("advice_free")) * 100, 1),
        "clarity": round(_clamp01(parsed.get("clarity")) * 100, 1),
        "notes": parsed.get("notes", ""),
    }


def _clamp01(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0

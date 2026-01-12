from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from utils.json_parser import parse_json

from .prompt import NODE10_REPORT_PROMPT


def node10_loss_review_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node10: N6~N9 결과를 기반으로 손실 복기 리포트를 생성합니다.
    """
    payload = {
        "layer1_stock": state.get("layer1_stock"),
        "layer2_buy_date": state.get("layer2_buy_date"),
        "layer2_sell_date": state.get("layer2_sell_date"),
        "layer3_decision_basis": state.get("layer3_decision_basis"),
        "n6_stock_analysis": state.get("n6_stock_analysis"),
        "n7_news_analysis": state.get("n7_news_analysis"),
        "n8_concept_explanation": state.get("n8_concept_explanation"),
        "n9_fallback_response": state.get("n9_fallback_response"),
    }

    llm = get_solar_chat()
    messages = [
        SystemMessage(content=NODE10_REPORT_PROMPT),
        HumanMessage(content=f"Write the report using this input:\n{payload}"),
    ]

    try:
        response = llm.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)
    except Exception as exc:
        return {"n10_loss_review_report": _fallback(f"LLM 호출 실패: {exc}")}

    parsed = parse_json(raw)
    if not isinstance(parsed, dict):
        return {"n10_loss_review_report": _fallback("JSON 파싱 실패")}

    return {"n10_loss_review_report": _normalize(parsed)}


def _normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_title": str(data.get("report_title", "손실 복기 리포트")),
        "summary": str(data.get("summary", "요약을 생성하지 못했습니다.")),
        "technical_analysis": str(data.get("technical_analysis", "")),
        "news_market_context": str(data.get("news_market_context", "")),
        "learning_points": _coerce_list(data.get("learning_points")),
        "mistake_pattern": str(data.get("mistake_pattern", "")),
        "reflection_actions": _coerce_list(data.get("reflection_actions")),
        "uncertainty_level": data.get("uncertainty_level", "high"),
    }


def _coerce_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def _fallback(reason: str) -> Dict[str, Any]:
    return {
        "report_title": "손실 복기 리포트",
        "summary": f"리포트를 생성하지 못했습니다. ({reason})",
        "technical_analysis": "",
        "news_market_context": "",
        "learning_points": [],
        "mistake_pattern": "",
        "reflection_actions": [],
        "uncertainty_level": "high",
    }

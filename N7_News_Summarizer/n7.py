from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from .prompt import NODE7_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.safety import contains_advice
from utils.validator import validate_node7


def node7_news_summarizer(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_solar_chat()

    payload = {
        "query": state.get("query") or state.get("layer1_stock"),
        "date_range": state.get("date_range")
        or f"{state.get('layer2_buy_date')} ~ {state.get('layer2_sell_date')}",
        "context": state.get("context") or state.get("layer3_decision_basis"),
    }

    messages = [
        SystemMessage(content=NODE7_SYSTEM_PROMPT),
        HumanMessage(content=f"뉴스 요약을 만들어 주세요.\n{payload}"),
    ]

    response = llm.invoke(messages)
    raw = response.content

    if contains_advice(raw):
        return {"n7_news_summary": fallback_result(payload)}

    parsed = parse_json(raw)
    if not parsed:
        return {"n7_news_summary": fallback_result(payload)}

    if not validate_node7(parsed):
        return {"n7_news_summary": fallback_result(payload)}

    return {"n7_news_summary": parsed}


def fallback_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "news_summary": {
            "query": str(payload.get("query") or "unknown"),
            "key_events": [
                {
                    "headline": "뉴스 데이터를 찾지 못했습니다.",
                    "source": "unknown",
                    "date": "unknown",
                    "summary": "외부 뉴스 API 연동 전입니다.",
                }
            ],
            "sentiment": "neutral",
            "impact_assessment": "뉴스 맥락을 확인할 수 없습니다.",
            "uncertainty_level": "high",
        }
    }

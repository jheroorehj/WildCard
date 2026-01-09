from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from .prommpt import NODE6_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.safety import contains_advice
from utils.validator import validate_node6


def node6_stock_analyst(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_solar_chat()

    payload = {
        "layer1_stock": state.get("layer1_stock"),
        "layer2_buy_date": state.get("layer2_buy_date"),
        "layer2_sell_date": state.get("layer2_sell_date"),
        "layer3_decision_basis": state.get("layer3_decision_basis"),
    }

    messages = [
        SystemMessage(content=NODE6_SYSTEM_PROMPT),
        HumanMessage(content=f"주가 흐름과 지표를 요약해 주세요.\n{payload}"),
    ]

    response = llm.invoke(messages)
    raw = response.content

    if contains_advice(raw):
        return {"n6_stock_analysis": fallback_result()}

    parsed = parse_json(raw)
    if not parsed:
        return {"n6_stock_analysis": fallback_result()}

    if not validate_node6(parsed):
        return {"n6_stock_analysis": fallback_result()}

    return {"n6_stock_analysis": parsed}


def fallback_result() -> Dict[str, Any]:
    return {
        "stock_analysis": {
            "summary": "주가 흐름 정보를 확보하지 못했습니다.",
            "price_move": {
                "start_price": "unknown",
                "end_price": "unknown",
                "pct_change": "unknown",
            },
            "trend": "sideways",
            "indicators": [
                {
                    "name": "bollinger_band",
                    "value": "unknown",
                    "interpretation": "지표 값을 계산하지 못했습니다.",
                }
            ],
            "risk_notes": ["데이터 소스가 연결되지 않았습니다."],
            "uncertainty_level": "high",
        }
    }

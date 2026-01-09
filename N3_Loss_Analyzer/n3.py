from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_solar_chat
from prommpt import NODE3_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.validator import validate_node3
from utils.safety import contains_advice


def node3_loss_analyzer(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_solar_chat()

    payload = {
        "loss_case": state.get("loss_case"),
        "decision_context": state.get("decision_context"),
        "n6_stock_analysis": state.get("n6_stock_analysis"),
        "n7_news_analysis": state.get("n7_news_analysis"),
    }

    messages = [
        SystemMessage(content=NODE3_SYSTEM_PROMPT),
        HumanMessage(content=f"입력 데이터:\n{payload}")
    ]

    response = llm.invoke(messages)
    raw = response.content

    if contains_advice(raw):
        return {"n3_loss_diagnosis": fallback_result()}

    parsed = parse_json(raw)
    if not parsed:
        return {"n3_loss_diagnosis": fallback_result()}

    if not validate_node3(parsed):
        return {"n3_loss_diagnosis": fallback_result()}

    return {"n3_loss_diagnosis": parsed}


def fallback_result() -> Dict[str, Any]:
    return {
        "loss_factors": [
            {
                "type": "information_bias",
                "description": "입력 정보가 제한되어 명확한 원인 진단이 어렵습니다.",
                "evidence": {
                    "source": "user_context",
                    "indicator": "bollinger_band",
                    "detail": "의사결정 근거 정보 부족",
                    "band_position": "unknown",
                    "related_period": "whole_period"
                }
            }
        ],
        "behavior_patterns": [],
        "knowledge_gaps": ["손실 복기 프레임워크"],
        "conversation_intent_hint": ["general_chat"],
        "uncertainty_level": "high"
    }

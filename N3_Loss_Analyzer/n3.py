from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_solar_chat
from .prommpt import NODE3_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.validator import validate_node3
from utils.safety import contains_advice


def node3_loss_analyzer(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_solar_chat()

    payload = {
        "layer1_stock": state.get("layer1_stock"),
        "layer2_buy_date": state.get("layer2_buy_date"),
        "layer2_sell_date": state.get("layer2_sell_date"),
        "layer3_decision_basis": state.get("layer3_decision_basis"),
    }

    messages = [
        SystemMessage(content=NODE3_SYSTEM_PROMPT),
        HumanMessage(content=f"레이어 1~3 입력만으로 손실을 분석해 주세요.\n{payload}"),
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
                "description": "사용자가 손실을 평가할 때 제한된 지표나 뉴스에 의존했을 수 있습니다.",
                "evidence": {
                    "source": "user_context",
                    "indicator": "bollinger_band",
                    "detail": "의사결정 근거가 명확하지 않고 지표가 검증되지 않았습니다.",
                    "band_position": "unknown",
                    "related_period": "whole_period",
                },
            }
        ],
        "behavior_patterns": [],
        "knowledge_gaps": ["위험 지표 검토가 충분하지 않음"],
        "conversation_intent_hint": ["일반_대화"],
        "uncertainty_level": "high",
    }

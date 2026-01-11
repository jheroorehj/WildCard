from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from .prompt import NODE8_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.safety import contains_advice
from utils.validator import validate_node8


def node8_concept_explainer(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_solar_chat()

    payload = {
        "term": state.get("term") or state.get("concept") or state.get("layer3_decision_basis"),
        "context": state.get("context") or "",
    }

    messages = [
        SystemMessage(content=NODE8_SYSTEM_PROMPT),
        HumanMessage(content=f"용어를 설명해 주세요.\n{payload}"),
    ]

    response = llm.invoke(messages)
    raw = response.content

    if contains_advice(raw):
        return {"n8_concept_explanation": fallback_result(payload)}

    parsed = parse_json(raw)
    if not parsed:
        return {"n8_concept_explanation": fallback_result(payload)}

    if not validate_node8(parsed):
        return {"n8_concept_explanation": fallback_result(payload)}

    return {"n8_concept_explanation": parsed}


def fallback_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    term = payload.get("term") or "unknown"
    return {
        "concept_explanation": {
            "term": str(term),
            "short_definition": "간단 정의를 생성하지 못했습니다.",
            "beginner_explanation": "외부 지식 리소스가 연결되지 않았습니다.",
            "examples": [],
            "related_terms": [],
            "uncertainty_level": "high",
        }
    }

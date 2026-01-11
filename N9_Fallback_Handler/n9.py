from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from .prompt import NODE9_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.safety import contains_advice
from utils.validator import validate_node9


def node9_fallback_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_solar_chat()

    payload = {
        "user_message": state.get("user_message") or state.get("message") or "",
        "context": state.get("context") or "",
    }

    messages = [
        SystemMessage(content=NODE9_SYSTEM_PROMPT),
        HumanMessage(content=f"자연스럽게 응답해 주세요.\n{payload}"),
    ]

    response = llm.invoke(messages)
    raw = response.content

    if contains_advice(raw):
        return {"n9_fallback": fallback_result()}

    parsed = parse_json(raw)
    if not parsed:
        return {"n9_fallback": fallback_result()}

    if not validate_node9(parsed):
        return {"n9_fallback": fallback_result()}

    return {"n9_fallback": parsed}


def fallback_result() -> Dict[str, Any]:
    return {
        "fallback_response": {
            "message": "지금은 자세한 분석 대신 대화를 이어갈게요. 궁금한 점을 알려주세요.",
            "intent_hint": "general_chat",
        }
    }

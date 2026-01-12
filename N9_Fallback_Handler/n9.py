# n9.py
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from .prompt import NODE9_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.safety import contains_advice
from utils.validator import validate_node9


def node9_fallback_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    입력: Node5에서 general_chat으로 분류된 JSON state
    출력: Node9 전용 JSON
    """
    llm = get_solar_chat()

    payload = {
        "user_message": state["user_message"],
        "context": state.get("context", ""),
    }

    messages = [
        SystemMessage(content=NODE9_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "아래 입력을 바탕으로 응답하세요.\n"
                "출력은 반드시 JSON만 반환하세요.\n"
                f"{payload}"
            )
        ),
    ]

    response = llm.invoke(messages)
    raw = response.content if isinstance(response.content, str) else str(response.content)

    parsed = parse_json(raw)
    if not isinstance(parsed, dict):
        return _fallback()

    if not validate_node9(parsed):
        return _fallback()

    return parsed


def _fallback() -> Dict[str, Any]:
    return {
        "fallback_response": {
            "message": "지금은 대화를 이어가는 단계입니다. 궁금한 점을 말해 주세요.",
            "intent_hint": "general_chat"
        }
    }

from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from utils.json_parser import parse_json

from .prompt import NODE1_SYSTEM_PROMPT


REQUIRED_FIELDS = (
    "layer1_stock",
    "layer2_buy_date",
    "layer2_sell_date",
    "layer3_decision_basis",
)


def node1_input_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node1: N6/N7에 전달할 입력을 정규화해 JSON 페이로드로 반환합니다.
    """
    missing = _missing_required(state, REQUIRED_FIELDS)
    if missing:
        return {
            "n1_input_error": {
                "message": "missing required input",
                "fields": missing,
            }
        }

    payload = {
        "layer1_stock": state.get("layer1_stock"),
        "layer2_buy_date": state.get("layer2_buy_date"),
        "layer2_sell_date": state.get("layer2_sell_date"),
        "layer3_decision_basis": state.get("layer3_decision_basis"),
    }

    llm = get_solar_chat()
    messages = [
        SystemMessage(content=NODE1_SYSTEM_PROMPT),
        HumanMessage(content=f"Build the JSON payloads:\n{payload}"),
    ]

    try:
        response = llm.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)
    except Exception:
        return _fallback_payload(payload)

    parsed = parse_json(raw)
    if not _validate_output(parsed):
        return _fallback_payload(payload)

    return parsed


def _missing_required(state: Dict[str, Any], keys: List[str]) -> List[str]:
    missing = []
    for key in keys:
        value = state.get(key)
        if not isinstance(value, str) or not value.strip():
            missing.append(key)
    return missing


def _validate_output(data: Any) -> bool:
    if not isinstance(data, dict):
        return False

    n6_input = data.get("n6_input")
    n7_input = data.get("n7_input")
    if not isinstance(n6_input, dict) or not isinstance(n7_input, dict):
        return False

    for key in ("ticker", "buy_date", "sell_date"):
        if not isinstance(n6_input.get(key), str):
            return False

    for key in ("ticker", "buy_date", "user_belief"):
        if not isinstance(n7_input.get(key), str):
            return False

    if set(data.keys()) != {"n6_input", "n7_input"}:
        return False

    return True


def _fallback_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "n6_input": {
            "ticker": payload.get("layer1_stock", ""),
            "buy_date": payload.get("layer2_buy_date", ""),
            "sell_date": payload.get("layer2_sell_date", ""),
        },
        "n7_input": {
            "ticker": payload.get("layer1_stock", ""),
            "buy_date": payload.get("layer2_buy_date", ""),
            "user_belief": payload.get("layer3_decision_basis", ""),
        },
    }

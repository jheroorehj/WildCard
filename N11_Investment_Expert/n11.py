from __future__ import annotations

import json
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from utils.json_parser import parse_json


def _compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _sanitize_json_text(raw: str) -> str:
    sanitized_chars = []
    in_string = False
    escape = False
    for ch in raw:
        if escape:
            sanitized_chars.append(ch)
            escape = False
            continue
        if ch == "\\":
            sanitized_chars.append(ch)
            escape = True
            continue
        if ch == "\"":
            in_string = not in_string
            sanitized_chars.append(ch)
            continue
        if in_string and ch == "\n":
            sanitized_chars.append("\\n")
            continue
        sanitized_chars.append(ch)
    return "".join(sanitized_chars)


def node11_investment_expert(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    N11: 분석 결과를 기반으로 질문에 답하는 투자 전문가 노드.
    """
    if not state.get("chat_mode"):
        print("[N11] chat_mode disabled; skipping")
        return {}

    question = (state.get("user_message") or "").strip()
    if not question:
        print("[N11] empty question")
        return {
            "n11_chat_response": {"message": "질문이 비어 있습니다."},
            "used_analysis": False,
        }

    analysis_result = state.get("analysis_result") or {}
    chat_history: List[Dict[str, Any]] = state.get("chat_history") or []

    system_prompt = (
        "당신은 투자 손실 분석 전문가입니다. "
        "주어진 분석 결과를 근거로 사용자의 질문에 한국어로 답하세요. "
        "과도한 확신은 피하고, 매수/매도 추천은 하지 마세요. "
        "아래 JSON만 출력하세요.\n"
        "{\n"
        '  "summary": "2문장 이내 요약",\n'
        '  "detail": "필요한 상세 설명"\n'
        "}"
    )

    messages = [SystemMessage(content=system_prompt)]
    history_text = "\n".join(
        [f"{item.get('role')}: {item.get('content')}" for item in chat_history]
    )
    prompt = (
        "분석 결과:\n"
        f"{_compact_json(analysis_result)}\n\n"
        "대화 기록:\n"
        f"{history_text}\n\n"
        f"사용자 질문: {question}"
    )
    messages.append(HumanMessage(content=prompt))

    llm = get_solar_chat()
    try:
        response = llm.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)
    except Exception as exc:
        raw = f'{{"summary": "", "detail": "답변을 생성하지 못했습니다. ({exc})"}}'

    parsed = parse_json(raw)
    if parsed is None and raw.strip().startswith("{"):
        try:
            parsed = json.loads(_sanitize_json_text(raw))
        except Exception:
            parsed = None
    if isinstance(parsed, dict):
        summary = str(parsed.get("summary", "")).strip()
        detail = str(parsed.get("detail", "")).strip()
    else:
        summary = ""
        detail = raw

    print("[N11] response generated")
    return {
        "n11_chat_response": {
            "summary": summary,
            "detail": detail,
        },
        "used_analysis": True,
    }

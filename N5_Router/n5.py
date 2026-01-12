from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from typing import Any, Dict, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from utils.json_parser import parse_json

from .prompt import NODE5_ROUTER_PROMPT


def _run_node(node_name: str, payload: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    if node_name == "N6":
        from N6_Stock_Analyst.n6 import node6_stock_analyst

        return node_name, node6_stock_analyst(payload)

    if node_name == "N7":
        from N7_News_Summarizer.n7 import node7_news_summarizer

        return node_name, node7_news_summarizer(payload)

    if node_name == "N8":
        from N8_Concept_Explainer.n8 import node8_concept_explainer

        return node_name, node8_concept_explainer(payload)

    if node_name == "N9":
        from N9_Fallback_Handler.n9 import node9_fallback_handler

        return node_name, node9_fallback_handler(payload)

    return node_name, {"error": f"Unknown node: {node_name}"}


def _build_n8_fallback(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("mode") in {"term", "learning"}:
        payload = {
            "mode": state.get("mode"),
            "term": state.get("term"),
            "concept": state.get("concept"),
            "investment_pattern": state.get("investment_pattern"),
            "loss_causes": state.get("loss_causes", []),
            "context": state.get("context", ""),
            "layer3_decision_basis": state.get("layer3_decision_basis"),
        }
        return {k: v for k, v in payload.items() if v is not None}

    investment_pattern = state.get("investment_pattern") or state.get("layer3_decision_basis")
    return {
        "mode": "learning",
        "investment_pattern": investment_pattern,
        "loss_causes": state.get("loss_causes", []),
        "context": state.get("context", ""),
    }


def _merge_payload(fallback: Dict[str, Any], candidate: Any) -> Dict[str, Any]:
    if not isinstance(candidate, dict):
        return dict(fallback)

    merged = dict(fallback)
    for key, value in candidate.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        merged[key] = value
    return merged


def _route_with_llm(state: Dict[str, Any]) -> Dict[str, Any] | None:
    payload = {
        "layer1_stock": state.get("layer1_stock"),
        "layer2_buy_date": state.get("layer2_buy_date"),
        "layer2_sell_date": state.get("layer2_sell_date"),
        "layer3_decision_basis": state.get("layer3_decision_basis"),
        "user_message": state.get("user_message"),
        "context": state.get("context", ""),
        "n3_loss_diagnosis": state.get("n3_loss_diagnosis", {}),
        "loss_causes": state.get("loss_causes", []),
    }

    llm = get_solar_chat()
    messages = [
        SystemMessage(content=NODE5_ROUTER_PROMPT),
        HumanMessage(content=f"Route the following input:\n{payload}"),
    ]
    response = llm.invoke(messages)
    raw = response.content if isinstance(response.content, str) else str(response.content)
    return parse_json(raw)


def node5_parallel_router(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node5: N3 결과를 바탕으로 N6~N9을 멀티프로세싱으로 병렬 실행.
    """
    base_payload = {
        "layer1_stock": state.get("layer1_stock"),
        "layer2_buy_date": state.get("layer2_buy_date"),
        "layer2_sell_date": state.get("layer2_sell_date"),
        "layer3_decision_basis": state.get("layer3_decision_basis"),
        "case_id": state.get("case_id"),
        "context": state.get("context", ""),
    }

    n3_guideline = state.get("n3_loss_diagnosis", {})
    fallback_payloads = {
        "N6": dict(base_payload),
        "N7": {
            **base_payload,
            "n3_loss_analysis": n3_guideline,
        },
        "N8": _build_n8_fallback({**base_payload, **state}),
        "N9": {
            "user_message": state.get("user_message")
            or state.get("layer3_decision_basis")
            or "사용자 메시지가 제공되지 않았습니다.",
            "context": state.get("context", ""),
        },
    }

    routed = _route_with_llm(state)
    payloads = {
        "N6": _merge_payload(fallback_payloads["N6"], routed.get("n6_input") if isinstance(routed, dict) else None),
        "N7": _merge_payload(fallback_payloads["N7"], routed.get("n7_input") if isinstance(routed, dict) else None),
        "N8": _merge_payload(fallback_payloads["N8"], routed.get("n8_input") if isinstance(routed, dict) else None),
        "N9": _merge_payload(fallback_payloads["N9"], routed.get("n9_input") if isinstance(routed, dict) else None),
    }

    results: Dict[str, Dict[str, Any]] = {}
    ctx = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=4, mp_context=ctx) as executor:
        futures = {executor.submit(_run_node, name, payload): name for name, payload in payloads.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                _, result = future.result()
                results[name] = result
            except Exception as exc:
                results[name] = {
                    "error": f"{name} 실행 실패: {exc}",
                    "uncertainty_level": "high",
                }

    merged: Dict[str, Any] = {}
    merged.update(results.get("N6", {}))
    merged.update(results.get("N7", {}))
    merged.update(results.get("N8", {}))

    n9_result = results.get("N9", {})
    if "fallback_response" in n9_result:
        merged["n9_fallback_response"] = n9_result
    else:
        merged["n9_fallback_response"] = {
            "fallback_response": n9_result.get(
                "fallback_response",
                {
                    "message": "폴백 응답을 생성하지 못했습니다.",
                    "intent_hint": "general_chat",
                },
            )
        }

    return merged

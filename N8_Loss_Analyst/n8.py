# -*- coding: utf-8 -*-
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from utils.json_parser import parse_json
from utils.safety import contains_advice
from utils.validator import validate_node8
from .prompt import NODE8_LOSS_ANALYST_PROMPT


def node8_loss_analyst(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    N8: loss analyst.
    Uses N6/N7 outputs to derive loss causes and market context.
    """
    payload = {
        "ticker": state.get("layer1_stock"),
        "buy_date": state.get("layer2_buy_date"),
        "sell_date": state.get("layer2_sell_date"),
        "user_decision_basis": state.get("layer3_decision_basis"),
        "n6_stock_analysis": state.get("n6_stock_analysis"),
        "n7_news_analysis": state.get("n7_news_analysis"),
    }

    llm = get_solar_chat()
    messages = [
        SystemMessage(content=NODE8_LOSS_ANALYST_PROMPT),
        HumanMessage(content=f"Build JSON using the following input.\n{payload}"),
    ]

    try:
        response = llm.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)
    except Exception as exc:
        return _fallback(f"LLM call failed: {exc}")

    if contains_advice(raw):
        return _fallback("Blocked due to investment advice")

    parsed = parse_json(raw)
    if not isinstance(parsed, dict):
        return _fallback("JSON parse failed")

    if not validate_node8(parsed):
        return _fallback("Output schema validation failed")

    return parsed


def _fallback(reason: str) -> Dict[str, Any]:
    return {
        "n8_loss_cause_analysis": {
            "loss_check": f"분석 생성 실패. ({reason})",
            "loss_amount_pct": "N/A",
            "one_line_summary": "분석을 완료할 수 없습니다.",
            "root_causes": [
                {
                    "id": "RC001",
                    "category": "internal",
                    "subcategory": "judgment_error",
                    "title": "분석 불가",
                    "description": f"손실 원인 분석을 완료할 수 없습니다. 사유: {reason}",
                    "impact_score": 5,
                    "impact_level": "medium",
                    "evidence": [
                        {
                            "source": "n6",
                            "type": "price",
                            "data_point": "데이터 없음",
                            "interpretation": "분석에 필요한 데이터를 수집할 수 없습니다."
                        }
                    ],
                    "timeline_relevance": "throughout"
                },
                {
                    "id": "RC002",
                    "category": "external",
                    "subcategory": "unexpected_event",
                    "title": "데이터 부족",
                    "description": "충분한 시장 데이터를 확보하지 못했습니다.",
                    "impact_score": 5,
                    "impact_level": "medium",
                    "evidence": [
                        {
                            "source": "n7",
                            "type": "news",
                            "data_point": "데이터 없음",
                            "interpretation": "관련 뉴스 데이터를 수집할 수 없습니다."
                        }
                    ],
                    "timeline_relevance": "throughout"
                }
            ],
            "cause_breakdown": {
                "internal_ratio": 50,
                "external_ratio": 50
            },
            "detailed_explanation": f"손실 원인 분석을 완료할 수 없습니다. 사유: {reason}. 다시 시도해 주세요.",
            "confidence_level": "low",
        },
        "n8_market_context_analysis": {
            "news_at_loss_time": [],
            "market_situation_analysis": "",
            "related_news": [],
        },
        "n9_input": {
            "investment_reason": "",
            "loss_cause_summary": "",
            "loss_cause_details": [],
            "objective_signals": {
                "price_trend": "sideways",
                "volatility_level": "medium",
                "technical_indicators": [],
                "news_facts": [],
            },
            "uncertainty_level": "high",
        },
    }

from typing import Dict, Any
from N3_Loss_Analyzer.schema import ALLOWED_FACTOR_TYPES, ALLOWED_UNCERTAINTY
from N6_Stock_Analyst.schema import ALLOWED_TRENDS
from N7_News_Summarizer.schema import ALLOWED_SENTIMENT
from N8_Concept_Explainer.schema import ALLOWED_UNCERTAINTY as ALLOWED_CONCEPT_UNCERTAINTY
from N9_Fallback_Handler.schema import ALLOWED_INTENT_HINT


def validate_node3(data: Dict[str, Any]) -> bool:
    """
    Node3 출력 JSON 최소 스키마 검증
    검증 실패 시 False 반환 → fallback 사용
    """

    # 1. loss_factors 검증
    loss_factors = data.get("loss_factors")
    if not isinstance(loss_factors, list) or len(loss_factors) == 0:
        return False

    for factor in loss_factors:
        if not isinstance(factor, dict):
            return False

        if factor.get("type") not in ALLOWED_FACTOR_TYPES:
            return False

        if not isinstance(factor.get("description"), str):
            return False

        evidence = factor.get("evidence")
        if not isinstance(evidence, dict):
            return False

        if not isinstance(evidence.get("source"), str):
            return False

        if evidence.get("indicator") != "bollinger_band":
            return False

        if not isinstance(evidence.get("related_period"), str):
            return False

    # 2. 선택적 리스트
    if "behavior_patterns" in data and not isinstance(data["behavior_patterns"], list):
        return False

    if "knowledge_gaps" in data and not isinstance(data["knowledge_gaps"], list):
        return False

    if "conversation_intent_hint" in data and not isinstance(
        data["conversation_intent_hint"], list
    ):
        return False

    # 3. uncertainty_level 검증
    if data.get("uncertainty_level") not in ALLOWED_UNCERTAINTY:
        return False

    return True


def validate_node6(data: Dict[str, Any]) -> bool:
    """
    Node6 출력 JSON 최소 스키마 검증
    """
    analysis = data.get("stock_analysis")
    if not isinstance(analysis, dict):
        return False

    if not isinstance(analysis.get("summary"), str):
        return False

    price_move = analysis.get("price_move")
    if not isinstance(price_move, dict):
        return False

    for key in ("start_price", "end_price", "pct_change"):
        if not isinstance(price_move.get(key), str):
            return False

    if analysis.get("trend") not in ALLOWED_TRENDS:
        return False

    indicators = analysis.get("indicators")
    if not isinstance(indicators, list):
        return False

    for indicator in indicators:
        if not isinstance(indicator, dict):
            return False
        if not isinstance(indicator.get("name"), str):
            return False
        if not isinstance(indicator.get("value"), str):
            return False
        if not isinstance(indicator.get("interpretation"), str):
            return False

    risk_notes = analysis.get("risk_notes")
    if not isinstance(risk_notes, list):
        return False
    if any(not isinstance(note, str) for note in risk_notes):
        return False

    if analysis.get("uncertainty_level") not in ALLOWED_UNCERTAINTY:
        return False

    return True


def validate_node7(data: Dict[str, Any]) -> bool:
    """
    Node7 출력 JSON 최소 스키마 검증
    """
    summary = data.get("news_summary")
    if not isinstance(summary, dict):
        return False

    if not isinstance(summary.get("query"), str):
        return False

    key_events = summary.get("key_events")
    if not isinstance(key_events, list):
        return False

    for event in key_events:
        if not isinstance(event, dict):
            return False
        for key in ("headline", "source", "date", "summary"):
            if not isinstance(event.get(key), str):
                return False

    if summary.get("sentiment") not in ALLOWED_SENTIMENT:
        return False

    if not isinstance(summary.get("impact_assessment"), str):
        return False

    if summary.get("uncertainty_level") not in ALLOWED_UNCERTAINTY:
        return False

    return True


def validate_node8(data: Dict[str, Any]) -> bool:
    """
    Node8 출력 JSON 최소 스키마 검증
    """
    explanation = data.get("concept_explanation")
    if not isinstance(explanation, dict):
        return False

    for key in ("term", "short_definition", "beginner_explanation"):
        if not isinstance(explanation.get(key), str):
            return False

    examples = explanation.get("examples")
    if not isinstance(examples, list):
        return False
    if any(not isinstance(item, str) for item in examples):
        return False

    related_terms = explanation.get("related_terms")
    if not isinstance(related_terms, list):
        return False
    if any(not isinstance(item, str) for item in related_terms):
        return False

    if explanation.get("uncertainty_level") not in ALLOWED_CONCEPT_UNCERTAINTY:
        return False

    return True


def validate_node9(data: Dict[str, Any]) -> bool:
    """
    Node9 출력 JSON 최소 스키마 검증
    """
    response = data.get("fallback_response")
    if not isinstance(response, dict):
        return False

    if not isinstance(response.get("message"), str):
        return False

    if response.get("intent_hint") not in ALLOWED_INTENT_HINT:
        return False

    return True

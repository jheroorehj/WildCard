from typing import Dict, Any
from N3_Loss_Analyzer.schema import ALLOWED_FACTOR_TYPES, ALLOWED_UNCERTAINTY


def validate_node3(data: Dict[str, Any]) -> bool:
    """
    Node3 출력 JSON 최소 스키마 검증
    실패하면 False → fallback 사용
    """

    # 1. loss_factors
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

    # 2. optional lists
    if "behavior_patterns" in data and not isinstance(data["behavior_patterns"], list):
        return False

    if "knowledge_gaps" in data and not isinstance(data["knowledge_gaps"], list):
        return False

    if "conversation_intent_hint" in data and not isinstance(
        data["conversation_intent_hint"], list
    ):
        return False

    # 3. uncertainty
    if data.get("uncertainty_level") not in ALLOWED_UNCERTAINTY:
        return False

    return True

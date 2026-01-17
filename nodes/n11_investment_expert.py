from typing import Any, Dict

from N11_Investment_Expert.n11 import node11_investment_expert


def node11_investment_expert_wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    N11: 투자 전문가 노드 래퍼
    """
    return node11_investment_expert(state)

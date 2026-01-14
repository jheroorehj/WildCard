from typing import Any, Dict

from N8_Loss_Analyst.n8 import node8_loss_analyst


def node8_loss_analyzer(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    N8: 손실 분석 래퍼
    """
    return node8_loss_analyst(state)

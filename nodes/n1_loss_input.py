from typing import Any, Dict

from N1_Input_Handler.n1 import node1_input_handler


def node1_loss_input(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    N1: 입력 핸들러 래퍼.
    """
    return node1_input_handler(state)

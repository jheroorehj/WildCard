# LangGraph 기반 State 정의
from typing import TypedDict, Dict


class MainState(TypedDict, total=False):
    # 입력 (레이어 1~3)
    layer1_stock: str
    layer2_buy_date: str
    layer2_sell_date: str
    layer3_decision_basis: str

    # Node3 출력
    n3_loss_diagnosis: Dict[str, object]

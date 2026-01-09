# LangGraph 공통 State 정의
from typing import TypedDict, Dict, Any

class MainState(TypedDict, total=False):
    # Node1 결과
    loss_case: Dict[str, Any]
    decision_context: Dict[str, Any]
    meta: Dict[str, Any]

    # Node6 / Node7 결과
    n6_stock_analysis: Dict[str, Any]
    n7_news_analysis: Dict[str, Any]

    # Node3 결과
    n3_loss_diagnosis: Dict[str, Any]

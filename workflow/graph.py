from langgraph.graph import StateGraph, END

from state.main_state import MainState
from nodes.n1_loss_input import node1_loss_input
from nodes.n6_n7_parallel import node6_n7_parallel
from nodes.n8_loss_analyzer import node8_loss_analyzer
from nodes.n9_learning_pattern import node9_learning_pattern
from nodes.n10_learning_tutor import node10_learning_tutor
from nodes.n4_chat_entry import node4_chat_entry
from nodes.n11_investment_expert import node11_investment_expert_wrapper


def build_graph(entry_point: str = "N1"):
    """
    투자 손실 분석 워크플로우 그래프 빌드
    N6(기술분석)과 N7(뉴스분석)은 병렬로 실행됩니다.
    """
    g = StateGraph(MainState)

    g.add_node("N1", node1_loss_input)
    # N6과 N7을 병렬로 실행하는 통합 노드
    g.add_node("N6_N7", node6_n7_parallel)
    g.add_node("N8", node8_loss_analyzer)
    g.add_node("N9", node9_learning_pattern)
    g.add_node("N10", node10_learning_tutor)
    g.add_node("N4", node4_chat_entry)
    g.add_node("N11", node11_investment_expert_wrapper)

    # 간소화된 엣지 구조 (N6_N7 병렬 노드 사용)
    g.set_entry_point(entry_point)
    g.add_edge("N1", "N6_N7")      # N1 → N6+N7 병렬
    g.add_edge("N6_N7", "N8")      # N6+N7 완료 후 N8
    g.add_edge("N8", "N9")
    g.add_edge("N9", "N10")
    g.add_edge("N10", "N4")
    g.add_edge("N4", "N11")
    g.add_edge("N11", END)

    return g.compile()

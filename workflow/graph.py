from langgraph.graph import StateGraph, END
from state.main_state import MainState
from N3_Loss_Analyzer.n3 import node3_loss_analyzer
from N5_Router.n5 import node5_parallel_router
from N10_Report_Writer.n10 import node10_loss_review_report

def build_graph():
    g = StateGraph(MainState)

    g.add_node("N3", node3_loss_analyzer)
    g.add_node("N5", node5_parallel_router)
    g.add_node("N10", node10_loss_review_report)

    g.set_entry_point("N3")
    g.add_edge("N3", "N5")
    g.add_edge("N5", "N10")
    g.add_edge("N10", END)

    return g.compile()

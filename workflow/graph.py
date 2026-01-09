from langgraph.graph import StateGraph, END
from state.main_state import MainState
from N3_Loss_Analyzer.n3 import node3_loss_analyzer

def build_graph():
    g = StateGraph(MainState)

    g.add_node("N3", node3_loss_analyzer)

    g.set_entry_point("N3")
    g.add_edge("N3", END)

    return g.compile()

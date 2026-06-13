from langgraph.graph import StateGraph, END
from state import AgentState
from nodes.doc_loader       import doc_loader
from nodes.preprocessor     import preprocessor
from nodes.output_formatter import output_formatter


def build_graph():
    graph = StateGraph(AgentState)

    # ── Add nodes ─────────────────────────
    graph.add_node("doc_loader",       doc_loader)
    graph.add_node("preprocessor",     preprocessor)
    graph.add_node("output_formatter", output_formatter)

    # ── Define edges (linear flow) ─────────
    # Removed synthesis step - directly formats paper summaries
    graph.set_entry_point("doc_loader")
    graph.add_edge("doc_loader",       "preprocessor")
    graph.add_edge("preprocessor",     "output_formatter")
    graph.add_edge("output_formatter", END)

    return graph.compile()
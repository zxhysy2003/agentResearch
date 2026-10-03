"""The shared model/tool loop, with no provider or service configuration imports."""

from typing import Any, Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END, MessagesState, StateGraph


def pending_tool_calls(state: MessagesState) -> Literal["tools", "done"]:
    message = state["messages"][-1]
    if not isinstance(message, AIMessage):
        raise TypeError(f"Expected AIMessage, got {type(message)}")
    return "tools" if message.tool_calls else "done"


def build_research_graph(
    model_node: Any,
    tools_node: Any,
    *,
    state_schema: type = MessagesState,
    entry_point: str | None = "model",
) -> StateGraph:
    """Inject model/prompt and tool execution nodes; callers may add input guards."""
    graph = StateGraph(state_schema)
    graph.add_node("model", model_node)
    graph.add_node("tools", tools_node)
    if entry_point is not None:
        graph.set_entry_point(entry_point)
    graph.add_edge("tools", "model")
    graph.add_conditional_edges("model", pending_tool_calls, {"tools": "tools", "done": END})
    return graph

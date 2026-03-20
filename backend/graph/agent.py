"""LangGraph assembly and agent execution helpers for KrishiBot."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph

from backend.graph.nodes import chatbot_node, should_continue, tool_executor_node
from backend.graph.state import AgriState

graph = StateGraph(AgriState)
graph.add_node("chatbot", chatbot_node)
graph.add_node("tools", tool_executor_node)
graph.set_entry_point("chatbot")
graph.add_conditional_edges("chatbot", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "chatbot")

compiled_graph = graph.compile()


def run_agent(
    user_message: str,
    session_id: str,
    location: Optional[str],
    history: List[BaseMessage],
) -> Dict[str, Any]:
    """Run the KrishiBot graph and return the final reply with metadata."""

    initial_state: AgriState = {
        "messages": [*history, HumanMessage(content=user_message)],
        "user_location": location,
        "session_id": session_id,
        "tools_used": [],
        "sources": [],
    }

    final_state = compiled_graph.invoke(initial_state)
    messages = final_state["messages"]
    final_ai_message = next(
        (message for message in reversed(messages) if isinstance(message, AIMessage)),
        None,
    )
    response_text = (
        final_ai_message.content
        if isinstance(final_ai_message, AIMessage)
        else "I could not generate a response right now."
    )

    return {
        "response": response_text,
        "tools_used": final_state.get("tools_used", []),
        "sources": final_state.get("sources", []),
        "history": messages[-20:],
    }

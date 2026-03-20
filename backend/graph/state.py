"""State definitions used by the LangGraph workflow."""

from __future__ import annotations

from typing import Annotated, List, Optional, TypedDict

from langgraph.graph.message import add_messages


class AgriState(TypedDict):
    """Shared state carried across KrishiBot graph nodes."""

    messages: Annotated[list, add_messages]
    user_location: Optional[str]
    session_id: str
    tools_used: List[str]
    sources: List[str]

"""Request and response schemas for the chat API."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat payload from the Streamlit frontend."""

    user_message: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    location: Optional[str] = None


class ChatResponse(BaseModel):
    """Response returned by the FastAPI chat endpoint."""

    response: str
    session_id: str
    sources: Optional[List[str]] = None
    tool_calls_made: Optional[List[str]] = None

"""Chat endpoints for the KrishiBot backend."""

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, HTTPException
from langchain_core.messages import BaseMessage

from backend.graph.agent import run_agent
from backend.models.schemas import ChatRequest, ChatResponse

router = APIRouter()

SESSION_STORE: Dict[str, List[BaseMessage]] = {}
MAX_HISTORY_MESSAGES = 20


@router.get("/health")
def health_check() -> dict:
    """Return service health information."""

    return {"status": "ok", "service": "KrishiBot Agriculture Chatbot"}


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Handle a chat request and return the assistant response."""

    history = SESSION_STORE.get(payload.session_id, [])

    try:
        result = run_agent(
            user_message=payload.user_message,
            session_id=payload.session_id,
            location=payload.location,
            history=history,
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"KrishiBot could not process the request: {exc}",
        ) from exc

    SESSION_STORE[payload.session_id] = result["history"][-MAX_HISTORY_MESSAGES:]

    return ChatResponse(
        response=result["response"],
        session_id=payload.session_id,
        sources=result.get("sources") or [],
        tool_calls_made=result.get("tools_used") or [],
    )

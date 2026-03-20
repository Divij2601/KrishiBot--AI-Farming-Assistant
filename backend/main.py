"""FastAPI entry point for the KrishiBot backend."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.chat import router as chat_router

app = FastAPI(
    title="KrishiBot - Agriculture AI Assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    """Return a welcome message for the API root."""

    return {"message": "Welcome to KrishiBot - Agriculture AI Assistant"}

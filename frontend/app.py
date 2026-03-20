"""Streamlit frontend for the KrishiBot agriculture chatbot."""

from __future__ import annotations

from datetime import datetime
from html import escape
from uuid import uuid4

import httpx
import streamlit as st

BACKEND_URL = "http://localhost:8080/api/v1/chat"

st.set_page_config(
    page_title="KrishiBot - Your AI Farming Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --app-bg: #0f1110;
        --panel-bg: #171b18;
        --panel-soft: #202521;
        --panel-line: rgba(255,255,255,0.08);
        --sidebar-bg: #102614;
        --text-main: #eef2ea;
        --text-soft: rgba(238, 242, 234, 0.68);
        --text-muted: rgba(238, 242, 234, 0.38);
        --accent: #3b8f45;
        --user-bubble: #2d7e37;
        --assistant-bubble: #2a2f2b;
        --input-bg: #252b27;
    }

    .stApp,
    [data-testid="stAppViewContainer"] {
        background: var(--app-bg);
        color: var(--text-main);
        font-family: "Segoe UI", sans-serif;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar-bg) 0%, #0f2213 100%);
        border-right: 1px solid var(--panel-line);
    }

    [data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        margin-bottom: 0.8rem;
    }

    .brand-icon {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(59, 143, 69, 0.18);
        font-size: 1.7rem;
    }

    .brand-title {
        color: var(--text-main);
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.05;
        margin: 0;
    }

    .brand-copy {
        color: var(--text-soft);
        font-size: 0.98rem;
        line-height: 1.5;
        margin: 0.85rem 0 1.25rem;
    }

    .sidebar-label {
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.84rem;
        font-weight: 700;
        margin: 1.1rem 0 0.55rem;
    }

    .capability-list {
        list-style: none;
        padding: 0;
        margin: 0.85rem 0 1.25rem;
    }

    .capability-list li {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        color: var(--text-soft);
        font-size: 0.98rem;
        margin-bottom: 0.9rem;
    }

    .cap-dot {
        width: 10px;
        height: 10px;
        border-radius: 999px;
        flex: 0 0 10px;
    }

    .sidebar-footer {
        color: var(--text-muted);
        border-top: 1px solid var(--panel-line);
        margin-top: 1.35rem;
        padding-top: 1rem;
        font-size: 0.82rem;
    }

    [data-testid="stSidebar"] .stTextInput label {
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.84rem;
        font-weight: 700;
    }

    [data-testid="stSidebar"] .stTextInput input {
        background: var(--input-bg);
        color: var(--text-main);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 13px;
        font-size: 1rem;
    }

    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: rgba(238,242,234,0.34);
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        height: 3.4rem;
        border-radius: 14px;
        background: rgba(255,255,255,0.02);
        color: var(--text-main);
        border: 1px solid rgba(255,255,255,0.14);
        font-size: 0.98rem;
        font-weight: 600;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.04);
        border-color: rgba(255,255,255,0.22);
    }

    .shell-header {
        background: var(--panel-soft);
        border-bottom: 1px solid var(--panel-line);
        border-radius: 20px 20px 0 0;
        padding: 1rem 1.2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0;
    }

    .shell-left {
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }

    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 999px;
        background: #58c45f;
    }

    .shell-title {
        color: var(--text-main);
        font-size: 1.35rem;
        font-weight: 700;
        margin: 0;
    }

    .shell-subtitle {
        color: var(--text-soft);
        font-size: 0.92rem;
        margin-top: 0.12rem;
    }

    .chip-row {
        display: flex;
        gap: 0.65rem;
        flex-wrap: wrap;
    }

    .tool-chip {
        padding: 0.42rem 0.85rem;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.03);
        color: var(--text-soft);
        font-size: 0.86rem;
        font-weight: 600;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--panel-bg);
        border-color: var(--panel-line);
        border-radius: 0 0 20px 20px;
        padding: 0.95rem 1rem 1rem;
    }

    .intro-card {
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        background: #202421;
        padding: 1.7rem 1.35rem;
        text-align: center;
        max-width: 760px;
        margin: 0 auto 1.2rem;
    }

    .intro-icon {
        font-size: 1.9rem;
        margin-bottom: 0.45rem;
    }

    .intro-title {
        color: var(--text-main);
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 0.45rem;
    }

    .intro-copy {
        color: var(--text-soft);
        font-size: 1rem;
        line-height: 1.5;
        margin: 0 auto;
        max-width: 580px;
    }

    .quick-label {
        color: var(--text-muted);
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }

    .message-wrap {
        margin-bottom: 1rem;
    }

    .message-wrap.user {
        text-align: right;
    }

    .message-wrap.assistant {
        text-align: left;
    }

    .message-meta {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.42rem;
    }

    .avatar {
        width: 38px;
        height: 38px;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.92rem;
        font-weight: 700;
    }

    .avatar.user {
        background: #225fb0;
        color: #ffffff;
    }

    .avatar.assistant {
        background: var(--accent);
        color: #ffffff;
    }

    .sender {
        color: var(--text-soft);
        font-size: 0.88rem;
        font-weight: 600;
    }

    .bubble {
        display: inline-block;
        max-width: min(78%, 720px);
        padding: 0.95rem 1.1rem;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        font-size: 1rem;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
    }

    .bubble.user {
        background: var(--user-bubble);
        color: #ffffff;
        border-top-right-radius: 8px;
    }

    .bubble.assistant {
        background: var(--assistant-bubble);
        color: var(--text-main);
        border-top-left-radius: 8px;
    }

    .timestamp {
        color: var(--text-muted);
        font-size: 0.78rem;
        margin-top: 0.3rem;
    }

    .stExpander {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        background: rgba(255,255,255,0.02);
        margin-bottom: 0.8rem;
    }

    .prompt-button .stButton > button {
        width: 100%;
        min-height: 2.9rem;
        border-radius: 999px;
        background: #1f2420;
        color: var(--text-main);
        border: 1px solid rgba(255,255,255,0.1);
        font-size: 0.95rem;
    }

    .prompt-button .stButton > button:hover {
        border-color: rgba(59,143,69,0.5);
        background: #252b27;
    }

    div[data-testid="stForm"] {
        border-top: 1px solid var(--panel-line);
        margin-top: 0.85rem;
        padding-top: 0.95rem;
    }

    div[data-testid="stForm"] .stTextInput input {
        background: var(--input-bg);
        color: var(--text-main);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px;
        min-height: 3rem;
    }

    div[data-testid="stForm"] .stTextInput input::placeholder {
        color: rgba(238,242,234,0.36);
    }

    div[data-testid="stForm"] .stButton > button,
    div[data-testid="stForm"] .stFormSubmitButton > button {
        width: 100%;
        min-height: 3rem;
        border-radius: 14px;
        background: var(--accent);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.08);
        font-weight: 700;
    }

    @media (max-width: 900px) {
        .shell-header {
            flex-direction: column;
            align-items: flex-start;
        }

        .bubble {
            max-width: 92%;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())
if "location" not in st.session_state:
    st.session_state.location = ""


def current_time_label() -> str:
    """Return a compact time label for chat messages."""

    return datetime.now().strftime("%I:%M %p").lstrip("0")


def render_message(message: dict) -> None:
    """Render a single chat message."""

    is_user = message["role"] == "user"
    role_class = "user" if is_user else "assistant"
    sender = "You" if is_user else "KrishiBot"
    avatar = "You" if is_user else "KB"
    timestamp = message.get("timestamp", "")

    if is_user:
        meta_html = (
            f'<div class="message-meta" style="justify-content:flex-end;">'
            f'<div class="sender">{sender}</div>'
            f'<div class="avatar {role_class}">{avatar}</div>'
            f"</div>"
        )
    else:
        meta_html = (
            f'<div class="message-meta">'
            f'<div class="avatar {role_class}">{avatar}</div>'
            f'<div class="sender">{sender}</div>'
            f"</div>"
        )

    st.markdown(
        f"""
        <div class="message-wrap {role_class}">
            {meta_html}
            <div class="bubble {role_class}">{escape(message["content"])}</div>
            <div class="timestamp">{timestamp}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if message.get("tool_calls_made"):
        with st.expander("Tools used"):
            for tool_name in message["tool_calls_made"]:
                st.markdown(f"- `{tool_name}`")

    if message.get("sources"):
        with st.expander("Sources"):
            for source in message["sources"]:
                st.markdown(f"- [{source}]({source})")


def send_prompt(prompt_text: str) -> None:
    """Send a prompt to the backend and store both chat turns."""

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt_text,
            "timestamp": current_time_label(),
        }
    )

    try:
        with st.spinner("KrishiBot is thinking..."):
            response = httpx.post(
                BACKEND_URL,
                json={
                    "user_message": prompt_text,
                    "session_id": st.session_state.session_id,
                    "location": st.session_state.location or None,
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": data["response"],
                "tool_calls_made": data.get("tool_calls_made", []),
                "sources": data.get("sources", []),
                "timestamp": current_time_label(),
            }
        )
    except httpx.HTTPError:
        st.error(
            "Could not connect to KrishiBot backend. Please ensure the server is running."
        )


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-icon">🌱</div>
            <div class="brand-title">KrishiBot</div>
        </div>
        <div class="brand-copy">AI farming guidance for crops, soil, weather and market prices.</div>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.location = st.text_input(
        "Your Location",
        value=st.session_state.location,
        placeholder="e.g. Pune, Maharashtra",
    )

    st.markdown('<div class="sidebar-label">Capabilities</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <ul class="capability-list">
            <li><span class="cap-dot" style="background:#61cf68;"></span><span>Crop selection and calendar</span></li>
            <li><span class="cap-dot" style="background:#f3b34d;"></span><span>Soil and NPK advice</span></li>
            <li><span class="cap-dot" style="background:#4da3ff;"></span><span>Live weather guidance</span></li>
            <li><span class="cap-dot" style="background:#ff7f50;"></span><span>Pest and disease support</span></li>
            <li><span class="cap-dot" style="background:#3ec7c7;"></span><span>Fertilizer and irrigation</span></li>
            <li><span class="cap-dot" style="background:#b564e3;"></span><span>Mandi price lookup</span></li>
        </ul>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid4())
        st.rerun()

    st.markdown(
        '<div class="sidebar-footer">Powered by Groq AI and LangGraph</div>',
        unsafe_allow_html=True,
    )

_, main_col, _ = st.columns([0.05, 0.9, 0.05])

selected_prompt = None
typed_prompt = None
send_clicked = False

with main_col:
    st.markdown(
        """
        <div class="shell-header">
            <div class="shell-left">
                <div class="status-dot"></div>
                <div>
                    <div class="shell-title">KrishiBot Assistant</div>
                    <div class="shell-subtitle">Online | 6 tools active</div>
                </div>
            </div>
            <div class="chip-row">
                <div class="tool-chip">Tavily Search</div>
                <div class="tool-chip">Weather API</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        with st.container(height=560):
            if not st.session_state.messages:
                st.markdown(
                    """
                    <div class="intro-card">
                        <div class="intro-icon">🌱</div>
                        <div class="intro-title">Namaste! I'm KrishiBot</div>
                        <div class="intro-copy">
                            Ask simple farming questions about crops, soil, weather, pests, fertilizer plans, irrigation, or mandi prices.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="quick-label">Try one of these</div>',
                    unsafe_allow_html=True,
                )

                quick_prompts = [
                    "Which crop should I grow this season?",
                    "How do I control tomato pests?",
                    "What is today's wheat price?",
                    "Give me soil NPK advice",
                ]
                prompt_cols = st.columns(2)
                for index, prompt in enumerate(quick_prompts):
                    with prompt_cols[index % 2]:
                        st.markdown('<div class="prompt-button">', unsafe_allow_html=True)
                        if st.button(
                            prompt,
                            key=f"quick_prompt_{index}",
                            use_container_width=True,
                        ):
                            selected_prompt = prompt
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                for message in st.session_state.messages:
                    render_message(message)

        with st.form("composer_form", clear_on_submit=True):
            input_cols = st.columns([10, 1.4])
            with input_cols[0]:
                typed_prompt = st.text_input(
                    "Message",
                    placeholder="Ask me about crops, weather, pests, prices...",
                    label_visibility="collapsed",
                )
            with input_cols[1]:
                send_clicked = st.form_submit_button("Send", use_container_width=True)

active_prompt = selected_prompt or (typed_prompt if send_clicked and typed_prompt else None)

if active_prompt:
    send_prompt(active_prompt)
    st.rerun()

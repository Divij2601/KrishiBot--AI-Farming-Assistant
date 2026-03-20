"""Node functions for the KrishiBot LangGraph agent."""

from __future__ import annotations

import re
from typing import Any, Dict

from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END
from langgraph.prebuilt import ToolNode

from backend.config import GROQ_API_KEY
from backend.graph.state import AgriState
from backend.graph.tools import TOOLS

SYSTEM_PROMPT = """
You are KrishiBot, an expert AI agricultural assistant designed to help farmers make informed decisions. You have deep knowledge of:

- Indian and global agricultural practices
- Crop science, agronomy, and horticulture
- Soil science and soil health management
- Plant pathology (pest and disease identification and control)
- Meteorology as it relates to farming
- Agricultural markets, commodity pricing, and MSP (Minimum Support Price)
- Organic and sustainable farming practices
- Government schemes for farmers (PM-KISAN, Soil Health Card, etc.)

## Your Behavior Rules:

1. **Always use tools** when the user asks about: current weather, market prices, recent pest outbreaks, news, or anything requiring real-time data. Do NOT answer such questions from memory alone.

2. **For crop selection questions:** Use the crop calendar tool and soil NPK advisor tool. Ask for location and soil type if not provided.

3. **For weather questions:** Always call the weather tool with the user's location. If location is unknown, ask for it.

4. **For pest/disease questions:** Use web_search_tool to find the latest information. Provide: identification signs, organic control methods, chemical control options (with safety precautions), and preventive measures.

5. **For market prices:** Use web_search_tool AND get_market_prices_tool. Always mention that prices vary by region and date.

6. **For fertilizer questions:** Use fertilizer_calculator_tool. Always recommend soil testing first.

7. **Language:** Respond in the same language the user writes in. If they write in Hindi or mixed Hindi-English (Hinglish), respond likewise. Keep responses practical and farmer-friendly - avoid overly technical jargon unless asked.

8. **Response Format:** Use bullet points and short paragraphs. For recommendations, always give a numbered action plan. End responses with a follow-up question to keep the conversation helpful.

9. **Safety:** Never recommend illegal pesticides. Always mention to consult a local agricultural extension officer (KVK) for critical decisions.

10. **Uncertainty:** If you are unsure, say so and recommend the user contact their nearest Krishi Vigyan Kendra (KVK).
""".strip()

tool_node = ToolNode(TOOLS)


def _build_model() -> ChatGroq:
    """Create the Groq chat model used by KrishiBot."""

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured. Please add it to your environment.")
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        temperature=0.2,
    )


def chatbot_node(state: AgriState) -> Dict[str, Any]:
    """Run the LLM node with the agriculture system prompt and bound tools."""

    model = _build_model().bind_tools(TOOLS)
    location_note = state.get("user_location") or "Unknown"
    messages = [
        SystemMessage(
            content=f"{SYSTEM_PROMPT}\n\nKnown user location: {location_note}\nSession ID: {state['session_id']}"
        ),
        *state["messages"],
    ]
    ai_message = model.invoke(messages)
    return {"messages": [ai_message]}


def tool_executor_node(state: AgriState) -> Dict[str, Any]:
    """Execute requested tools and record tool usage plus discovered source URLs."""

    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", []) or []
    tool_names = [tool_call.get("name", "unknown_tool") for tool_call in tool_calls]

    tool_result = tool_node.invoke(state)
    tool_messages = tool_result.get("messages", [])

    combined_text = "\n".join(str(message.content) for message in tool_messages)
    found_urls = re.findall(r"https?://[^\s)\]]+", combined_text)

    updated_tools = list(dict.fromkeys([*state.get("tools_used", []), *tool_names]))
    updated_sources = list(dict.fromkeys([*state.get("sources", []), *found_urls]))

    return {
        "messages": tool_messages,
        "tools_used": updated_tools,
        "sources": updated_sources,
    }


def should_continue(state: AgriState) -> str:
    """Route to the tool executor when the last AI message contains tool calls."""

    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END

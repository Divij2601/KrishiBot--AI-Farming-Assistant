# KrishiBot - AI Agriculture Chatbot

KrishiBot is a full-stack agriculture assistant that helps farmers and agri-professionals with crop planning, soil guidance, fertilizer decisions, weather-aware advice, pest and disease support, and market price lookups. The backend is built with FastAPI and LangGraph, while the frontend uses Streamlit for a simple farmer-friendly chat experience.

## Features

- Crop selection help based on season, soil, and region
- Soil health and NPK guidance for common soil types
- Live weather lookup with farming-oriented interpretation
- Pest and disease assistance using web search
- Fertilizer calculation by crop, acreage, and soil fertility
- Market price discovery using real-time search
- Stateful multi-step orchestration with LangGraph
- Session-aware chat with short-term in-memory history

## Project Structure

```text
agri-chatbot/
├── backend/
│   ├── main.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   └── tools.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── chat.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── config.py
├── frontend/
│   └── app.py
├── .env.example
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10 or newer
- A Groq API key
- A Tavily API key
- An OpenWeatherMap API key
- Internet access for live tools

## Setup

1. Clone the repository or move into the generated project folder:

```bash
cd agri-chatbot
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:

```bash
copy .env.example .env
```

5. Add your API keys to `.env`.

6. Run the backend from the project root:

```bash
uvicorn backend.main:app --reload
```

7. In a new terminal, run the frontend:

```bash
streamlit run frontend/app.py
```

8. Open the Streamlit URL shown in your terminal, usually `http://localhost:8501`.

## API Keys

- Groq API: https://console.groq.com/keys
- Tavily API: https://app.tavily.com/home
- OpenWeatherMap API: https://openweathermap.org/api

## Example Questions

- Which crop is suitable for loamy soil in Punjab during the rabi season?
- My tomato leaves have yellow spots and curling. What could it be?
- What is the weather today in Nashik and how will it affect spraying?
- Suggest fertilizer for wheat on 3 acres with low soil fertility.
- What is the current soybean mandi price in India?
- How should I improve sandy soil for maize cultivation?

## Architecture

```text
User
  |
  v
Streamlit Frontend
  |
  v
FastAPI Backend
  |
  v
LangGraph Agent
  |
  +--> Groq LLM
  |
  +--> Tools
       |
       +--> Tavily Search
       +--> OpenWeatherMap
       +--> Crop Calendar Tool
       +--> Soil NPK Advisor Tool
       +--> Fertilizer Calculator Tool
       +--> Market Price Tool
```

## Troubleshooting

- `GROQ_API_KEY is not configured`
  Add your Groq key to `.env` and restart the backend.

- Weather or search tools return errors
  Check your API keys, internet connection, and whether the target service is reachable.

- Streamlit cannot connect to the backend
  Make sure FastAPI is running on `http://localhost:8080` and that no firewall rule is blocking it.

- Import errors on startup
  Confirm you installed dependencies from `requirements.txt` in the same active virtual environment.

- Empty or poor market price results
  Market data changes by mandi and date. Cross-check with your local APMC or mandi portal before selling.

## Notes

- Chat history is stored only in memory and capped to the last 20 messages per session.
- The app uses Groq-hosted LLMs with LangGraph tool orchestration.
- For high-stakes farm decisions, users should still consult their nearest KVK or extension officer.

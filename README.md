# Personalized Networking Assistant

An AI-powered web application that helps users generate smart, tailored conversation starters for professional or social networking events.

## Features

1. **Smart Starters Generator**: Extracts themes from event descriptions using DistilBERT and generates tailored conversation prompts using GPT-2 / Gemini / fallback heuristics.
2. **Quick Fact Verification**: Searches and summarizes quick references on networking topics using the Wikipedia API.
3. **History Strategy Review**: Logs past generated prompts and logs feedback (thumbs up/down) to persist networking strategies.

## Project Structure

```
personalized-networking-assistant/
├── backend/
│   ├── __init__.py
│   ├── main.py            # FastAPI Application Entrypoint & Endpoints
│   ├── database.py        # SQLite Database connection, model logs & feedback
│   ├── models.py          # Pydantic Schemas for Requests and Responses
│   ├── ai_service.py      # Theme Extraction (DistilBERT) & Prompt Generation (GPT-2/Gemini)
│   └── wikipedia_service.py # Wikipedia API integration for fact checking
├── frontend/
│   ├── __init__.py
│   └── app.py             # Streamlit premium interface
├── tests/
│   ├── __init__.py
│   ├── test_backend.py    # FastAPI router and integration tests
│   └── test_ai_service.py # Unit tests for AI service and fallbacks
├── requirements.txt       # Project dependencies
├── .env.example           # Environment variables configuration template
├── README.md              # Project usage and setup instructions
└── run.py                 # Runner utility to start backend and frontend concurrently
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in any keys:
   ```bash
   cp .env.example .env
   ```
   If you have a Gemini API key, add it to `GEMINI_API_KEY` and set `AI_PROVIDER=gemini`. Otherwise, keep `AI_PROVIDER=fallback` or `AI_PROVIDER=huggingface`.

3. **Run the Application**:
   ```bash
   python run.py
   ```
   This will start the FastAPI backend on `http://localhost:8000` and the Streamlit frontend on `http://localhost:8501`.

4. **Run Unit Tests**:
   ```bash
   pytest
   ```

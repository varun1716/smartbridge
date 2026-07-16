from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from backend.models import (
    StarterRequest,
    StarterResponse,
    FactCheckResponse,
    FeedbackRequest,
    HistoryItem
)
from backend import database
from backend.ai_service import AIService
from backend.wikipedia_service import get_wikipedia_summary

app = FastAPI(
    title="Personalized Networking Assistant API",
    description="Backend API for generating conversation starters, fact-checking, and logging history.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    """Health check endpoint."""
    return {"status": "online", "message": "Personalized Networking Assistant API is running."}

@app.post("/api/generate-starters", response_model=StarterResponse, status_code=status.HTTP_201_CREATED)
def generate_starters(request: StarterRequest):
    """
    Extracts key themes from the event description and generates tailored conversation starters.
    Logs the interaction in the database.
    """
    try:
        # 1. Run AI theme extraction and prompt generation
        themes, starters = AIService.extract_themes_and_generate_starters(
            request.event_description,
            request.interests
        )
        
        # 2. Save the interaction in SQLite database
        interaction_id = database.save_interaction(
            event_description=request.event_description,
            interests=request.interests,
            extracted_themes=themes,
            conversation_starters=starters
        )
        
        # 3. Return response
        return StarterResponse(
            id=interaction_id,
            event_description=request.event_description,
            interests=request.interests,
            extracted_themes=themes,
            conversation_starters=starters
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate starters: {str(e)}"
        )

@app.get("/api/fact-check", response_model=FactCheckResponse)
def fact_check(query: str):
    """
    Queries the Wikipedia API to retrieve a summary of information about the searched topic.
    """
    if not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'query' cannot be empty."
        )
    
    result = get_wikipedia_summary(query)
    return FactCheckResponse(
        topic=result["topic"],
        summary=result["summary"],
        source_url=result["source_url"],
        found=result["found"]
    )

@app.get("/api/history", response_model=List[HistoryItem])
def get_history():
    """
    Retrieves all past logged conversation sessions and their feedback ratings.
    """
    try:
        history = database.get_history()
        return [HistoryItem(**item) for item in history]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )

@app.post("/api/feedback")
def update_feedback(request: FeedbackRequest):
    """
    Updates the thumbs up/down feedback for a previously generated conversation session.
    """
    success = database.update_feedback(request.interaction_id, request.feedback)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No interaction found with ID {request.interaction_id}"
        )
    return {"message": "Feedback updated successfully", "id": request.interaction_id, "feedback": request.feedback}

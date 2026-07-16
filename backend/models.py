from pydantic import BaseModel, Field
from typing import List, Optional

class StarterRequest(BaseModel):
    event_description: str = Field(..., description="Details/description of the networking event")
    interests: List[str] = Field(..., description="User's list of interests or fields")

class StarterResponse(BaseModel):
    id: int = Field(..., description="Database record ID for the generated session")
    event_description: str
    interests: List[str]
    extracted_themes: List[str]
    conversation_starters: List[str]

class FactCheckResponse(BaseModel):
    topic: str
    summary: str
    source_url: str
    found: bool

class FeedbackRequest(BaseModel):
    interaction_id: int
    feedback: Optional[str] = Field(None, description="Feedback status: 'thumbs_up', 'thumbs_down', or null")

class HistoryItem(BaseModel):
    id: int
    event_description: str
    interests: List[str]
    extracted_themes: List[str]
    conversation_starters: List[str]
    feedback: Optional[str] = None
    timestamp: str

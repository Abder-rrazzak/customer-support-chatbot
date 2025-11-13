from pydantic import BaseModel
from typing import Optional, Dict, List

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    intent: str
    confidence: float
    entities: Dict = {}
    suggestions: List[str] = []
    requires_human: bool = False
    response_time_ms: Optional[float] = None

class SessionCreate(BaseModel):
    user_id: str

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    created_at: str
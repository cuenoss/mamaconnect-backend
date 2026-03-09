from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str

class ChatSessionCreate(BaseModel):
    user_id: int

class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    created_at: str
    
    class Config:
        from_attributes = True

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    sender: str
    message: str
    timestamp: str
    
    class Config:
        from_attributes = True

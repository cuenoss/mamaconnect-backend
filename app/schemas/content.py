from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArticleCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    author_name: Optional[str] = None
    created_at: datetime
    category: Optional[str] = None
    
    class Config:
        from_attributes = True

class ArticleCreateRequest(BaseModel):
    title: str
    content: str

class FAQCreate(BaseModel):
    question: str
    answer: str

class FAQResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    author_id: int
    
    class Config:
        from_attributes = True

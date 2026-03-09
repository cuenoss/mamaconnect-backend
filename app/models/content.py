from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    category: Optional[str] = None  # nutrition, exercise, labor, postpartum


class FAQ(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    answer: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    author_id: int = Field(foreign_key="user.id")

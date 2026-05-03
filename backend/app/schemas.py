from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ProjectCreate(BaseModel):
    repo_url: str

class ProjectResponse(BaseModel):
    id: int
    repo_url: str
    name: str
    status: str
    progress: int
    created_at: datetime
    updated_at: datetime
    last_analyzed_at: Optional[datetime]

    class Config:
        from_attributes = True

class AnalysisProgressResponse(BaseModel):
    step: str
    message: str
    timestamp: datetime

class QARequest(BaseModel):
    project_id: int
    question: str

class QAResponse(BaseModel):
    project_id: int
    question: str
    answer: str

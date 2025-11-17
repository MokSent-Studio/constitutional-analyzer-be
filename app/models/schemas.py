from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from enum import Enum

class ExplanationScope(str, Enum):
    SUMMARY = "A"
    KEY_POINTS = "B"
    COMPREHENSIVE_OUTLINE = "C"

class AnalysisRequest(BaseModel):
    chapter_url: HttpUrl
    explanation_scope: ExplanationScope
    analysis_role: Optional[str] = None
    target_audience: Optional[str] = None
    follow_up_questions: List[str] = []

class FollowUpRequest(BaseModel):
    question: str
    initial_analysis_text: str
    original_url: HttpUrl

class Chapter(BaseModel):
    id: int
    name: str
    url: HttpUrl
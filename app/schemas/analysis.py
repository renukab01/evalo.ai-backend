from pydantic import BaseModel
from typing import Optional, Union

class AnalysisData(BaseModel):
    confidence: Optional[str] = None
    clarity: Optional[str] = None
    ques_count: Optional[str] = None
    correct_ans_count: Optional[str] = None
    wrong_ans_count: Optional[str] = None
    tech_knowledge: Optional[str] = None
    overall_fit: Optional[str] = None
    ai_feedback: Optional[str] = None
    what_went_well: Optional[str] = None
    area_to_improve: Optional[str] = None
    speech_patterns: Optional[str] = None

class AnalysisResponse(BaseModel):
    status: int
    analysis: AnalysisData

class ErrorResponse(BaseModel):
    status: int
    errors: str 
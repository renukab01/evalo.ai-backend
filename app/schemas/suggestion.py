from pydantic import BaseModel
from typing import Union, Optional, List

class SuggestionRequest(BaseModel):
    id: int
    role: Optional[str] = None
    job_desc: Optional[str] = None
    experience: Optional[Union[str, int]] = None
    skills: Optional[str] = None
    transcript: Optional[str] = None

class SuggestionResponse(BaseModel):
    status: int
    expected_questions: List[str]

class ErrorResponse(BaseModel):
    status: int
    errors: str 
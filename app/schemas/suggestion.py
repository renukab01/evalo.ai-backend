from pydantic import BaseModel
from typing import Union, Optional

class SuggestionRequest(BaseModel):
    id: int
    role: str
    job_desc: str
    experience: Union[str, int]
    skills: str
    transcript: str

class SuggestionResponse(BaseModel):
    status: int
    expected_questions: str

class ErrorResponse(BaseModel):
    status: int
    errors: str 
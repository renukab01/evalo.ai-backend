from pydantic import BaseModel
from typing import Optional

class ReportRequest(BaseModel):
    audio: str  # URL to audio file

class ReportResponse(BaseModel):
    status: int
    message: str

class ErrorResponse(BaseModel):
    status: int
    errors: str 
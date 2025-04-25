from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Union, Any
from datetime import date, time
from enum import Enum

class MeetingStatus(str, Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

# Request Schemas
class MeetingCreate(BaseModel):
    date: date
    time: time
    name: str
    interviewer_name: str
    meet_link: str
    role: str
    job_desc: str
    experience: Union[str, int]
    skills: str

# Response Schemas
class BaseResponse(BaseModel):
    status: int

class ErrorResponse(BaseResponse):
    errors: str

class MeetingListItem(BaseModel):
    id: int
    date: date
    time: time
    name: str
    interviewer_name: str
    meet_link: str
    status: MeetingStatus
    role: str

class MeetingsResponse(BaseResponse):
    meetings: List[MeetingListItem]

class MeetingDetail(BaseModel):
    id: int
    date: date
    time: time
    name: str
    interviewer_name: str
    meet_link: str
    role: str
    job_desc: str
    experience: Union[str, int]
    skills: str
    status: MeetingStatus
    is_review_ready: bool
    audio: Optional[str] = None
    transcript: Optional[str] = None
    expected_questions: Optional[str] = None
    confidence: Optional[str] = None
    clarity: Optional[str] = None
    ques_count: Optional[str] = None
    correct_ans_count: Optional[str] = None
    wrong_ans_count: Optional[str] = None
    tech_knowledge: Optional[str] = None
    overall_fit: Optional[str] = None
    what_went_well: Optional[str] = None
    area_to_improve: Optional[str] = None
    ai_feedback: Optional[str] = None
    speech_patterns: Optional[str] = None

class MeetingDetailResponse(BaseResponse):
    meeting: MeetingDetail
    
    model_config = ConfigDict(from_attributes=True)
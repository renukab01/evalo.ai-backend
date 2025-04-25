from sqlalchemy import Column, String, Integer, Date, Time, Boolean, Enum, BigInteger, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from app.database.database import Base

import enum

class MeetingStatus(enum.Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    name = Column(String, nullable=False)
    interviewer_name = Column(String, nullable=False)
    meet_link = Column(String, nullable=False)
    role = Column(String, nullable=False)
    job_desc = Column(Text, nullable=True)
    experience = Column(String, nullable=True)  # Using String for flexibility
    skills = Column(String, nullable=True)
    status = Column(Enum(MeetingStatus), default=MeetingStatus.SCHEDULED, nullable=False)
    is_review_ready = Column(Boolean, default=False, nullable=False)
    
    # Optional fields for review
    audio = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    expected_questions = Column(Text, nullable=True)
    confidence = Column(String, nullable=True)
    clarity = Column(String, nullable=True)
    ques_count = Column(String, nullable=True)
    correct_ans_count = Column(String, nullable=True)
    wrong_ans_count = Column(String, nullable=True)
    what_went_well = Column(Text, nullable=True)
    area_to_improve = Column(Text, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    tech_knowledge = Column(String, nullable=True)
    overall_fit = Column(String, nullable=True)
    speech_patterns = Column(String, nullable=True) 
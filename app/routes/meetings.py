from fastapi import APIRouter, Depends, HTTPException, status, Response, Path
from sqlalchemy.orm import Session
from typing import Dict, Optional, List, Union
from sqlalchemy.exc import SQLAlchemyError
import json

from app.database.database import get_db
from app.models.meeting import Meeting as MeetingModel, MeetingStatus as DBMeetingStatus
from app.schemas.meeting import (
    MeetingCreate, 
    BaseResponse, 
    ErrorResponse, 
    MeetingsResponse, 
    MeetingDetailResponse,
    MeetingListItem,
    MeetingDetail,
    MeetingStatus
)
from app.services.question_generator import generate_expected_questions

router = APIRouter(tags=["meetings"])

@router.post("/meetings", response_model=Union[BaseResponse, ErrorResponse])
def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    """
    Schedule a new meeting.
    """
    try:
        # Generate expected questions based on job description and candidate info
        expected_questions_json = generate_expected_questions(
            job_desc=meeting.job_desc,
            experience=str(meeting.experience),
            skills=meeting.skills
        )
        
        db_meeting = MeetingModel(
            date=meeting.date,
            time=meeting.time,
            name=meeting.name,
            interviewer_name=meeting.interviewer_name,
            meet_link=meeting.meet_link,
            role=meeting.role,
            job_desc=meeting.job_desc,
            experience=meeting.experience,
            skills=meeting.skills,
            status=DBMeetingStatus.SCHEDULED,
            is_review_ready=False,
            expected_questions=expected_questions_json
        )
        db.add(db_meeting)
        db.commit()
        return BaseResponse(status=201)
    except SQLAlchemyError as e:
        db.rollback()
        return ErrorResponse(status=400, errors=f"Failed to create meeting: {str(e)}")
    except Exception as e:
        db.rollback()
        return ErrorResponse(status=500, errors=f"Internal server error: {str(e)}")

@router.get("/meetings", response_model=Union[MeetingsResponse, ErrorResponse])
def get_all_meetings(db: Session = Depends(get_db)):
    """
    Get all meetings.
    """
    try:
        db_meetings = db.query(MeetingModel).all()
        meeting_list: List[MeetingListItem] = []
        
        for meeting in db_meetings:
            # Convert DB enum to Pydantic enum
            status_value = meeting.status.value if meeting.status else None
            
            meeting_list.append(
                MeetingListItem(
                    id=meeting.id,
                    date=meeting.date,
                    time=meeting.time,
                    name=meeting.name,
                    interviewer_name=meeting.interviewer_name,
                    meet_link=meeting.meet_link,
                    status=status_value,
                    role=meeting.role
                )
            )
        
        return MeetingsResponse(
            status=200,
            meetings=meeting_list
        )
    except Exception as e:
        return ErrorResponse(status=500, errors=f"Internal server error: {str(e)}")

@router.get("/meeting/{meeting_id}", response_model=Union[MeetingDetailResponse, ErrorResponse])
def get_meeting(meeting_id: int = Path(..., title="The ID of the meeting to get"), db: Session = Depends(get_db)):
    """
    Get a single meeting by ID.
    """
    try:
        db_meeting = db.query(MeetingModel).filter(MeetingModel.id == meeting_id).first()
        if db_meeting is None:
            return ErrorResponse(status=404, errors=f"Meeting with ID {meeting_id} not found")
        
        # Convert DB enum to Pydantic enum
        status_value = db_meeting.status.value if db_meeting.status else None
        
        meeting_detail = MeetingDetail(
            id=db_meeting.id,
            date=db_meeting.date,
            time=db_meeting.time,
            name=db_meeting.name,
            interviewer_name=db_meeting.interviewer_name,
            meet_link=db_meeting.meet_link,
            role=db_meeting.role,
            job_desc=db_meeting.job_desc,
            experience=db_meeting.experience,
            skills=db_meeting.skills,
            status=status_value,
            is_review_ready=db_meeting.is_review_ready,
            audio=db_meeting.audio,
            transcript=db_meeting.transcript,
            expected_questions=db_meeting.expected_questions,
            confidence=db_meeting.confidence,
            clarity=db_meeting.clarity,
            ques_count=db_meeting.ques_count,
            correct_ans_count=db_meeting.correct_ans_count,
            wrong_ans_count=db_meeting.wrong_ans_count,
            what_went_well=db_meeting.what_went_well,
            area_to_improve=db_meeting.area_to_improve,
            ai_feedback=db_meeting.ai_feedback,
            tech_knowledge=db_meeting.tech_knowledge,
            overall_fit=db_meeting.overall_fit,
            speech_patterns=db_meeting.speech_patterns
        )
        
        return MeetingDetailResponse(
            status=200,
            meeting=meeting_detail
        )
    except Exception as e:
        return ErrorResponse(status=500, errors=f"Internal server error: {str(e)}") 
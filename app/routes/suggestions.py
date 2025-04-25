from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Union
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import get_db
from app.models.meeting import Meeting as MeetingModel
from app.schemas.suggestion import SuggestionRequest, SuggestionResponse, ErrorResponse
from app.utils.ai_suggestions import get_suggested_questions

router = APIRouter(tags=["suggestions"])

@router.post("/suggestions", response_model=Union[SuggestionResponse, ErrorResponse])
def generate_suggestions(request: SuggestionRequest, db: Session = Depends(get_db)):
    """
    Generate real-time suggestions for interview questions.
    """
    try:
        # Check if the meeting exists
        meeting = db.query(MeetingModel).filter(MeetingModel.id == request.id).first()
        if not meeting:
            return ErrorResponse(
                status=404, 
                errors=f"Meeting with ID {request.id} not found"
            )
        
        # If transcript is provided in the request and the meeting has no transcript, update it
        if request.transcript and not meeting.transcript:
            meeting.transcript = request.transcript
            db.commit()
        # If neither has a transcript, return an error
        else:
            return ErrorResponse(
                status=400, 
                errors="No transcript provided"
            )
        
        # Generate suggestions using AI
        suggested_questions = get_suggested_questions(
            job_desc=request.job_desc,
            role=request.role,
            experience=request.experience,
            skills=request.skills,
            transcript=request.transcript
        )
        
        # Update the meeting record with the expected questions
        meeting.expected_questions = suggested_questions
        db.commit()
        
        # Return the suggestions
        return SuggestionResponse(
            status=200,
            expected_questions=suggested_questions
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        return ErrorResponse(status=400, errors=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        return ErrorResponse(status=500, errors=f"Failed to generate suggestions: {str(e)}") 
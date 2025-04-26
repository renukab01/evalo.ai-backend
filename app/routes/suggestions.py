from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Union, List
from sqlalchemy.exc import SQLAlchemyError
import json

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
        
        # Get transcript from request or meeting
        transcript = ""
        if request.transcript:
            transcript = request.transcript
            # If meeting has no transcript, update it
            if not meeting.transcript:
                meeting.transcript = request.transcript
                db.commit()
        elif meeting.transcript:
            transcript = meeting.transcript
        
        # Generate suggestions using AI (returns JSON string)
        suggested_questions_json = get_suggested_questions(
            job_desc=meeting.job_desc if not request.job_desc else request.job_desc,
            role=meeting.role if not request.role else request.role,
            experience=str(meeting.experience) if not request.experience else str(request.experience),
            skills=meeting.skills if not request.skills else request.skills,
            already_suggested_questions=meeting.expected_questions if meeting.expected_questions else "",
            transcript=transcript
        )
        
        # Update the meeting record with the expected questions
        if meeting.expected_questions:
            # Try to parse existing questions as JSON, if possible
            try:
                existing_questions = json.loads(meeting.expected_questions)
                new_questions = json.loads(suggested_questions_json)
                
                # Combine the question arrays
                combined_questions = existing_questions + new_questions
                
                # Store the combined questions
                meeting.expected_questions = json.dumps(combined_questions)
            except json.JSONDecodeError:
                # If existing questions aren't in JSON format, store them separately
                meeting.expected_questions = f"{meeting.expected_questions}\n\n--- Additional Questions ---\n{suggested_questions_json}"
        else:
            meeting.expected_questions = suggested_questions_json
            
        db.commit()
        
        # Return the suggestions as parsed JSON for the API response
        return SuggestionResponse(
            status=200,
            expected_questions=json.loads(suggested_questions_json)
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        return ErrorResponse(status=400, errors=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        return ErrorResponse(status=500, errors=f"Failed to generate suggestions: {str(e)}") 
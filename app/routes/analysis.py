from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from typing import Union
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import get_db
from app.models.meeting import Meeting as MeetingModel
from app.schemas.analysis import AnalysisResponse, AnalysisData, ErrorResponse

router = APIRouter(tags=["analysis"])

@router.get("/meeting/{meeting_id}/analysis", response_model=Union[AnalysisResponse, ErrorResponse])
def get_meeting_analysis(meeting_id: int = Path(..., title="The ID of the meeting to get analysis for"), 
                        db: Session = Depends(get_db)):
    """
    Get analysis details by meeting ID.
    """
    try:
        # Query the meeting from database
        meeting = db.query(MeetingModel).filter(MeetingModel.id == meeting_id).first()
        
        # Check if meeting exists
        if not meeting:
            return ErrorResponse(
                status=404,
                errors=f"Meeting with ID {meeting_id} not found"
            )
        
        # Check if analysis data exists
        if not any([
            meeting.confidence,
            meeting.clarity,
            meeting.ques_count,
            meeting.correct_ans_count,
            meeting.wrong_ans_count,
            meeting.tech_knowledge,
            meeting.overall_fit,
            meeting.ai_feedback,
            meeting.what_went_well,
            meeting.area_to_improve,
            meeting.speech_patterns
        ]):
            return ErrorResponse(
                status=404,
                errors=f"Analysis data not available for meeting with ID {meeting_id}"
            )
        
        # Return analysis data
        return AnalysisResponse(
            status=200,
            analysis=AnalysisData(
                confidence=meeting.confidence,
                clarity=meeting.clarity,
                ques_count=meeting.ques_count,
                correct_ans_count=meeting.correct_ans_count,
                wrong_ans_count=meeting.wrong_ans_count,
                tech_knowledge=meeting.tech_knowledge,
                overall_fit=meeting.overall_fit,
                ai_feedback=meeting.ai_feedback,
                what_went_well=meeting.what_went_well,
                area_to_improve=meeting.area_to_improve,
                speech_patterns=meeting.speech_patterns
            )
        )
    
    except SQLAlchemyError as e:
        return ErrorResponse(status=400, errors=f"Database error: {str(e)}")
    except Exception as e:
        return ErrorResponse(status=500, errors=f"Internal server error: {str(e)}") 
from fastapi import APIRouter, Depends, Path, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Union
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import get_db
from app.models.meeting import Meeting as MeetingModel
from app.schemas.report import ReportRequest, ReportResponse, ErrorResponse
from app.utils.report_generator import generate_interview_report
from app.utils.voice_analyzer import analyze_voice

router = APIRouter(tags=["reports"])

def process_report_generation(meeting_id: int, audio_url: str, db_session):
    """
    Background task to generate and store the report.
    """
    try:
        # Get the meeting
        meeting = db_session.query(MeetingModel).filter(MeetingModel.id == meeting_id).first()
        if not meeting:
            print(f"Meeting with ID {meeting_id} not found")
            return
            
        # Store audio URL
        meeting.audio = audio_url
        db_session.commit()
        
        # Analyze audio if URL is provided
        if audio_url:
            print(f"Analyzing audio from URL: {audio_url}")
            voice_analysis = analyze_voice(audio_url)
            if voice_analysis:
                meeting.clarity = voice_analysis["clarity"]
                meeting.confidence = voice_analysis["confidence"]
                meeting.speech_patterns = voice_analysis["speech_patterns"]
                db_session.commit()
                print(f"Voice analysis completed for meeting ID {meeting_id}")
            else:
                print(f"Voice analysis failed for meeting ID {meeting_id}")
        
        # If no transcript available, we can't generate a report
        if not meeting.transcript:
            print("Cannot generate report: No transcript available")
            return
            
        # Generate the report using Gemini AI
        report_data = generate_interview_report(
            transcript=meeting.transcript,
            role=meeting.role,
            job_desc=meeting.job_desc,
            experience=str(meeting.experience),
            skills=meeting.skills
        )
        
        # Update the meeting with report data
        for key, value in report_data.items():
            if hasattr(meeting, key) and key not in ["clarity", "confidence", "speech_patterns"]:
                # Don't override voice analysis results if already set
                if key in ["clarity", "confidence", "speech_patterns"] and getattr(meeting, key):
                    continue
                setattr(meeting, key, value)
        
        # Mark the review as ready
        meeting.is_review_ready = True
        
        # Save to database
        db_session.commit()
        print(f"Report generation completed for meeting ID {meeting_id}")
    except Exception as e:
        print(f"Error in background task: {str(e)}")
        db_session.rollback()
    finally:
        db_session.close()

@router.post("/meeting/{meeting_id}/generate-report", response_model=Union[ReportResponse, ErrorResponse])
async def generate_report(
    background_tasks: BackgroundTasks,
    request: ReportRequest, 
    meeting_id: int = Path(..., title="The ID of the meeting to generate a report for"),
    db: Session = Depends(get_db)
):
    """
    Trigger report generation for a meeting.
    This endpoint initiates a background task to generate the report.
    """
    try:
        # Check if the meeting exists
        meeting = db.query(MeetingModel).filter(MeetingModel.id == meeting_id).first()
        if not meeting:
            return ErrorResponse(
                status=404,
                errors=f"Meeting with ID {meeting_id} not found"
            )
        
        # Add the task to the background tasks
        background_tasks.add_task(
            process_report_generation,
            meeting_id=meeting_id,
            audio_url=request.audio,
            db_session=db
        )
        
        # Return immediately
        return ReportResponse(
            status=202,
            message=f"Report generation initiated for meeting ID {meeting_id}"
        )
        
    except SQLAlchemyError as e:
        return ErrorResponse(status=400, errors=f"Database error: {str(e)}")
    except Exception as e:
        return ErrorResponse(status=500, errors=f"Internal server error: {str(e)}") 
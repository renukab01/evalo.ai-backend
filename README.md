# Interview Management API

A FastAPI application for managing interview meetings, reviews, and AI-powered analysis.

## Requirements

- Python 3.10 or higher
- PostgreSQL database
- Google API key for Gemini AI

## Features

- Create, read, update, and delete interview meetings
- Track meeting status (Scheduled, In Progress, Completed, Cancelled)
- Generate AI-powered suggestions for interview questions
- Analyze interview transcripts with AI feedback
- Analyze voice recordings for clarity and confidence metrics
- Generate comprehensive interview reports

## Database Schema

The application uses a PostgreSQL database with the following schema:

- `meetings` table with fields for:
  - Basic interview details (date, time, names, role, etc.)
  - Interview status and review readiness
  - Transcript and audio recording links
  - AI analysis results (confidence, clarity, speech patterns, etc.)
  - Feedback and evaluation metrics

## AI Integration

The application uses Google's Gemini AI for:
1. Generating interview question suggestions
2. Analyzing interview transcripts
3. Evaluating voice recordings for clarity and confidence
4. Providing comprehensive candidate feedback

## Setup and Installation

1. Clone the repository
2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your database connection string and Google API key:
   ```
   DATABASE_URL=postgresql://username:password@host:port/dbname
   GOOGLE_API_KEY=your_google_api_key
   ```

## Audio Analysis Requirements

For voice analysis features, you'll need to install additional dependencies:
- librosa
- soundfile
- SpeechRecognition
- pydub

These can be installed with:
```
pip install librosa soundfile SpeechRecognition pydub
```

## Running the Application

Start the application with:

```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the application is running, you can access:

- Interactive API documentation: `http://localhost:8000/docs`
- Alternative documentation: `http://localhost:8000/redoc`

## API Endpoints

### Meetings
- `GET /meetings` - List all meetings
- `POST /meetings` - Create a new meeting
- `GET /meeting/{id}` - Get a specific meeting

### Analysis
- `GET /meeting/{id}/analysis` - Get analysis details for a meeting

### Suggestions
- `POST /suggestions` - Generate AI-powered interview question suggestions

### Reports
- `POST /meeting/{id}/generate-report` - Trigger report generation with audio and transcript analysis

## Audio URL Format

When providing audio URLs for analysis, ensure they are full URLs including the protocol (http:// or https://). Local file paths will not work with the download function. 
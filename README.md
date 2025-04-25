# Interview Management API

A FastAPI application for managing interview meetings and reviews.

## Features

- Create, read, update, and delete interview meetings
- Track meeting status (Scheduled, In Progress, Completed, Cancelled)
- Store and update interview reviews and feedback
- RESTful API with comprehensive endpoint documentation

## Database Schema

The application uses a PostgreSQL database with the following schema:

- `meetings` table with fields for:
  - Basic interview details (date, time, names, role, etc.)
  - Interview status and review readiness
  - Feedback and review data (optional fields)

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
4. Create a `.env` file with your database connection string:
   ```
   DATABASE_URL=postgresql://username:password@host:port/dbname
   ```

## Running the Application

Start the application with:

```
python main.py
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the application is running, you can access:

- Interactive API documentation: `http://localhost:8000/docs`
- Alternative documentation: `http://localhost:8000/redoc`

## API Endpoints

- `GET /meetings` - List all meetings with optional filtering
- `POST /meetings` - Create a new meeting
- `GET /meetings/{id}` - Get a specific meeting
- `PUT /meetings/{id}` - Update a meeting
- `PATCH /meetings/{id}/review` - Update meeting review details
- `PATCH /meetings/{id}/status` - Update meeting status
- `DELETE /meetings/{id}` - Delete a meeting 
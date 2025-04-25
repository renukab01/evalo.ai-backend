from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base
from app.routes import meetings, suggestions, analysis, reports

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Interview Management API",
    description="API for managing interview meetings and reviews",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(meetings.router)
app.include_router(suggestions.router)
app.include_router(analysis.router)
app.include_router(reports.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Interview Management API"} 
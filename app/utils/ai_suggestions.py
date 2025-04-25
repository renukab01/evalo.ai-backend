import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Environment
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GENAI_API_KEY:
    raise EnvironmentError("Set GOOGLE_API_KEY in .env file or as environment variable.")

# Configure Gemini AI
genai.configure(api_key=GENAI_API_KEY)

def get_suggested_questions(job_desc: str, role: str, experience: str, skills: str, transcript: str):
    """Get suggested questions based on the interview transcript and job details."""
    
    # Construct job description from inputs
    jd = f"""
    {role} ({experience} Years)
    Required:
    {skills}

    Job Description:
    {job_desc}
    """
    
    prompt = f"""You are an expert interviewer. Based on the following interview transcript and job description, suggest three follow-up questions. 
The questions should be one of these types:
1. A question to evaluate the candidate's technical knowledge based on their previous answers
2. A skill mentioned in Job description
3. A cross-question if something was answered incompletely or needs clarification
4. A question to explore something the candidate mentioned but didn't explain in detail

The goal of the question should be to evaluate the candidate.

Job Description:
{jd}
Interview Transcript:
{transcript}

Provide exactly three numbered questions, one of each type mentioned above. Format your response as three numbered questions only, without any additional text.
"""

    try:
        # Create Gemini model client
        client = genai.GenerativeModel("gemini-1.5-flash")

        # Generate the response
        response = client.generate_content(prompt)
        
        # Return the response text
        return response.text
    except Exception as e:
        print(f"Error getting suggestions: {e}")
        raise Exception(f"Failed to generate suggestions: {str(e)}") 
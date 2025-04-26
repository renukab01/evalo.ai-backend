import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from typing import Dict, Optional

# === Setup logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Load environment variables ===
load_dotenv()

# === Setup Environment ===
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GENAI_API_KEY:
    logger.warning("GOOGLE_API_KEY not found. Question generation will not work.")
else:
    # === Setup Clients ===
    genai.configure(api_key=GENAI_API_KEY)

def generate_expected_questions(job_desc: str, experience: str, skills: str) -> Optional[str]:
    """
    Generate expected interview questions based on job description and candidate info.
    
    Args:
        job_desc: The job description
        experience: The candidate's experience
        skills: The candidate's skills
        
    Returns:
        A string containing the generated questions or None if an error occurs
    """
    if not GENAI_API_KEY:
        logger.error("GOOGLE_API_KEY not set. Cannot generate questions.")
        return None
    
    logger.info("Generating expected questions...")
    
    # Format the candidate info
    interviewee_details = f"experience: {experience}, skills: {skills}"
    
    prompt = f"""You are an expert interviewer. Based on the following interviewee details and job description, suggest three follow-up questions. 
The questions should be one of these types:
1. A question to evaluate the candidate's technical knowledge based on their skills or experience
2. A skill mentioned in Job description
3. A skill mentioned in interviewee details
4. Any questions that will be helpful to evaluate the candidate for the desired role

The goal of the question should be to evaluate the candidate.

Job Description:
{job_desc}

Interviewee Details:
{interviewee_details}

Provide exactly three numbered questions, one of each type mentioned above. Format your response as three numbered questions only, without any additional text.
"""

    try:
        # Generate the response using the compatible API
        client = genai.GenerativeModel("gemini-1.5-flash")
        response = client.generate_content(prompt)
        
        # Return the response text
        return response.text
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return None 
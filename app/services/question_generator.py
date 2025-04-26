import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import json
import re
from typing import Dict, Optional, List

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
        A JSON string containing the generated questions or None if an error occurs
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

The goal of the questions should be to evaluate the candidate thoroughly. Include some warm questions in starting and simple technical questions.

Job Description:
{job_desc}

Interviewee Details:
{interviewee_details}

Return your response as a JSON array of strings, with each string being a question.
Format your response like this:
["Question 1 text", "Question 2 text", "Question 3 text", "Question 4 text", "Question 5 text"]

Ensure your response is valid JSON that can be parsed directly. Each question should be concise, technical, and relevant.
Do not include any text before or after the JSON array.
"""

    try:
        # Generate the response using the compatible API
        client = genai.GenerativeModel("gemini-1.5-flash")
        response = client.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean the response to ensure it's valid JSON
        # Remove any markdown code block formatting if present
        response_text = re.sub(r'```json', '', response_text)
        response_text = re.sub(r'```', '', response_text)
        response_text = response_text.strip()
        
        # Parse the response as JSON to validate it
        try:
            questions = json.loads(response_text)
            return json.dumps(questions)  # Return valid JSON string
        except json.JSONDecodeError:
            # If not valid JSON, attempt to parse numbered questions and convert to JSON
            logger.warning("Response was not valid JSON, attempting to parse numbered format...")
            numbered_pattern = r'\d+\.\s+(.*?)(?=\d+\.\s+|$)'
            matches = re.findall(numbered_pattern, response_text, re.DOTALL)
            
            if matches:
                questions = [q.strip() for q in matches]
                return json.dumps(questions)
            else:
                # If all parsing attempts fail, return the raw text as a single item
                return json.dumps([response_text])
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return None 
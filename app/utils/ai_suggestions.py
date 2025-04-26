import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

# Setup Environment
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GENAI_API_KEY:
    raise EnvironmentError("Set GOOGLE_API_KEY in .env file or as environment variable.")

# Configure Gemini AI
genai.configure(api_key=GENAI_API_KEY)

def get_suggested_questions(job_desc: str, role: str, experience: str, skills: str, already_suggested_questions: str, transcript: str = None):
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

The goal of the questions should be to evaluate the candidate. Ask simple questions on technical topics that are easy to answer. Keep your question short and concise.

Job Description:
{jd}
Interview Transcript:
{transcript}

DO NOT INCLUDE QUESTIONS THAT ARE ALREADY SUGGESTED.

DO NOT include below questions in your response:
{already_suggested_questions}

Return your response as a JSON array of strings, with each string being a question. 
Format your response like this:
["Question 1 text", "Question 2 text", "Question 3 text"]

Ensure your response is valid JSON that can be parsed directly. Do not include any text before or after the JSON array.
"""

    try:
        # Create Gemini model client
        client = genai.GenerativeModel("gemini-1.5-flash")

        # Generate the response
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
            print("Response was not valid JSON, attempting to parse numbered format...")
            numbered_pattern = r'\d+\.\s+(.*?)(?=\d+\.\s+|$)'
            matches = re.findall(numbered_pattern, response_text, re.DOTALL)
            
            if matches:
                questions = [q.strip() for q in matches]
                return json.dumps(questions)
            else:
                # If all parsing attempts fail, return the raw text as a single item
                return json.dumps([response_text])
            
    except Exception as e:
        print(f"Error getting suggestions: {e}")
        raise Exception(f"Failed to generate suggestions: {str(e)}") 
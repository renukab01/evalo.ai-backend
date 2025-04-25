import os
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Setup Environment
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GENAI_API_KEY:
    raise EnvironmentError("Set GOOGLE_API_KEY in .env file or as environment variable.")

# Configure Gemini AI
genai.configure(api_key=GENAI_API_KEY)

def generate_interview_report(transcript: str, role: str, job_desc: str, experience: str, skills: str):
    """
    Generate a comprehensive interview report using Gemini AI.
    Returns a dictionary with all analyzed fields.
    """
    
    # Construct job description from inputs
    jd = f"""
    {role}

    Job Description:
    {job_desc}
    """
    
    prompt = f"""You are an expert at evaluating technical interviews. Analyze this interview transcript and provide a detailed evaluation.

JOB DESCRIPTION:
{jd}

INTERVIEW TRANSCRIPT:
{transcript}

CANDIDATE EXPERIENCE:
{experience}

CANDIDATE SKILLS:
{skills}

Based on the transcript, provide an evaluation in the following format:

CONFIDENCE: INTEGER BETWEEN 0 AND 10 where 0 is the lowest and 10 is the highest

CLARITY: INTEGER BETWEEN 0 AND 10 where 0 is the lowest and 10 is the highest

QUESTION COUNT: Count the total number of questions asked in the interview.

CORRECT ANSWERS: Count how many questions the candidate answered correctly.

INCORRECT ANSWERS: Count how many questions the candidate answered incorrectly.

TECHNICAL KNOWLEDGE: INTEGER BETWEEN 0 AND 10 where 0 is the lowest and 10 is the highest

OVERALL FIT: INTEGER BETWEEN 0 AND 10 where 0 is the lowest and 10 is the highest

WHAT WENT WELL: Mention 3-5 strengths demonstrated by the candidate seperated by line breaks.

AREAS TO IMPROVE: Mention 3-5 areas where the candidate could improve seperated by line breaks.

AI FEEDBACK: Provide a 5 sentence overall assessment of the candidate's performance and fit for the role.

Make sure your evaluation is balanced, fair, and based solely on the evidence in the transcript, jd, candidates experience and skills.
The candidate can be good in some areas but bad in others. Remember not to be too harsh.
Format each section clearly with the heading followed by your analysis. Do not use markdown formatting like asterisks or bold text.
"""

    try:
        # Create Gemini model client
        client = genai.GenerativeModel("gemini-1.5-flash")

        # Generate the response
        response = client.generate_content(prompt)
        response_text = response.text
        
        # Parse the response to extract different sections
        report_data = {}
        
        # Extract sections using string operations
        sections = {
            "confidence": "CONFIDENCE:",
            "clarity": "CLARITY:",
            "ques_count": "QUESTION COUNT:",
            "correct_ans_count": "CORRECT ANSWERS:",
            "wrong_ans_count": "INCORRECT ANSWERS:",
            "tech_knowledge": "TECHNICAL KNOWLEDGE:",
            "overall_fit": "OVERALL FIT:",
            "what_went_well": "WHAT WENT WELL:",
            "area_to_improve": "AREAS TO IMPROVE:",
            "ai_feedback": "AI FEEDBACK:"
        }
        
        for key, section_header in sections.items():
            try:
                start_index = response_text.find(section_header)
                if start_index == -1:
                    report_data[key] = "Not provided"
                    continue
                
                start_index += len(section_header)
                
                # Find the next section header to determine where this section ends
                end_index = len(response_text)
                for _, next_header in sections.items():
                    next_header_index = response_text.find(next_header, start_index)
                    if next_header_index != -1 and next_header_index < end_index:
                        end_index = next_header_index
                
                # Extract and clean the section content
                section_content = response_text[start_index:end_index].strip()
                
                # Remove markdown formatting (** for bold, etc.)
                section_content = re.sub(r'\*\*', '', section_content)
                # Remove extra newlines
                section_content = re.sub(r'\n{3,}', '\n\n', section_content)
                
                report_data[key] = section_content
            except Exception as e:
                report_data[key] = f"Error extracting {key}: {str(e)}"
        
        return report_data
    except Exception as e:
        print(f"Error generating report: {e}")
        raise Exception(f"Failed to generate report: {str(e)}") 
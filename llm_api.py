import os
import openai
from dotenv import load_dotenv

def setup_openai():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def filter_relevant_keywords(resume_keywords, job_keywords, job_description, model="gpt-3.5-turbo"):
    prompt = (
        "You're a resume optimization assistant.\n\n"
        "Below is a list of keywords found in a job description and a separate list found in a candidate's resume. "
        "Your task is to compare them and return **only the job-related, relevant missing keywords** from the job keywords that are not already in the resume keywords.\n\n"
        "Please remove irrelevant, overly generic, personal, or location-based keywords. Focus on technical skills, tools, qualifications, and core competencies that match the job.\n\n"
        f"Resume Keywords:\n{', '.join(resume_keywords)}\n\n"
        f"Job Description Keywords:\n{', '.join(job_keywords)}\n\n"
        f"Job Description Snippet:\n{job_description[:1000]}...\n\n"
        "Return only the relevant missing keywords as a Python list."
    )
    
    setup_openai()
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at resume-job keyword matching."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=300
        )
        filtered = response.choices[0].message['content'].strip()
        # Optional: extract the list using eval or ast.literal_eval if needed
        return filtered
    except Exception as e:
        print(f"Error filtering keywords: {e}")
        return "[]"


def create_prompt(resume_section, relevant_keywords, job_posting_text):
    prompt = (
        "You're a professional resume editor. Below is a candidate's resume section followed by a list of **relevant** keywords based on a job posting.\n\n"
        "Your task is to:\n"
        "1. Improve the resume section to sound more impactful and aligned with the job description.\n"
        "2. Naturally integrate the listed keywords.\n"
        "3. Write the revised section using professional bullet points focused on actionable solutions and outcomes.\n\n"
        f"Resume Section:\n{resume_section}\n\n"
        f"Relevant Keywords: {', '.join(relevant_keywords)}\n\n"
        f"Job Posting Snippet:\n{job_posting_text[:1000]}...\n\n"
        "Return only the enhanced resume bullet points."
    )
    return prompt


def generate_text_gpt(prompt, model="gpt-3.5-turbo", temperature=0.7, max_tokens=500):
    setup_openai()
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful and professional resume assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating text with GPT: {e}")
        return ""

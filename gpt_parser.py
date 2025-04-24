import os
import openai
import dotenv
import json
import re

# Load environment variables from .env file
dotenv.load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_resume_with_gpt(html_resume: str) -> dict:
    """
    Uses GPT-4 to parse a cleaned HTML resume into structured sections.

    Args:
        html_resume (str): The full resume converted to HTML (already cleaned, no base64 images).

    Returns:
        dict: A dictionary with keys: summary, skills, experience, education.
              The 'experience' value should be a list of job dictionaries:
              Each job should have: title, company, date_range, and bullets (list of strings).
    """
    try:
        # Construct the system and user prompts
        system_prompt = (
            "You are a resume parser. Given a resume in HTML format, extract each logical section and return it as structured JSON. "
            "Do not modify, rewrite, summarize, or enhance any content. Preserve original bullet points and section text exactly as-is.\n\n"
            "Normalize similar section headers as follows:\n"
            "- 'Professional Summary', 'Objective', 'Overview' → 'summary'\n"
            "- 'Technical Skills', 'Tools', 'Tech Stack' → 'skills'\n"
            "- 'Work History', 'Professional Experience', 'Employment' → 'experience'\n"
            "- 'Education and Certifications', 'Certifications', 'Degrees' → 'education'\n"
            "- 'Projects', 'Capstone Projects', 'Independent Work', 'Freelance', 'Other Work' → 'projects'\n\n"
            "Return only a JSON object with keys: summary, skills, education, experience, and projects."
        )


        user_prompt = f"""HTML RESUME:
        {html_resume}

        Return only a JSON object with keys: summary, skills, education, experience, and projects.

        👉 Treat all non-standard sections (e.g., 'Independent Learning', 'Training', 'Other Work', 'Capstones', 'Certifications') as part of `projects` if they contain relevant bullets or work.

        👉 For certifications or short courses that don’t belong in `projects`, fold them into the `education` field as a bullet or short list.

        Do not return extra keys beyond those listed. Reclassify or discard irrelevant/unstructured text.


        For the `experience` key:
        - Return a list of job objects.
        - Each job object MUST contain:
        - "title"
        - "company"
        - "date_range"
        - "bullets" ← (this must be the field name)
        - Do NOT use any alternative keys like "responsibilities" or "tasks".

        """

        # Call the OpenAI API
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        # Parse the response
        parsed_response = response.choices[0].message.content.strip()
        # DEBUG
        print("GPT RAW RESPONSE:\n", parsed_response)
        # Strip markdown-style triple backticks

        if parsed_response.startswith("```json"):
            parsed_response = parsed_response.replace("```json", "").strip()
        if parsed_response.endswith("```"):
            parsed_response = parsed_response[:-3].strip()

        # Try JSON parse
        # Sanitize GPT output before parsing
        if parsed_response.startswith("```json"):
            parsed_response = parsed_response.replace("```json", "").strip()
        if parsed_response.endswith("```"):
            parsed_response = parsed_response[:-3].strip()

        # Strip leading/trailing junk
        parsed_response = parsed_response.strip().strip("`").strip()

        # Try to extract valid JSON from middle of a mess
        try:
            json_start = parsed_response.find('{')
            json_end = parsed_response.rfind('}') + 1
            clean_json = parsed_response[json_start:json_end]
            parsed_json = json.loads(clean_json)
            return parsed_json
        except Exception as e:
            print("❌ GPT did not return valid JSON.")
            print(parsed_response)
            print("Error:", e)
            return {}


    except Exception as e:
        print(f"Error parsing resume: {e}")
        return {}

if __name__ == "__main__":
    # Load a sample HTML resume from a file for testing
    sample_file_path = "sample_resume.html"
    with open(sample_file_path, 'r', encoding='utf-8') as file:
        html_resume = file.read()

    # Parse the resume and print the output
    parsed_resume = parse_resume_with_gpt(html_resume)
    print(json.dumps(parsed_resume, indent=4))
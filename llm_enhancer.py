# llm_enhancer.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from experience_splitter import split_experience_section, parse_job_entry
from typing import List

# Load your OpenAI key securely
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def enhance_summary_with_gpt(summary_text: str, missing_keywords: list) -> str:
    """
    Enhance the 'summary' section of a resume using GPT-4,
    by naturally incorporating missing job description keywords.
    """
    prompt = f"""
You are enhancing the 'Professional Summary' section of a resume.

The original summary is below:

---
{summary_text.strip()}
---

You must naturally incorporate the following missing keywords into the summary, without making it sound robotic or stuffed:

{", ".join(missing_keywords)}

🎯 Guidelines:
- Keep the improved summary under 60 words
- Focus on integrating missing *tools, certifications, or domain expertise*
- Keep tone professional, clear, and concise
- **Avoid redundancy 
- DO NOT fabricate achievements or job titles

Return ONLY the enhanced summary. Do not include explanations or headers.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"[Summary Enhancement Error] {e}")
        return summary_text  # fallback to original

#Detect format of skills section (comma vs bullet separated)
def detect_skills_format(skills_text: str) -> str:
    """
    Detects whether the skills section uses bullets or commas.

    Returns:
        'bullet' or 'comma'
    """
    if any(skills_text.strip().startswith(prefix) for prefix in ("•", "-", "*")):
        return "bullet"
    elif "," in skills_text:
        return "comma"
    else:
        return "unknown"

def build_skills_prompt(skills_text: str, missing_keywords: list, format_type: str) -> str:
    """
    Builds a GPT prompt for enhancing the skills section.
    """
    format_instruction = {
        "comma": "Return a clean, comma-separated list.",
        "bullet": "Return each skill as a short bullet point (use • or -).",
        "unknown": "Use a clean and readable format to list skills."
    }[format_type]

    prompt = f"""
You are enhancing the 'Skills' section of a resume.

Here is the original Skills section:

---
{skills_text.strip()}
---

Below is a list of missing keywords from the job description:

{", ".join(missing_keywords)}

🎯 Your task:
- Naturally incorporate as many relevant missing keywords as possible.
- Only include hard skills (tools, platforms, certifications, or directly measurable capabilities).
- If the existing section includes soft skills as a subcategory, only add soft skills to that portion.
- Avoid fabricating new skills unless they are *clearly implied* by the original.
- DO NOT repeat or re-list skills already present.
- **If the skills section is organized by category, rename the category headers to align with the key themes and terminology of the job description.**
- {format_instruction}

Return only the final enhanced skills section. No explanations.
    """.strip()

    return prompt

def enhance_skills_with_gpt(skills_text: str, missing_keywords: list) -> str:
    format_type = detect_skills_format(skills_text)
    prompt = build_skills_prompt(skills_text, missing_keywords, format_type)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"[Skills Enhancement Error] {e}")
        return skills_text  # fallback to original

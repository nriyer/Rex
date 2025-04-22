# llm_enhancer.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from keyword_matcher import extract_keywords, filter_relevant_keywords


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
def detect_skills_format(skills_text: str | list | dict) -> str:
    if isinstance(skills_text, dict):
        # Flatten values into a comma-separated string
        skills_text = ", ".join(
            item for sublist in skills_text.values() for item in (sublist if isinstance(sublist, list) else [sublist])
        )
    """
    Detects whether the skills section uses bullets or commas.

    Returns:
        'bullet' or 'comma'
    """
    if isinstance(skills_text, list):
        return "comma"  # Treat lists as comma-separated

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

# Assembles the instruction to GPT
# Embeds the original bullets
# Injects the missing keywords
# Includes the job description for tone
def build_experience_prompt(bullets: List[str], missing_keywords: List[str], job_posting: str) -> str:
    """
    Build a GPT prompt to enhance a single job's bullet points.
    - Incorporates relevant keywords
    - Aligns tone and focus with the target job posting
    """
    bullets_text = "\n".join(f"- {b}" for b in bullets)
    keyword_str = ", ".join(missing_keywords)

    prompt = f"""
You are enhancing the bullet points of a single job from a professional resume.

📌 Original Bullets:
---
{bullets_text}
---

📋 Relevant but missing keywords from the job posting:
{keyword_str}

💼 Target Job Posting (for tone and relevance alignment):
\"\"\"{job_posting.strip()}\"\"\"

🎯 Your task:
You are enhancing the bullet points of a single job from a professional resume.

- Rewrite each bullet to improve clarity, strength, and relevance.
- Integrate missing keywords naturally. No keyword stuffing.
- Match tone and terminology to the job posting (role, function, tools).
- Emphasize transferable accomplishments backed by the resume — not invented.
- Use 1 bullet per line. Combine similar ideas when possible.
- Avoid filler phrases: “responsible for”, “worked on”, etc.

📌 Bullet Rules:
- If the original job has <4 bullets, you may add 1–2 concise bullets only if clearly supported by the resume/JD.
- If there are >6 bullets, trim to the best 4–6 lines. Prioritize impact and keyword relevance.
- **Do not fabricate job titles, results, or accomplishments.**
- Highlight quantifiable impact if present — but do not invent numbers.

Return ONLY the enhanced bullets. Keep formatting consistent.

    """.strip()

    return prompt

# Takes a single job dict (title, company, date_range, bullets)
# Builds a GPT prompt with build_experience_prompt(...)
# Calls GPT-4 to rewrite the bullets
# Returns a new job dict with the same title/company/date, but enhanced bullets
def enhance_experience_job(job: dict, missing_keywords: List[str], job_posting: str) -> dict:
    """
    Enhance a single job entry using GPT-4.
    Inputs:
        job: dict with keys 'title', 'company', 'date_range', 'bullets'
        missing_keywords: relevant keywords not found in original resume
        job_posting: full JD text for tone/keyword guidance
    Returns:
        New job dict with same structure but enhanced bullet points
    """
    from openai import OpenAI  # Ensure OpenAI is loaded after dotenv
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    bullets = job["bullets"]
    if isinstance(bullets, str):
        bullets = bullets.splitlines()

    prompt = build_experience_prompt(
        bullets=bullets,
        missing_keywords=missing_keywords,
        job_posting=job_posting,
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        enhanced_text = response.choices[0].message.content.strip()
        enhanced_bullets = [
            line.strip("•- ").strip()
            for line in enhanced_text.splitlines()
            if line.strip()
        ]
                # Enforce bullet limit: Keep at most 6
        if len(enhanced_bullets) > 6:
            enhanced_bullets = enhanced_bullets[:6]
        return {
            "title": job["title"],
            "company": job["company"],
            "date_range": job["date_range"],
            "bullets": enhanced_bullets,
        }

    except Exception as e:
        print(f"[Experience Enhancement Error] {e}")
        return job  # fallback to original

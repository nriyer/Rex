# llm_enhancer.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load your OpenAI key securely
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def enhance_summary_with_gpt(summary_text: str, missing_keywords: list) -> str:
    """
    Enhance the 'summary' section of a resume using GPT-3.5,
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
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"[Summary Enhancement Error] {e}")
        return summary_text  # fallback to original

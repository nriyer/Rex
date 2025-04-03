import os
import pdfplumber
from dotenv import load_dotenv
from openai import OpenAI

from experience_splitter import split_experience_section, parse_job_entry
from parsing_module import split_resume_into_sections

# === Set up OpenAI Client ===
def setup_openai():
    load_dotenv()
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Enhance Single Job Entry ===
def enhance_job_entry_with_gpt(job, job_keywords, client, model="gpt-4"):
    context = (
        f"Company: {job['company']}\n"
        f"Title: {job['title']}\n"
        f"Dates: {job['date_range']}\n\n"
        f"Responsibilities:\n" + "\n".join(job['bullets'])
    )

    prompt = (
        "You are a professional resume writer.\n\n"
        "Improve the job description below by:\n"
        "- Enhancing clarity, conciseness, and tone\n"
        "- Limiting to 3–5 strong, high-impact bullets per job\n"
        "- Avoiding repetitive phrasing (e.g., 'leveraged', 'developed')\n"
        "- Preserving bullet formatting\n"
        f"- Integrating job keywords (only where relevant): {', '.join(job_keywords)}\n"
        "- Ensuring each bullet clearly answers 'So what?' with impact or business value\n"
        "- Quantify results (e.g., time saved, accuracy improved)\n"
        "- Do not exaggerate or invent accomplishments\n\n"
        "Rewrite this job experience:\n"
        f"```\n{context}\n```\n\n"
        "Respond only with improved bullet points in bullet format."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

# === Format Final Output ===
def format_enhanced_experience(jobs):
    blocks = []
    for job in jobs:
        blocks.append(
            f"Company: {job['company']}\n"
            f"Title: {job['title']}\n"
            f"Dates: {job['date_range']}\n\n"
            f"{job['bullets']}"
        )
    return "\n\n".join(blocks)

# === Main Pipeline ===
def enhance_resume_experience(pdf_path, job_keywords, model="gpt-4"):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Resume not found at: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        resume_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    sections = split_resume_into_sections(resume_text, pdf_path)
    experience_text = sections.get("experience", "").strip()
    if not experience_text:
        raise ValueError("No experience section found in the resume.")

    chunks = split_experience_section(experience_text)
    parsed_jobs = [parse_job_entry(chunk) for chunk in chunks]
    parsed_jobs = [job for job in parsed_jobs if job['company'] and job['title']]
    # ✅ Remove duplicate job entries based on (company, title, date_range)
    seen = set()
    deduped_jobs = []
    for job in parsed_jobs:
        job_id = (job["company"], job["title"], job["date_range"])
        if job_id not in seen:
            seen.add(job_id)
            deduped_jobs.append(job)
    parsed_jobs = deduped_jobs


    client = setup_openai()
    enhanced_jobs = []

    for job in parsed_jobs:
        bullets = enhance_job_entry_with_gpt(job, job_keywords, client, model)
        enhanced_jobs.append({
            "company": job['company'],
            "title": job['title'],
            "date_range": job['date_range'],
            "bullets": bullets
        })

    return format_enhanced_experience(enhanced_jobs)

# === Entry Point for Manual Testing ===
if __name__ == "__main__":
    job_keywords = ["SQL", "Python", "Power BI", "budget forecasting", "reporting automation", "workforce analytics"]
    pdf_path = "docs/sample_resume.pdf"
    output = enhance_resume_experience(pdf_path, job_keywords)
    print("\n=== FINAL ENHANCED EXPERIENCE SECTION ===\n")
    print(output)

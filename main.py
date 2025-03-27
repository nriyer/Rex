# main.py (Updated fully integrated version)

import os
import requests
import ast
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from parsing_module import (
    extract_text_pdfminer,
    extract_text_from_docx,
    extract_text_from_txt,
    extract_keywords,
    calculate_keyword_match,
    split_resume_into_sections,
    normalize_section_name
)

from llm_utils import enhance_section, filter_relevant_keywords


def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for element in soup(["script", "style"]):
            element.decompose()
        text = soup.get_text(separator='\n')
        lines = (line.strip() for line in text.splitlines())
        cleaned_text = '\n'.join(line for line in lines if line)
        return cleaned_text
    except Exception as e:
        print(f"Error reading job posting from URL: {e}")
        return ""


def process_resume(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_pdfminer(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format for resume.")


def process_job_posting(input_text_or_url):
    if input_text_or_url.startswith("http"):
        return extract_text_from_url(input_text_or_url)
    else:
        return input_text_or_url


def setup_environment():
    load_dotenv()
    print("✅ Environment variables loaded successfully.")


def main():
    setup_environment()

    # === 1. Process resume file ===
    resume_file = "docs/sample_resume.pdf"
    resume_text = process_resume(resume_file)
    sections = split_resume_into_sections(resume_text, pdf_path=resume_file)


    # Aggregate keywords from entire resume
    resume_keywords = extract_keywords(resume_text)

    # === 2. Process job posting ===
    job_input = """[Job posting text or URL goes here]"""
    job_text = process_job_posting(job_input)
    job_keywords = extract_keywords(job_text)

    # === 3. Calculate overlap ===
    match_percentage = calculate_keyword_match(resume_keywords, job_keywords)
    print("Keyword Match Percentage:", round(match_percentage, 2))

    enhanced_sections = {}

    if match_percentage < 80:
        missing_keywords = job_keywords - resume_keywords
        print("Raw Missing Keywords:", missing_keywords)

        # === 4. Enhance each section individually ===
        for section_name, section_text in sections.items():
            prompt_keywords_str = filter_relevant_keywords(
                extract_keywords(section_text),
                job_keywords,
                job_text
            )
            try:
                section_keywords = ast.literal_eval(prompt_keywords_str)
            except:
                section_keywords = []

            enhanced_text = enhance_section(
                section_name,
                section_text,
                section_keywords,
                job_text
            )

            enhanced_sections[section_name] = enhanced_text

        # === 5. Output enhanced sections ===
        print("\n--- Enhanced Resume Sections ---\n")
        for section, enhanced_content in enhanced_sections.items():
            print(f"## {section.capitalize()} ##\n")
            print(enhanced_content)
            print("\n")

    else:
        print("Resume already meets/exceeds the keyword threshold.")


if __name__ == "__main__":
    main()

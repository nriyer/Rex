# main.py

import os
import requests
from bs4 import BeautifulSoup
from parsing_module import (
    extract_text_pdfminer,
    extract_text_from_docx,
    extract_text_from_txt,
    extract_keywords,
    calculate_keyword_match
)

def extract_text_from_url(url):
    """
    Extracts and returns visible text from the web page at the given URL.
    Uses requests to fetch the page and BeautifulSoup to parse HTML.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()
            
        # Extract visible text from the remaining HTML
        text = soup.get_text(separator='\n')
        
        # Clean up the text by stripping and removing extra blank lines
        lines = (line.strip() for line in text.splitlines())
        cleaned_text = '\n'.join(line for line in lines if line)
        return cleaned_text
    except Exception as e:
        print(f"Error reading job posting from URL: {e}")
        return ""

def process_resume(file_path):
    """
    Determines the file type of the resume and extracts its text.
    """
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
    """
    Processes the job posting input.
    If it starts with "http", treat it as a URL; otherwise, assume it's raw text.
    """
    if input_text_or_url.startswith("http"):
        return extract_text_from_url(input_text_or_url)
    else:
        return input_text_or_url

def main():
    # 1. Process the resume file.
    resume_file = "docs/sample_resume.pdf"  # Change to .docx or .txt as needed.
    resume_text = process_resume(resume_file)
    resume_keywords = extract_keywords(resume_text)
    
    # 2. Process the job posting.
    # You can provide a full job posting URL or paste the text directly.
    # For a URL, for example:
    job_input = "https://example.com/job-posting"  # Replace with an actual job posting URL.
    # Alternatively, you could use a multi-line string if pasting raw text:
    # job_input = """
    # We are seeking a Data Analyst with expertise in SQL, Python, and Tableau.
    # Responsibilities include analyzing large datasets, building dashboards, and collaborating with cross-functional teams.
    # Requirements include proficiency in SQL and Python, and familiarity with machine learning.
    # """
    
    job_text = process_job_posting(job_input)
    job_keywords = extract_keywords(job_text)
    
    # 3. Calculate keyword match percentage.
    match_percentage = calculate_keyword_match(resume_keywords, job_keywords)
    
    print("Resume Keywords:", resume_keywords)
    print("Job Posting Keywords:", job_keywords)
    print(f"Keyword Match Percentage: {match_percentage:.2f}%")
    
    # 4. Identify missing keywords if the match is below the threshold (e.g., 80%).
    if match_percentage < 80:
        missing_keywords = job_keywords - resume_keywords
        print("Missing Keywords:", missing_keywords)
    else:
        print("The resume meets or exceeds the required keyword threshold.")

if __name__ == "__main__":
    main()

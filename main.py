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
    job_input = """" 
    At RunPod, you'll have the opportunity to work on cutting-edge technology and significantly impact the AI and ML fields. We encourage you to apply if you're driven by innovation excellence and want to be part of a team that values bold ideas and professional growth. Let's shape the future of technology together!

What You'll Work On:

Optimize the User Funnel: Use data analytics to enhance user engagement from acquisition to conversion, collaborating with marketing and sales to refine strategies.
Retention Strategies: Partner with the growth team to devise and implement data-driven retention strategies, utilizing analytics to boost user loyalty.
Monitor KPIs: Develop and track KPIs for machine reliability, working with the engineering team to ensure optimal performance.
Cross-Functional Collaboration: Serve as a liaison between technical and non-technical teams, translating data insights into actionable cross-departmental strategies.
Reporting: Provide regular updates on key metrics and strategic insights to senior management, driving data-informed decisions.

Responsibilities:

Analyze large, complex datasets to extract actionable insights about users, product performance, and operational efficiency.
Work closely with cross-functional teams, including engineering, marketing, operations, and sales, to support data-driven decision-making.
Develop and implement data collection systems and other strategies that optimize statistical efficiency and data quality.
Identify, analyze, and interpret trends or patterns in complex data sets.
Prepare reports and dashboards that use relevant data to communicate trends, patterns, and predictions.
Collaborate with engineering teams to enhance data collection and analysis processes.
Present findings and recommendations to stakeholders and executive leadership clearly and compellingly.
Stay abreast of industry trends and best practices in data analysis and data science.

Requirements:

Bachelor's degree in Data Science, Statistics, Computer Science, or a related field. A Master's degree is a plus.
At least three years of experience in a data analytics role, preferably with user and machine data exposure.
Strong analytical skills with the ability to collect, organize, analyze, and disseminate significant amounts of information with attention to detail and accuracy.
Proficiency in data analysis tools and programming languages such as SQL, Python, and R.
Experience with data visualization tools (e.g., Mode, Tableau, or Power BI).
Experience with data warehousing platforms (e.g., Snowflake, Athena, or Redshift)
Excellent verbal and written communication skills, with the ability to translate complex data into actionable insights.
Strong problem-solving skills.
Successful completion of a background check

Preferred:

A Master's degree in Data Science, Statistics, Computer Science, or a related field.
Knowledge of machine learning techniques and algorithms is a plus.
Experience at an AI, ML, LLM company
"""
    
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

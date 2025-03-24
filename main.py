# main.py

import os
import requests
import ast
from bs4 import BeautifulSoup
from parsing_module import (
    extract_text_pdfminer,
    extract_text_from_docx,
    extract_text_from_txt,
    extract_keywords,
    calculate_keyword_match
)
from llm_api import generate_text_gpt, filter_relevant_keywords

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

def create_prompt(resume_section, relevant_keywords, job_posting_text):
    prompt = (
        "You're a professional resume editor. Below is a candidate's resume section followed by a list of relevant "
        "keywords based on a job posting.\n\n"
        "Your task is to:\n"
        "1. Improve the resume section to sound more impactful and aligned with the job description.\n"
        "2. Naturally integrate the listed keywords.\n"
        "3. Write the revised section using professional bullet points focused on outcomes.\n\n"
        f"Resume Section:\n{resume_section}\n\n"
        f"Relevant Keywords: {', '.join(relevant_keywords)}\n\n"
        f"Job Posting Snippet:\n{job_posting_text[:1000]}...\n\n"
        "Return only the enhanced resume bullet points."
    )
    return prompt

def main():
    # === 1. Process resume file ===
    resume_file = "docs/sample_resume.pdf"
    resume_text = process_resume(resume_file)
    resume_keywords = extract_keywords(resume_text)

    # === 2. Process job posting ===
    job_input = """ 
    Aretum is looking for a talented AI/ML Engineer to join our team on a contingent basis. In this role, you will leverage your expertise in artificial intelligence and machine learning to drive innovative solutions and contribute to the development of advanced AI applications. As a member of our team, you will work closely with data scientists, software engineers, and other stakeholders to implement machine learning models, optimize algorithms, and enhance system performance.

Aretum specializes in delivering cutting-edge technology solutions to various sectors, including government and commercial clients. Our mission is to harness the power of AI and ML to improve decision-making processes and drive actionable insights.

Responsibilities

Design, develop, and implement machine learning models and algorithms to solve complex problems
Collaborate with data scientists and software engineers to integrate AI solutions into existing systems and applications
Analyze large datasets and extract meaningful insights to inform business strategies
Optimize and fine-tune machine learning algorithms for improved performance and scalability
Conduct experiments and A/B testing to validate model effectiveness and enhance performance
Stay up-to-date with industry trends and emerging technologies in AI and ML
Communicate findings and present technical information to both technical and non-technical stakeholders
Document processes, designs, and code for maintainability and compliance
Participate in code reviews and ensure best practices in software development are followed


Requirements


Active Secret Clearance required
Bachelor's or Master's degree in Computer Science, Mathematics, Engineering, or a related field
Proven experience working as an AI/ML Engineer or Data Scientist with a focus on machine learning techniques
Strong programming skills in Python; experience with relevant libraries such as TensorFlow, PyTorch, scikit-learn, etc
Solid understanding of machine learning algorithms, statistical methods, and data analysis
Experience with data preprocessing, feature engineering, and model evaluation techniques
Familiarity with big data technologies (e.g., Hadoop, Spark) is a plus
Knowledge of cloud computing platforms (e.g., AWS, Google Cloud, Azure) and their machine learning services
Strong analytical and problem-solving skills
Ability to work independently and collaboratively in a fast-paced environment
Excellent communication skills, both verbal and written
Preferred Skills{{:}

 Experience with deep learning techniques and neural network
 Familiarity with natural language processing (NLP) and computer vision tool
 Publication or contributions to open-source projects related to AI/ML will strengthen the application
    """
    job_text = process_job_posting(job_input)
    job_keywords = extract_keywords(job_text)

    # === 3. Calculate overlap ===
    match_percentage = calculate_keyword_match(resume_keywords, job_keywords)
    print("Keyword Match Percentage:", round(match_percentage, 2))

    if match_percentage < 80:
        missing_keywords = job_keywords - resume_keywords
        print("Raw Missing Keywords:", missing_keywords)

        # === 4. Use GPT to filter relevant keywords ===
        filtered_str = filter_relevant_keywords(resume_keywords, job_keywords, job_text)
        try:
            relevant_keywords = ast.literal_eval(filtered_str)
        except Exception:
            print("Warning: Could not parse filtered keywords properly.")
            relevant_keywords = []

        print("\nFiltered Relevant Keywords:", relevant_keywords)

        # === 5. Use GPT to improve resume section ===
        resume_section = "Summary: " + resume_text[:500]  # Example
        prompt = create_prompt(resume_section, relevant_keywords, job_text)
        enhanced_section = generate_text_gpt(prompt)

        print("\n--- Enhanced Resume Section ---\n")
        print(enhanced_section)

    else:
        print("Resume already meets/exceeds the keyword threshold.")

if __name__ == "__main__":
    main()

import PyPDF2
import docx
from pdfminer.high_level import extract_text
import re
import spacy
import string
from spacy.lang.en.stop_words import STOP_WORDS
import os
from dotenv import load_dotenv
from openai import OpenAI

# === PDF ===
def clean_extracted_text(text):
    text = text.replace("•", "")
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def extract_text_pdfminer(pdf_path):
    try:
        raw_text = extract_text(pdf_path)
        cleaned_text = clean_extracted_text(raw_text)
        return cleaned_text
    except Exception as e:
        print(f"Error reading PDF with pdfminer: {e}")
        return ""

# === DOCX ===
def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        full_text = [para.text for para in doc.paragraphs]
        return "\n".join(full_text)
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

# === TXT ===
def extract_text_from_txt(txt_path):
    try:
        with open(txt_path, "r", encoding="cp1252") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading text file: {e}")
        return ""

if __name__ == "__main__":
    print("\n=== PDF Sample ===")
    pdf_file_path = "docs/sample_resume.pdf"
    print(extract_text_pdfminer(pdf_file_path))

    print("\n=== DOCX Sample ===")
    docx_file_path = "docs/sample_resume.docx"
    print(extract_text_from_docx(docx_file_path))

    print("\n=== TXT Sample ===")
    txt_file_path = "docs/sample_resume.txt"
    print(extract_text_from_txt(txt_file_path))

# === NLP Setup ===
_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

# === Synonyms ===
SKILL_SYNONYMS = {
    "scikit-learn": "sklearn", "sklearn": "sklearn",
    "power bi": "powerbi", "microsoft excel": "excel", "ms excel": "excel", "excel": "excel",
    "amazon web services": "aws", "aws": "aws",
    "google cloud platform": "gcp", "gcp": "gcp",
    "natural language processing": "nlp", "nlp": "nlp",
    "tensorflow": "tensorflow", "pytorch": "pytorch",
    "big data": "bigdata", "machine learning": "ml", "ml": "ml",
    "ai": "ai", "artificial intelligence": "ai"
}

CUSTOM_IGNORE = set(word.lower() for word in {
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
    "Resume", "Summary", "Company", "Team", "Project", "Experience",
    "Name", "Address", "Email", "Phone", "LinkedIn", "DOCX", "PDF"
})

def normalize_keyword(keyword):
    return SKILL_SYNONYMS.get(keyword.lower(), keyword.lower())

def extract_keywords(text, allowed_pos={"NOUN", "PROPN"}):
    nlp = get_nlp()
    doc = nlp(text)
    keywords = set()
    for token in doc:
        if token.pos_ in allowed_pos and token.is_alpha and token.lower_ not in STOP_WORDS:
            lemma = token.lemma_.lower()
            if lemma not in CUSTOM_IGNORE:
                keywords.add(normalize_keyword(lemma))
    return keywords

def calculate_keyword_match(resume_keywords, job_keywords):
    if not job_keywords:
        return 0.0
    matched = resume_keywords.intersection(job_keywords)
    return (len(matched) / len(job_keywords)) * 100

# === Section Parsing ===
def setup_openai():
    load_dotenv()
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def normalize_section_name(header_text):
    name = header_text.strip().lower()
    mapping = {
        "summary": ["summary", "professional summary", "about", "bio"],
        "skills": ["skills", "technical skills", "abilities", "competencies"],
        "experience": ["experience", "work experience", "professional experience", "employment history", "work history"],
        "education": ["education", "academic background"],
        "projects": ["projects", "relevant projects"],
        "certifications": ["certifications", "certificates", "licenses"],
        "awards": ["awards", "honors"],
        "publications": ["publications", "research"],
    }
    for std_name, variants in mapping.items():
        if name in variants:
            return std_name
    # fallback to LLM
    try:
        client = setup_openai()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a resume parsing assistant."},
                {"role": "user", "content": f"Given the section title '{header_text}', which standard resume section is it most likely referring to? Return one of: summary, skills, experience, education, projects, certifications, awards, publications, or 'other'."}
            ],
            max_tokens=50
        )
        return completion.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"Warning: fallback LLM normalization failed for '{header_text}' → {e}")
        return "other"

def split_resume_into_sections(resume_text):
    sections = {}
    pattern = re.compile(r"^([A-Z][A-Za-z\s&/-]{1,50})\s*[:\n]", re.MULTILINE)
    matches = list(pattern.finditer(resume_text))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(resume_text)
        raw_header = match.group(1).strip()
        section_text = resume_text[start:end].strip()
        normalized = normalize_section_name(raw_header)
        if normalized in sections:
            sections[normalized] += "\n" + section_text
        else:
            sections[normalized] = section_text
    return sections

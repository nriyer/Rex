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
        "skills": ["skills", "technical skills", "abilities", "competencies", "professional skills"],
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
        
    VALID_SECTIONS = set(mapping.keys()).union({"other"})


    # fallback to LLM (strict, concise response)
    try:
        client = setup_openai()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a resume parsing assistant."},
                {"role": "user", "content": (
                    f"Classify '{header_text}' into exactly one category from this list: "
                    "summary, skills, experience, education, projects, certifications, awards, publications, other. "
                    "Return ONLY the single category word."
                )}
            ],
            max_tokens=10,   
            temperature=0   # enforce deterministic (non-random) answers
        )
        normalized_name = completion.choices[0].message.content.strip().lower()

        # If GPT still returns verbose answer accidentally, default to 'other'
        if normalized_name not in VALID_SECTIONS.keys() and normalized_name != "other":
            print(f"⚠️ Unexpected GPT response '{normalized_name}'. Defaulting to 'other'.")
            return "other"

        return normalized_name

    except Exception as e:
        print(f"⚠️ Fallback LLM normalization failed for '{header_text}' → {e}")
        return "other"


def split_resume_into_sections(resume_text):
    sections = {}

    # Split lines once and store
    lines = resume_text.splitlines()

    # Dynamically capture the first line as a likely name
    FALSE_HEADERS = set([
        "resume", "curriculum vitae", "cv", "name", "contact", "contact information"
    ])
    if lines:
        FALSE_HEADERS.add(lines[0].strip().lower())

    VALID_SECTIONS = {
        "summary", "skills", "experience", "education",
        "projects", "certifications", "awards", "publications"
    }
    

    pattern = re.compile(r"^(?:\s*)([A-Z][A-Za-z\s&/-]{1,40})(?::)?\s*$", re.MULTILINE)
    matches = list(pattern.finditer(resume_text))

    for idx, match in enumerate(matches):
        raw_header = match.group(1).strip()
        if raw_header.lower() in FALSE_HEADERS:
            continue

        # Check line context
        match_line_num = resume_text[:match.start()].count("\n")
        prev_line = lines[match_line_num - 1].strip() if match_line_num > 0 else ""
        next_line = lines[match_line_num + 1].strip() if match_line_num + 1 < len(lines) else ""

        if prev_line.startswith("•") or next_line.startswith("•") or len(next_line.split()) > 6:
            continue

        # Normalize section name via your LLM logic
        normalized = normalize_section_name(raw_header)

        # ✅ New: Accept only recognized section types
        if normalized not in VALID_SECTIONS:
            continue

        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(resume_text)
        section_text = resume_text[start:end].strip()

        if normalized in sections:
            sections[normalized] += "\n" + section_text
        else:
            sections[normalized] = section_text

    return sections



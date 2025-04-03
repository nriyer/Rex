import PyPDF2
import pdfplumber
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

    # Known variant mappings
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

    # Try matching via local mapping
    for std_name, variants in mapping.items():
        if name in variants:
            return std_name

    VALID_SECTIONS = set(mapping.keys()).union({"other"})

    # Fallback to GPT with strict response expectations
    try:
        client = setup_openai()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a resume parsing assistant."},
                {"role": "user", "content": (
                    f"Classify '{header_text}' into one of the following categories: "
                    "summary, skills, experience, education, projects, certifications, awards, publications, other. "
                    "Return ONLY the single category word with no explanation."
                )}
            ],
            max_tokens=10,
            temperature=0
        )

        raw_response = completion.choices[0].message.content.strip().lower()
        raw_response = raw_response.strip(string.punctuation).strip()

        print(f"[normalize_section_name] GPT returned: '{raw_response}' for '{header_text}'")

        # ✅ Strict enforcement: must be exactly one known word
        if raw_response in VALID_SECTIONS:
            return raw_response

        print(f"⚠️ Rejected GPT response: '{raw_response}' → defaulting to 'other'")
        return "other"
    
    except Exception as e:
        print(f"⚠️ LLM normalization failed for '{header_text}' → {e}")
        return "other"



def extract_headers_with_pdfplumber(pdf_path, font_size_threshold=13):
    headers = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for obj in page.extract_words(extra_attrs=["size"]):
                    if float(obj["size"]) >= font_size_threshold:
                        line = obj["text"].strip()
                        if line and line not in headers:
                            headers.append(line)
                        # Force-include Experience if embedded in large font
                        if "experience" in line.lower() and "experience" not in headers:
                            headers.append("Experience")
    except Exception as e:
        print(f"[pdfplumber error] {e}")
    return headers

def split_resume_into_sections(resume_text, pdf_path=None):
    # Clean up spacing issues to ensure headers match correctly
    resume_text = "\n".join([line.strip() for line in resume_text.splitlines()])
    sections = {}
    lines = resume_text.splitlines()

    FALSE_HEADERS = set([
        "resume", "curriculum vitae", "cv", "name", "contact", "contact information"
    ])
    if lines:
        FALSE_HEADERS.add(lines[0].strip().lower())

    VALID_SECTIONS = {
        "summary", "skills", "experience", "education",
        "projects", "certifications", "awards", "publications"
    }

    KNOWN_HEADER_PHRASES = {
        "professional summary", "summary",
        "professional skills", "technical skills", "technical abilities", "skills",
        "experience", "work experience", "professional experience", "work history", "work",
        "education", "education and certifications", "certifications and education",
        "projects", "certifications", "awards", "publications",
        "independent learning", "independent projects"
    }

    high_confidence_headers = set()
    if pdf_path:
        high_confidence_headers = set(map(str.lower, extract_headers_with_pdfplumber(pdf_path)))

    pattern = re.compile(r"^(?:\s*)([A-Z][A-Za-z\s&/-]{1,40})(?::)?\s*$", re.MULTILINE)
    matches = list(pattern.finditer(resume_text))

    for idx, match in enumerate(matches):
        raw_header = match.group(1).strip()
        match_line_num = resume_text[:match.start()].count("\n")

        if raw_header.lower() in FALSE_HEADERS:
            continue
        if len(raw_header.split()) > 5:
            continue
        if not raw_header[0].isupper():
            continue

        skip_lines = 0
        next_line_idx = match_line_num + 1
        if next_line_idx < len(lines) and re.match(r"^-{3,}$", lines[next_line_idx].strip()):
            skip_lines = 1
            next_line_idx += 1

        prev_line = lines[match_line_num - 1].strip() if match_line_num > 0 else ""
        next_line = lines[next_line_idx].strip() if next_line_idx < len(lines) else ""

        if prev_line.startswith(("•", "-", "*")) or next_line.startswith(("•", "-", "*")):
            continue

        normalized = None
        if raw_header.lower() in high_confidence_headers:
            normalized = normalize_section_name(raw_header)
        elif raw_header.lower() in KNOWN_HEADER_PHRASES or any(raw_header.lower() in h for h in high_confidence_headers):
            normalized = normalize_section_name(raw_header)
        else:
            continue

        if normalized not in VALID_SECTIONS:
            continue

        start = match.end()
        if skip_lines:
            start = resume_text.find('\n', start) + 1
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(resume_text)
        section_text = resume_text[start:end].strip()

        if normalized in sections:
            sections[normalized] += "\n" + section_text
        else:
            sections[normalized] = section_text

    # === Inject any pdfplumber headers not found via regex ===
    for h in high_confidence_headers:
        if h in VALID_SECTIONS and h not in sections:
            print(f"[INJECTED] Forcing section '{h}' from pdfplumber headers")
            sections[h] = ""

    # === Inject any pdfplumber headers not found via regex ===
    for h in high_confidence_headers:
        if h in VALID_SECTIONS and h not in sections:
            print(f"[INJECTED] Forcing section '{h}' from pdfplumber headers")
            sections[h] = ""

    return sections









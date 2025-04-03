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

# === PDF TEXT CLEANUP ===
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

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        full_text = [para.text for para in doc.paragraphs]
        return "\n".join(full_text)
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

def extract_text_from_txt(txt_path):
    try:
        with open(txt_path, "r", encoding="cp1252") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading text file: {e}")
        return ""

# === SPA Cy ===
_nlp = None
def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

SKILL_SYNONYMS = {
    "scikit-learn": "sklearn", "power bi": "powerbi", "microsoft excel": "excel",
    "ms excel": "excel", "excel": "excel", "aws": "aws", "gcp": "gcp",
    "nlp": "nlp", "tensorflow": "tensorflow", "pytorch": "pytorch",
    "big data": "bigdata", "machine learning": "ml", "ml": "ml", "ai": "ai"
}

CUSTOM_IGNORE = set(word.lower() for word in {
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December", "Resume", "Summary", "Company",
    "Team", "Project", "Experience", "Name", "Address", "Email", "Phone", "LinkedIn",
    "DOCX", "PDF"
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

# === GPT SETUP ===
def setup_openai():
    load_dotenv()
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Section Normalization ===
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
        return raw_response if raw_response in VALID_SECTIONS else "other"
    except:
        return "other"

# === Fallback Experience Extractor ===
def extract_experience_from_raw_text(resume_text):
    match = re.search(
        r"(experience|work history|employment|professional experience)(.*?)"
        r"((education|projects|certifications|skills|summary))",
        resume_text,
        re.IGNORECASE | re.DOTALL,
    )
    return match.group(2).strip() if match else ""

# === PDF Header Extractor ===
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
                        if "experience" in line.lower() and "experience" not in headers:
                            headers.append("Experience")
    except Exception as e:
        print(f"[pdfplumber error] {e}")
    return headers

# === MAIN PARSER ===
def split_resume_into_sections(resume_text, pdf_path=None):
    resume_text = "\n".join([line.strip() for line in resume_text.splitlines()])
    sections = {}
    lines = resume_text.splitlines()

    FALSE_HEADERS = {"resume", "cv", "curriculum vitae", "name", "contact", "contact information"}
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

        if raw_header.lower() in FALSE_HEADERS or len(raw_header.split()) > 5 or not raw_header[0].isupper():
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
            norm = normalize_section_name(h)
            if norm in VALID_SECTIONS and norm not in sections:
                print(f"[Fallback] No '{norm}' section found. Trying raw text extraction for {norm} section...")

        # Try to find the raw header and extract lines below it
            pattern = re.compile(rf"{re.escape(h)}", re.IGNORECASE)
            match = pattern.search(resume_text)
            if match:
                start = match.end()
                end = len(resume_text)
                section_text = resume_text[start:end].strip()
                sections[norm] = section_text
            else:
                sections[norm] = ""


    # Final fallback: if experience is still missing, try regex fallback
    if "experience" not in sections or not sections["experience"].strip():
        print("[Fallback] Trying raw text extraction for experience section...")
        fallback_text = extract_experience_from_raw_text(resume_text)
        if fallback_text:
            sections["experience"] = fallback_text

    return sections

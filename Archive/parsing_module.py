import os
import re
import pdfplumber
import docx2txt

# === TEXT EXTRACTION ===

def extract_text_pdfplumber(pdf_path):
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
    except Exception as e:
        print(f"[pdfplumber error] {e}")
    return full_text.strip()

def extract_text_from_docx(docx_path):
    try:
        return docx2txt.process(docx_path)
    except Exception as e:
        print(f"[docx error] {e}")
        return ""

def extract_text_from_txt(txt_path):
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[txt error] {e}")
        return ""

# === SECTION NORMALIZATION (RULE-BASED ONLY) ===

def normalize_section_name(header_text):
    text = header_text.strip().lower()
    mapping = {
        "summary": {"summary", "professional summary"},
        "skills": {"skills", "technical skills", "professional skills", "technical abilities"},
        "experience": {
            "experience", "work experience", "employment history",
            "professional experience", "work history", "work"
        },
        "education": {
            "education", "academic background", "education and certifications", "certifications and education"
        },
        "projects": {"projects", "relevant projects", "independent projects"},
        "certifications": {"certifications", "certificates", "licenses"},
        "awards": {"awards", "honors"},
        "publications": {"publications", "research"}
    }

    for key, variants in mapping.items():
        if text in variants:
            return key
    return None  # Let fallback handle if necessary

# === MAIN SECTION SPLITTER ===

def split_resume_into_sections(resume_text, pdf_path=None):
    KNOWN_HEADER_PHRASES = {
        "professional summary", "summary",
        "professional skills", "technical skills", "technical abilities", "skills",
        "experience", "work experience", "professional experience", "work history", "work",
        "education", "education and certifications", "certifications and education",
        "projects", "certifications", "awards", "publications",
        "independent learning", "independent projects"
    }

    lines = resume_text.splitlines()
    sections = {}
    current_section = None
    buffer = []

    for line in lines:
        header_candidate = line.strip().lower()

        if header_candidate in KNOWN_HEADER_PHRASES:
            normalized = normalize_section_name(header_candidate)
            if normalized:
                if current_section and buffer:
                    sections[current_section] = "\n".join(buffer).strip()
                    buffer = []
                current_section = normalized
                continue

        if current_section:
            buffer.append(line)

    if current_section and buffer:
        sections[current_section] = "\n".join(buffer).strip()

    # === GPT Fallback for missing sections ===
    required_sections = {"summary", "skills", "experience", "education"}
    missing = required_sections - set(sections.keys())

    if missing:
        print(f"[GPT fallback] Missing sections: {missing}")
        unknown_candidates = []
        for line in lines:
            line_clean = line.strip().lower()
            if (
                1 < len(line_clean) < 60 and
                not line.startswith(("•", "-", "*")) and
                not any(char.isdigit() for char in line) and
                line_clean not in KNOWN_HEADER_PHRASES and
                line == line.title() and len(line.split()) <= 6
            ):
                unknown_candidates.append(line.strip())

            classified = {}

        for raw, label in classified.items():
            normalized = label.strip().lower()
            if normalized in missing and normalized not in sections:
                print(f"[GPT] Matched '{raw}' → '{normalized}'")
                start = resume_text.lower().find(raw.lower())
                end = len(resume_text)
                section_text = resume_text[start:end].strip()
                sections[normalized] = section_text

    return sections


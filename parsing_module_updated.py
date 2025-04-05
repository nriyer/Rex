import re
import pdfplumber
from pdfminer.high_level import extract_text


def extract_text_pdfminer(pdf_path):
    try:
        raw_text = extract_text(pdf_path)
        return raw_text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""


def extract_visual_headers(pdf_path, font_threshold=13):
    headers = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for obj in page.extract_words(extra_attrs=["size"]):
                    if float(obj["size"]) >= font_threshold:
                        header = obj["text"].strip()
                        if header and header not in headers:
                            headers.append(header)
    except Exception as e:
        print(f"[pdfplumber error] {e}")
    return headers


def normalize_section_name(text):
    mapping = {
        "summary": ["summary", "professional summary"],
        "skills": ["skills", "technical skills", "professional skills"],
        "experience": ["experience", "work experience", "employment history"],
        "education": ["education", "academic background"],
        "projects": ["projects", "relevant projects"],
        "certifications": ["certifications", "certificates", "licenses"],
        "awards": ["awards", "honors"],
        "publications": ["publications", "research"],
    }

    text = text.lower().strip()
    for norm, variants in mapping.items():
        if text in variants:
            return norm
    return "other"


def split_resume_into_sections(resume_text, pdf_path=None):
    lines = resume_text.splitlines()
    resume_text = "\n".join([line.strip() for line in lines])

    # Step 1: Try to get headers using visual PDF parsing
    headers = extract_visual_headers(pdf_path) if pdf_path else []
    print(f"[DEBUG] Headers from pdfplumber: {headers}")

    pattern = re.compile(r"^(?:\s*)([A-Z][A-Za-z\s&/-]{1,40})(?::)?\s*$", re.MULTILINE)
    matches = list(pattern.finditer(resume_text))
    print(f"[DEBUG] Found {len(matches)} candidate headers via regex.")

    sections = {}
    for idx, match in enumerate(matches):
        raw_header = match.group(1).strip()
        normalized = normalize_section_name(raw_header)
        print(f"[DEBUG] Raw: '{raw_header}' → Normalized: '{normalized}'")

        if normalized == "other":
            continue

        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(resume_text)
        content = resume_text[start:end].strip()

        if normalized in sections:
            sections[normalized] += "\n" + content
        else:
            sections[normalized] = content

    return sections

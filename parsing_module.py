import PyPDF2
import docx
from pdfminer.high_level import extract_text
import re
import spacy
import string
from spacy.lang.en.stop_words import STOP_WORDS

#PDF
def clean_extracted_text(text):
    """
    Cleans extracted text by removing extra line breaks, bullet points, etc.
    """
    # Remove bullet characters
    text = text.replace("•", "")
    # Replace multiple consecutive newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    # Strip leading/trailing whitespace
    return text.strip()

def extract_text_pdfminer(pdf_path):
    """
    Extracts text from a PDF file using pdfminer.six, then cleans the extracted text.
    """
    try:
        raw_text = extract_text(pdf_path)
        cleaned_text = clean_extracted_text(raw_text)
        return cleaned_text
    except Exception as e:
        print(f"Error reading PDF with pdfminer: {e}")
        return ""

# Example usage:

#Docx
def extract_text_from_docx(docx_path):
    """
    Extracts text from a DOCX file using python-docx.
    """
    try:
        doc = docx.Document(docx_path)
        full_text = [para.text for para in doc.paragraphs]
        return "\n".join(full_text)
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

    
#Plain Text
def extract_text_from_txt(txt_path):
    """
    Reads text from a plain text file.
    """
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

   
   
#Keyword Extraction
_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

# === Synonym mapping for tech/tools/skills ===
SKILL_SYNONYMS = {
    "scikit-learn": "sklearn",
    "sklearn": "sklearn",
    "power bi": "powerbi",
    "microsoft excel": "excel",
    "ms excel": "excel",
    "excel": "excel",
    "amazon web services": "aws",
    "aws": "aws",
    "google cloud platform": "gcp",
    "gcp": "gcp",
    "natural language processing": "nlp",
    "nlp": "nlp",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "big data": "bigdata",
    "machine learning": "ml",
    "ml": "ml",
    "ai": "ai",
    "artificial intelligence": "ai"
}

# === Custom ignore list ===
CUSTOM_IGNORE = set(word.lower() for word in {
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
    "Resume", "Summary", "Company", "Team", "Project", "Experience",
    "Name", "Address", "Email", "Phone", "LinkedIn", "DOCX", "PDF"
})

def normalize_keyword(keyword):
    """
    Map a keyword to its canonical form using SKILL_SYNONYMS.
    If no mapping exists, return the original keyword.
    """
    return SKILL_SYNONYMS.get(keyword.lower(), keyword.lower())

def extract_keywords(text, allowed_pos={"NOUN", "PROPN"}):
    """
    Extracts and normalizes keywords from the input text.
    Returns a set of lowercased, lemmatized, and synonym-mapped keywords.
    """
    nlp = get_nlp()
    doc = nlp(text)
    keywords = set()

    for token in doc:
        if (
            token.pos_ in allowed_pos
            and token.is_alpha
            and token.lower_ not in STOP_WORDS
        ):
            lemma = token.lemma_.lower()
            if lemma not in CUSTOM_IGNORE:
                normalized = normalize_keyword(lemma)
                keywords.add(normalized)

    return keywords



#Keyword Matching
def calculate_keyword_match(resume_keywords, job_keywords):
    """
    Calculates the percentage of job keywords that appear in the resume.
    Returns a float (0-100).
    """
    if not job_keywords:
        return 0.0  # Avoid division by zero if the job posting has no keywords

    matched = resume_keywords.intersection(job_keywords)
    match_percentage = (len(matched) / len(job_keywords)) * 100
    return match_percentage

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
if __name__ == "__main__":
    # Update the path to match where your PDF is located.
    # For example, if your project has a "docs" folder with "sample_resume.pdf":
    pdf_file_path = "docs/sample_resume.pdf"  
    pdf_text = extract_text_pdfminer(pdf_file_path)
    print("Extracted and Cleaned Text from PDF (pdfminer):")
    print(pdf_text)

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

# Example usage:
if __name__ == "__main__":
    docx_file_path = "docs/sample_resume.docx"  # Place a sample DOCX file in your project folder
    docx_text = extract_text_from_docx(docx_file_path)
    print("Extracted Text from DOCX:")
    print(docx_text)
    
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

# Example usage:
if __name__ == "__main__":
    txt_file_path = "docs/sample_resume.txt"  # Place a sample TXT file in your project folder
    txt_text = extract_text_from_txt(txt_file_path)
    print("Extracted Text from TXT:")
    print(txt_text)
   
   
#Keyword Extraction
nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    """
    Extract keywords (nouns/proper nouns) from text using spaCy.
    Returns a set of keyword strings.
    """
    doc = nlp(text)
    keywords = set()

    for token in doc:
        # Conditions for a 'keyword' token
        if (
            token.pos_ in ["NOUN", "PROPN"]    # Must be a noun or proper noun
            and token.is_alpha                # Must be alphabetic
            and token.lower_ not in STOP_WORDS
        ):
            # Use the lemma (base form) and make it lowercase for consistency
            keywords.add(token.lemma_.lower())

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

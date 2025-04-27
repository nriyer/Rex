import os
import subprocess
import tempfile
import mammoth
import pypandoc
from pdf2docx import Converter
import re


def convert_resume_to_html(file_path: str) -> str:
    """
    Converts a resume file (.pdf, .docx, or .txt) to clean, readable HTML.
    Returns HTML string content for downstream GPT-based parsing.
    """
    try:
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            from pdf2docx import Converter
            import uuid

            with tempfile.TemporaryDirectory() as temp_dir:
                # Convert PDF to temporary .docx
                docx_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.docx")
                converter = Converter(file_path)
                converter.convert(docx_path, start=0, end=None)
                converter.close()

                # Use mammoth to convert DOCX to HTML
                with open(docx_path, "rb") as docx_file:
                    result = mammoth.convert_to_html(docx_file)
                    html_content = result.value


        elif file_extension == '.docx':
            with open(file_path, 'rb') as docx_file:
                result = mammoth.convert_to_html(docx_file)
                html_content = result.value

        elif file_extension == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    lines = txt_file.readlines()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as txt_file:
                    lines = txt_file.readlines()

            html_content = ''.join(f'<p>{line.strip()}</p>' for line in lines)


        else:
            raise ValueError("Unsupported file format")
    
        html_content = re.sub(r'<img\s+src="data:image/[^>]+>', '', html_content)
        return html_content

    except Exception as e:
        print(f"Error converting file: {e}")
        return ""


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python html_converter.py <file_path>")
    else:
        file_path = sys.argv[1]
        html_content = convert_resume_to_html(file_path)
        print(html_content[:500]) 
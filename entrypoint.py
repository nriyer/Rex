# entrypoint.py

from Rough.old_workflow import run_enhancement_pipeline
from environment import setup_environment

if __name__ == "__main__":
    setup_environment()

    resume_file = "docs/sample_resume.pdf"
    job_input = """Paste your job description or URL here"""

    result = run_enhancement_pipeline(resume_file, job_input)

    for section, content in result.items():
        print(f"\n## {section.upper()} ##\n{content}\n")

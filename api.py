from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File, Form
from workflow import run_resume_enhancement_pipeline
from parsing_module import extract_text_pdfplumber, extract_text_from_docx, extract_text_from_txt

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Resume Optimizer API"}

@app.post("/optimize-resume")
async def optimize_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    format_template: str = Form(default="ATS-friendly")
):
    # Step 1: Extract text from uploaded resume
    if resume_file.filename.endswith(".pdf"):
        resume_text = extract_text_pdfplumber(resume_file.file)
    elif resume_file.filename.endswith(".docx"):
        resume_text = extract_text_from_docx(resume_file.file)
    elif resume_file.filename.endswith(".txt"):
        resume_text = extract_text_from_txt(resume_file.file)
    else:
        return {"error": "Unsupported file format"}

    # Step 2: Run enhancement pipeline
    final_resume, score_report = run_resume_enhancement_pipeline(resume_text, job_description)

    # Step 3: Return result
    return {
        "enhanced_resume": final_resume,
        "score_report": score_report,
        "template_used": format_template
    }

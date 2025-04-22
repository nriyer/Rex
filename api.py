from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from workflow import run_resume_enhancement_pipeline
from Archive.parsing_module import extract_text_pdfplumber, extract_text_from_docx, extract_text_from_txt
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ResumeOptimizationRequest(BaseModel):
    resume_text: str
    job_posting: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Resume Optimizer API"}

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    try:
        if file.filename.endswith(".pdf"):
            text = extract_text_pdfplumber(file.file)
        elif file.filename.endswith(".docx"):
            text = extract_text_from_docx(file.file)
        elif file.filename.endswith(".txt"):
            text = extract_text_from_txt(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize-resume")
async def optimize_resume(request: ResumeOptimizationRequest):
    try:
        # Run enhancement pipeline
        final_resume, score_report = run_resume_enhancement_pipeline(
            request.resume_text,
            request.job_posting
        )

        # Return result
        return {
            "enhanced_resume": final_resume,
            "score_report": score_report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

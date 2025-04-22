from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from workflow import run_resume_enhancement_pipeline
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
    html_resume: str
    job_posting: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Resume Optimizer API"}

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_upload.{file.filename.split('.')[-1]}"
        with open(temp_path, "wb") as f_out:
            content = await file.read()
            f_out.write(content)

        # Convert to HTML using updated converter
        from html_converter import convert_resume_to_html
        html = convert_resume_to_html(temp_path)

        return {"html_resume": html}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize-resume")
async def optimize_resume(request: ResumeOptimizationRequest):
    try:
        # Run enhancement pipeline
        final_resume, score_report = run_resume_enhancement_pipeline(
            request.html_resume,
            request.job_posting
        )

        # Return result
        return {
            "enhanced_resume": final_resume,
            "score_report": score_report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

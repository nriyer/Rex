# Resume Optimizer

A comprehensive web application that streamlines your job application process by optimizing resumes for multiple job postings using AI-powered analysis and enhancement.

## Features

### Resume Management
- Upload or build your base resume
- Store and manage multiple resume versions
- Intelligent resume parsing and section detection

### Job Application Optimization
- Input multiple job descriptions simultaneously
- Generate tailored, ATS-optimized resumes for each position
- View match scores and suggested improvements
- Track optimization history and improvements

### Automated Application Support
- Auto-apply functionality for supported job platforms
- Export packages of tailored resumes with corresponding job descriptions
- Batch processing for multiple applications

### Application Tracking
- Centralized dashboard for monitoring all applications
- Track application status and follow-ups
- Analytics on resume performance and optimization impact

### Technical Features
- AI-powered resume enhancement
- ATS compatibility checking
- Keyword optimization and scoring
- Professional formatting templates

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ResumeOptimizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

1. Start the FastAPI backend:
```bash
uvicorn api:app --reload
```

2. In a new terminal, start the Streamlit frontend:
```bash
streamlit run app.py
```

Alternatively, use the provided PowerShell script to start both services:
```powershell
.\run.ps1
```

3. Open your browser and navigate to:
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## Usage

1. Resume Setup
   - Upload your base resume (PDF/DOCX) or create one using the builder
   - Review the parsed sections and make any necessary adjustments

2. Job Description Input
   - Paste job descriptions or import from supported job boards
   - Add multiple positions for batch processing

3. Optimization Process
   - Click "Optimize Resume" to process all selected jobs
   - Review match scores and suggested improvements
   - Fine-tune optimizations if needed

4. Application Management
   - Auto-apply for supported positions
   - Download optimized resume packages for manual applications
   - Track application status from the dashboard

## Architecture

- Frontend: Streamlit
- Backend: FastAPI
- AI Processing: OpenAI GPT
- File Processing: PDFPlumber, python-docx
- Database: SQLite (for application tracking)

## Roadmap

- [ ] Integration with major job boards
- [ ] Enhanced auto-apply functionality
- [ ] Resume version control
- [ ] Application analytics dashboard
- [ ] Email notification system
- [ ] Mobile app support

## License

MIT License

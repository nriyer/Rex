# Resume Optimizer

A web application that helps optimize your resume to better match job descriptions using AI-powered analysis and enhancement.

## Features

- Upload or paste your resume
- Input job descriptions
- Get AI-enhanced resume suggestions
- View match scores and improvements
- Download optimized resume

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

3. Open your browser and navigate to:
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## Usage

1. Choose how to input your resume:
   - Upload a PDF file
   - Paste resume text directly

2. Input the job description you want to optimize for

3. Click "Optimize Resume" to process

4. View the enhanced resume and score report

5. Download the optimized resume if desired

## Architecture

- Frontend: Streamlit
- Backend: FastAPI
- AI Processing: OpenAI GPT
- File Processing: PDFPlumber, python-docx

## License

MIT License

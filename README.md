# Rex — AI Resume Optimizer

An AI-powered resume optimizer built with Streamlit + FastAPI.

# Resume Optimizer

Rex streamlines your job application process by optimizing resumes for multiple job postings using AI-powered analysis and enhancement.

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
---

## 🚀 Quick Start

## 🚀 Setup

1. Make sure Docker and Docker Compose are installed.
2. Clone the Rex repo:
   ```bash
   git clone https://github.com/nriyer/Rex.git
   cd Rex

To run Dev environment:

 ```bash
Copy code
docker-compose up backend-dev frontend-dev

To run Staging environment:

bash
Copy code
docker-compose up backend-staging frontend-staging

Access the app:

Environment	Frontend URL	Backend URL
Dev	http://localhost:8501	http://localhost:8000
Staging	http://localhost:8502	http://localhost:8001

## Services Overview - Services Description
backend-dev	FastAPI server for development
frontend-dev	Streamlit app for development
backend-staging	FastAPI server for staging
frontend-staging	Streamlit app for staging


## Stop all services
In your terminal:

bash
Copy code
docker-compose down
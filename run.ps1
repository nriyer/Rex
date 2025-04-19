Write-Host "Starting Resume Optimizer..."
Write-Host "Starting FastAPI backend..."
Start-Process powershell -ArgumentList "uvicorn api:app --reload"

Write-Host "Starting Streamlit frontend..."
Start-Process powershell -ArgumentList "streamlit run app.py"

Write-Host "Services started!"
Write-Host "FastAPI backend running at: http://127.0.0.1:8000"
Write-Host "Streamlit frontend running at: http://localhost:8501"
Write-Host "Press Ctrl+C to stop all services"

# Keep the script running
while ($true) {
    Start-Sleep -Seconds 1
} 
# Makefile for Rex Project

# Activate venv and run Streamlit frontend
run-streamlit:
	@source venv/bin/activate && streamlit run app/main.py

# Activate venv and run FastAPI backend (if needed separately)
run-fastapi:
	@source venv/bin/activate && uvicorn api:app --reload

# Setup everything (bootstrap if needed)
bootstrap:
	@chmod +x bootstrap.sh && ./bootstrap.sh

# Clean venv (dangerous: use with caution!)
clean-venv:
	@rm -rf venv

# Install Python dependencies
install:
	@source venv/bin/activate && pip install -r requirements.txt

import os
from dotenv import load_dotenv

def setup_environment():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("❌ OPENAI_API_KEY not found in .env file")
    print("✅ Environment loaded.")

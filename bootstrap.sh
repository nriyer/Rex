#!/bin/bash

echo "🚀 Starting Rex project bootstrap..."

# Check if venv folder exists
if [ ! -d "venv" ]; then
  echo "🛠 Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
echo "🔑 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing project dependencies..."
pip install -r requirements.txt

# Check if wkhtmltopdf is installed
if ! command -v wkhtmltopdf &> /dev/null; then
  echo "⚠️  wkhtmltopdf not found. Please install it manually for PDF export."
fi

# Check if .env exists
if [ ! -f ".env" ]; then
  echo "⚠️  .env file not found. Please create a .env file with your OPENAI_API_KEY before running."
else
  echo "✅ .env file found."
fi

# Run the project
echo "🚀 Running development server..."
python manage.py dev

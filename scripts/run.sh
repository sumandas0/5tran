#!/bin/bash

# Quick run script for 5Tran

echo "🚀 Starting 5Tran AI Pipeline Automation..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: bash scripts/setup.sh"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating from template..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and add your GEMINI_API_KEY"
    echo ""
fi

# Run the app
echo "Starting Gradio UI..."
echo "Open http://localhost:7860 in your browser"
echo ""
python src/ui/app.py


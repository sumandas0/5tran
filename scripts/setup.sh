#!/bin/bash

# 5Tran Setup Script

echo "🚀 Setting up 5Tran AI Pipeline Automation"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo ""
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -e . 

echo ""
echo "✓ Dependencies installed"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - GEMINI_API_KEY (required)"
    echo "   - GCP_PROJECT_ID (optional for dev)"
    echo ""
else
    echo ""
    echo ".env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p configs/fivetran
mkdir -p dbt_project/models/staging
mkdir -p dbt_project/models/marts
mkdir -p examples
echo "✓ Directories created"

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GEMINI_API_KEY"
echo "2. Run: python src/ui/app.py"
echo "3. Open http://localhost:7860 in your browser"
echo ""
echo "For testing without UI:"
echo "  python scripts/test_pipeline.py"
echo ""


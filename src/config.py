"""Configuration management for 5Tran."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
CONFIGS_DIR = PROJECT_ROOT / "configs"
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"
EXAMPLES_DIR = PROJECT_ROOT / "examples"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIVETRAN_API_KEY = os.getenv("FIVETRAN_API_KEY")
FIVETRAN_API_SECRET = os.getenv("FIVETRAN_API_SECRET")

# GCP / BigQuery
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "dev_pipeline_test")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Gemini Settings
GEMINI_MODEL_FAST = "gemini-2.5-flash-preview-09-2025"
GEMINI_MODEL_PRO = "gemini-2.5-pro"
GEMINI_TEMPERATURE = 0.2

# Development mode
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
MOCK_FIVETRAN = os.getenv("MOCK_FIVETRAN", "true").lower() == "true"

def validate_config():
    """Validate essential configuration."""
    missing = []
    
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    
    if not DEV_MODE and not GCP_PROJECT_ID:
        missing.append("GCP_PROJECT_ID")
    
    if missing:
        print(f"⚠️  Warning: Missing configuration: {', '.join(missing)}")
        print("Create a .env file based on .env.example")
        return False
    
    return True


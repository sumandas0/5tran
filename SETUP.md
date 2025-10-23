# 🛠️ Setup Guide for 5Tran

This guide will help you set up 5Tran AI Pipeline Automation on your local machine.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed ([Download Python](https://www.python.org/downloads/))
- **Git** installed ([Download Git](https://git-scm.com/downloads))
- **Google Gemini API Key** ([Get API Key](https://ai.google.dev/))
- (Optional) **Google Cloud Project** with BigQuery enabled
- (Optional) **Fivetran Account**

## Installation Methods

### Method 1: Automated Setup (Recommended)

This is the fastest way to get started:

```bash
# 1. Clone the repository
git clone <repository-url>
cd 5tran

# 2. Run the setup script
bash scripts/setup.sh

# 3. Edit .env and add your Gemini API key
nano .env  # or use your favorite editor

# 4. Run the application
bash scripts/run.sh
```

### Method 2: Manual Setup

If you prefer to set things up manually:

```bash
# 1. Clone the repository
git clone <repository-url>
cd 5tran

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e .

# 4. Create .env file
cp .env.example .env

# 5. Edit .env and add your API keys
nano .env

# 6. Create necessary directories
mkdir -p configs/fivetran
mkdir -p dbt_project/models/{staging,marts}

# 7. Run the application
python src/ui/app.py
```

### Method 3: Using UV (Fast)

If you have [uv](https://github.com/astral-sh/uv) installed:

```bash
# 1. Clone and navigate
git clone <repository-url>
cd 5tran

# 2. Install dependencies with uv
uv pip install -e .

# 3. Setup .env
cp .env.example .env
nano .env

# 4. Run
python src/ui/app.py
```

## Configuration

### Required Configuration

Edit your `.env` file and add at minimum:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Getting a Gemini API Key:**
1. Go to [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Click "Get API Key"
4. Copy your API key to `.env`

### Optional Configuration

For full functionality (not required for development):

```env
# Google Cloud / BigQuery
GCP_PROJECT_ID=your_gcp_project_id
BIGQUERY_DATASET=dev_pipeline_test

# Path to service account key (if not using OAuth)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Fivetran (if you want to use real connectors)
FIVETRAN_API_KEY=your_fivetran_api_key
FIVETRAN_API_SECRET=your_fivetran_secret

# Development mode (default: true)
DEV_MODE=true
MOCK_FIVETRAN=true
```

### Google Cloud Setup (Optional)

If you want to use real BigQuery:

1. **Create a GCP Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable BigQuery API**
   - Navigate to "APIs & Services" > "Enable APIs and Services"
   - Search for "BigQuery API"
   - Click "Enable"

3. **Create Service Account (Optional)**
   ```bash
   # Using gcloud CLI
   gcloud iam service-accounts create 5tran-service-account
   
   # Grant BigQuery permissions
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:5tran-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/bigquery.admin"
   
   # Download key
   gcloud iam service-accounts keys create service-account-key.json \
     --iam-account=5tran-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

4. **Update .env**
   ```env
   GCP_PROJECT_ID=YOUR_PROJECT_ID
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

### Fivetran Setup (Optional)

For real Fivetran connectors:

1. Sign up at [Fivetran](https://fivetran.com/)
2. Generate API key and secret in your account settings
3. Add to `.env`:
   ```env
   FIVETRAN_API_KEY=your_key
   FIVETRAN_API_SECRET=your_secret
   MOCK_FIVETRAN=false
   ```

## Verification

### Test the Installation

Run the test script to verify everything is working:

```bash
python scripts/test_pipeline.py
```

Expected output:
```
🧪 Testing 5Tran Pipeline Creation
==================================================

1. Validating configuration...
2. Initializing orchestrator...
3. Creating pipeline...
✅ Pipeline created successfully!
```

### Test the UI

```bash
# Start the Gradio interface
python src/ui/app.py
```

Then open your browser to `http://localhost:7860`

You should see the 5Tran interface with three tabs:
- 🔧 Pipeline Creator
- 💬 SQL Chat
- 📊 Pipeline Status

## Troubleshooting

### "Command 'python' not found"

Try `python3` instead:
```bash
python3 src/ui/app.py
```

### "Module 'google.generativeai' not found"

Install dependencies:
```bash
pip install -e .
```

### "Gemini API key not found"

Ensure your `.env` file exists and contains:
```env
GEMINI_API_KEY=your_actual_key_here
```

### "Port 7860 already in use"

Either:
- Stop the other process using port 7860
- Or modify `src/ui/app.py` to use a different port:
  ```python
  app.launch(server_name="0.0.0.0", server_port=7861)
  ```

### BigQuery Connection Issues

This is expected without GCP credentials. The app will run in mock mode:
```
⚠️ BigQuery client initialization failed
Running in mock mode for development
```

To use real BigQuery, complete the Google Cloud Setup section above.

## Development Mode

By default, 5Tran runs in development mode with:
- ✅ Gemini AI (requires API key)
- 🔧 Mock Fivetran connectors
- 🔧 Mock BigQuery (if no credentials)

This allows you to test the full pipeline creation flow without external dependencies.

## Next Steps

Once everything is set up:

1. **Try the examples**
   - Check `examples/` directory for sample OpenAPI specs
   - Use them to create your first pipeline

2. **Create a pipeline**
   - Go to "Pipeline Creator" tab
   - Describe your requirements
   - Upload an OpenAPI spec (optional)
   - Click "Create Pipeline"

3. **Query your data**
   - Go to "SQL Chat" tab
   - Ask questions in natural language
   - View generated SQL and results

4. **Monitor status**
   - Go to "Pipeline Status" tab
   - Check created connectors and models

## Getting Help

- 📖 See [README.md](README.md) for usage guide
- 📁 Check [examples/README.md](examples/README.md) for OpenAPI examples
- 🐛 Review error messages in terminal output
- 💡 Check dbt logs in `dbt_project/logs/`

## Updating

To update to the latest version:

```bash
git pull
pip install -e . --upgrade
```

---

**Need more help?** Check the main [README.md](README.md) or open an issue.


# 🎬 Getting Started with 5Tran

Welcome to 5Tran AI Pipeline Automation! This guide will get you up and running in minutes.

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] A Google Gemini API key ([Get one here](https://ai.google.dev/))
- [ ] Terminal/command line access

## 🚀 Installation (Choose One)

### Option A: Automated Setup (Recommended) ⚡

```bash
# 1. Navigate to project directory
cd /Users/suman/projects/5tran

# 2. Run automated setup
bash scripts/setup.sh

# 3. Edit .env file with your API key
nano .env  # or use your favorite editor
# Add: GEMINI_API_KEY=your_key_here

# 4. Start the application
bash scripts/run.sh
```

### Option B: Manual Setup 🔧

```bash
# 1. Navigate to project
cd /Users/suman/projects/5tran

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e .

# 4. Configure environment
cp .env.example .env
nano .env  # Add your GEMINI_API_KEY

# 5. Run the app
python src/ui/app.py
```

## 🎯 First Time Setup

### Step 1: Get Your Gemini API Key

1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Sign in with Google
4. Copy your API key

### Step 2: Configure Environment

Edit `.env` file:
```env
# Required
GEMINI_API_KEY=paste_your_key_here

# Optional (for development)
DEV_MODE=true
MOCK_FIVETRAN=true
```

### Step 3: Verify Installation

Test that everything works:
```bash
python scripts/test_pipeline.py
```

You should see:
```
✅ Pipeline created successfully!
```

## 🎨 Using the Interface

### Access the UI

After running the app, open your browser to:
```
http://localhost:7860
```

You'll see three tabs:

### 1️⃣ Pipeline Creator

**Purpose:** Create new data pipelines

**How to use:**
1. Describe your requirements in plain English
2. (Optional) Upload an OpenAPI specification
3. Click "Create Pipeline"
4. View generated components

**Example:**
```
Requirements:
I want to sync orders and customers from our e-commerce API.
Calculate monthly revenue and customer lifetime value.

OpenAPI Spec:
[Upload examples/ecommerce_api.json]
```

### 2️⃣ SQL Chat

**Purpose:** Query your data in natural language

**How to use:**
1. Type your question in plain English
2. Click "Generate & Execute"
3. View generated SQL and results

**Example:**
```
What are the top 10 customers by total revenue?
```

### 3️⃣ Pipeline Status

**Purpose:** Monitor your pipelines

**How to use:**
1. Click "Refresh Status"
2. View connectors, models, and tables

## 📚 Try These Examples

### Example 1: E-Commerce Pipeline

**File:** `examples/ecommerce_api.json`

**Requirements:**
```
Create a pipeline for our e-commerce store with orders, 
customers, and products. Calculate revenue metrics and 
identify top customers.
```

**What you'll get:**
- 3 staging models (orders, customers, products)
- 1 mart model with business metrics
- Fivetran connector configuration

### Example 2: SaaS Metrics Pipeline

**File:** `examples/saas_metrics_api.yaml`

**Requirements:**
```
Set up tracking for our SaaS app with users, subscriptions, 
and usage events. Calculate MRR and churn rate.
```

**What you'll get:**
- 3 staging models (users, subscriptions, usage)
- 1 mart model with SaaS metrics
- MRR and churn calculations

## 🎓 Learning Path

### Beginner (First Hour)

1. ✅ Complete installation
2. ✅ Run test script
3. ✅ Open UI and explore tabs
4. ✅ Create pipeline with example spec
5. ✅ Try SQL chat with simple query

### Intermediate (First Day)

1. ⏭️ Create custom requirements
2. ⏭️ Explore generated dbt models
3. ⏭️ Review Fivetran configs
4. ⏭️ Try complex SQL queries
5. ⏭️ Customize generated models

### Advanced (First Week)

1. ⏭️ Create custom OpenAPI specs
2. ⏭️ Set up real BigQuery connection
3. ⏭️ Configure Fivetran integration
4. ⏭️ Deploy dbt models
5. ⏭️ Build production pipelines

## 🔍 What Gets Created

When you create a pipeline, 5Tran generates:

```
configs/fivetran/
└── {source}_connector.json       # Fivetran config

dbt_project/
├── dbt_project.yml               # Project config
├── profiles.yml                  # Connection settings
└── models/
    ├── staging/
    │   ├── stg_{source}_{table}.sql
    │   └── sources.yml
    └── marts/
        ├── mart_{name}.sql
        └── schema.yml
```

## 🐛 Troubleshooting

### "Gemini API key not found"
✅ **Solution:** Edit `.env` and add `GEMINI_API_KEY=your_key`

### "Port 7860 already in use"
✅ **Solution:** Edit `src/ui/app.py` and change the port:
```python
app.launch(server_name="0.0.0.0", server_port=7861)
```

### "BigQuery client initialization failed"
✅ **Solution:** This is normal! The app runs in mock mode for development. To use real BigQuery, add GCP credentials to `.env`

### "Module not found"
✅ **Solution:** Reinstall dependencies:
```bash
pip install -e .
```

## 💡 Pro Tips

1. **Start Simple** - Use provided examples first
2. **Check Console** - Useful debug info is printed there
3. **Review Generated Code** - Learn from dbt models
4. **Use Dev Mode** - No need for all credentials to start
5. **Read the Docs** - Check README.md for details

## 📖 Documentation Guide

| Document | Purpose | When to Read |
|----------|---------|--------------|
| `QUICKSTART.md` | 5-min setup | First time setup |
| `README.md` | Full documentation | Understanding features |
| `SETUP.md` | Detailed setup | Troubleshooting install |
| `GETTING_STARTED.md` | This file | Learning to use |
| `BUILD_SUMMARY.md` | What was built | Understanding system |
| `PROJECT_STRUCTURE.md` | Code organization | Development work |

## 🎯 Success Checklist

After setup, you should be able to:

- [ ] Open UI at http://localhost:7860
- [ ] See three tabs (Pipeline Creator, SQL Chat, Status)
- [ ] Create a pipeline from example spec
- [ ] See generated dbt models in `dbt_project/models/`
- [ ] See Fivetran config in `configs/fivetran/`
- [ ] Generate SQL from natural language
- [ ] View pipeline status

## 🚀 Next Steps

Once you're comfortable:

1. **Explore** - Try different requirements and specs
2. **Customize** - Modify generated dbt models
3. **Extend** - Add your own OpenAPI specifications
4. **Deploy** - Set up real BigQuery and Fivetran
5. **Build** - Create production data pipelines

## 🤝 Need Help?

- 📖 Check `README.md` for detailed documentation
- 🐛 Review error messages in console
- 📁 Look at generated files in `dbt_project/`
- 💻 Run tests: `python scripts/test_pipeline.py`
- 📧 Open an issue on GitHub

## 🎉 You're Ready!

You now have everything you need to start building AI-powered data pipelines!

**Quick Commands:**
```bash
# Start the app
bash scripts/run.sh

# Run tests
python scripts/test_pipeline.py

# Check project structure
ls -R configs/ dbt_project/
```

**Happy Pipeline Building! 🚀**

---

*5Tran AI Pipeline Automation - Making data pipelines as easy as having a conversation*


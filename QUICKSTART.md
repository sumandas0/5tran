# ⚡ Quick Start Guide

Get 5Tran running in 5 minutes!

## 1. Get Your Gemini API Key (1 minute)

1. Visit: https://ai.google.dev/
2. Click "Get API Key"
3. Sign in with Google
4. Copy your API key

## 2. Install (2 minutes)

```bash
# Clone and enter directory
cd /Users/suman/projects/5tran

# Quick setup
bash scripts/setup.sh
```

## 3. Configure (1 minute)

Edit `.env` file and add your API key:

```bash
# Open in your editor
nano .env

# Add this line:
GEMINI_API_KEY=paste_your_key_here

# Save and exit (Ctrl+X, then Y, then Enter)
```

## 4. Run (30 seconds)

```bash
bash scripts/run.sh
```

Open browser to: **http://localhost:7860**

## 5. Create Your First Pipeline (30 seconds)

In the **Pipeline Creator** tab:

1. **Requirements:**
   ```
   I want to sync orders and customers from our e-commerce API.
   Calculate monthly revenue and customer lifetime value.
   ```

2. **OpenAPI Spec:** Upload `examples/ecommerce_api.json`

3. Click **Create Pipeline**

4. Watch 5Tran generate:
   - Fivetran connector config
   - BigQuery tables
   - dbt transformation models
   - Business metrics

## Next: Query Your Data

Go to **SQL Chat** tab and ask:
```
What are the top 10 customers by revenue?
```

See SQL generated and executed automatically!

---

## Common Issues

**"Gemini API key not found"**
→ Make sure you saved the `.env` file with your key

**"Port already in use"**
→ Kill other process on 7860 or change port in `src/ui/app.py`

**"BigQuery not working"**
→ That's OK! App runs in mock mode for development

---

## What's Next?

- 📖 Read full [README.md](README.md)
- 🛠️ See detailed [SETUP.md](SETUP.md)
- 📚 Check [examples/](examples/) for more samples
- 🧪 Run tests: `python scripts/test_pipeline.py`

---

**That's it! You're ready to automate data pipelines with AI! 🚀**


# 🚀 5Tran AI Pipeline Automation

AI-powered data pipeline automation that creates end-to-end data pipelines using Fivetran connectors, dbt transformations, and BigQuery - all from natural language descriptions.

## 🎯 What is 5Tran?

5Tran is a development prototype that uses Google's Gemini AI to automatically generate complete data pipelines. Simply describe your data requirements in natural language, optionally provide an OpenAPI specification, and 5Tran will:

1. **Analyze** your requirements using Gemini AI
2. **Configure** Fivetran connectors for data ingestion
3. **Generate** dbt models for transformations
4. **Create** BigQuery schemas and tables
5. **Enable** natural language SQL queries against your data

## ✨ Features

- 🤖 **AI-Powered**: Uses Google Gemini for intelligent pipeline design
- 📊 **End-to-End**: From source API to warehouse to insights
- 🔧 **Automated**: Generates all configuration and transformation code
- 💬 **Natural Language**: Chat with your data using plain English
- 🎨 **Beautiful UI**: Modern Gradio interface for easy interaction
- 📝 **OpenAPI Support**: Automatically parse API specifications

## 🏗️ Architecture

```
User Requirements (Natural Language)
           ↓
    [Gemini AI Analysis]
           ↓
    ┌──────┴──────┐
    ↓             ↓
[Fivetran]    [BigQuery]
Connectors     Schemas
    ↓             ↓
    └──────┬──────┘
           ↓
    [dbt Models]
  Staging + Marts
           ↓
    [SQL Chat Bot]
  Query with NL
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- **Google Gemini API key** (required)
- **Fivetran API credentials** (required) - Get from [Fivetran Dashboard](https://fivetran.com/dashboard/settings/account)
- Google Cloud Project with BigQuery (for warehouse)
- Fivetran account with destination configured

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd 5tran
```

2. **Install dependencies**
```bash
# Using pip
pip install -e .

# Or using uv (recommended)
uv pip install -e .
```

3. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here
FIVETRAN_API_KEY=your_fivetran_api_key
FIVETRAN_API_SECRET=your_fivetran_api_secret

# For BigQuery warehouse
GCP_PROJECT_ID=your_gcp_project_id
BIGQUERY_DATASET=dev_pipeline_test
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

4. **Run the application**
```bash
python src/ui/app.py
```

The Gradio UI will open at `http://localhost:7860`

## 📖 Usage

### Creating & Deploying a Pipeline (All from UI!)

1. Navigate to the **Pipeline Creator** tab
2. Describe your requirements in natural language:
   ```
   I want to sync data from our e-commerce API including orders, 
   customers, and products. Calculate monthly revenue and customer 
   lifetime value.
   ```
3. (Optional) Upload an OpenAPI specification
4. **Enable Auto-Deploy** (optional but recommended):
   - Check "Auto-deploy to Fivetran"
   - Enter your Fivetran Group ID (get from CLI: `python scripts/list_fivetran_groups.py`)
   - Enter source API credentials (URL + API Key)
5. Click **Create & Deploy Pipeline**
6. 5Tran will generate AND deploy:
   - ✅ Fivetran connector (auto-deployed!)
   - ✅ BigQuery tables
   - ✅ dbt staging models
   - ✅ dbt mart models
   - ✅ Start syncing immediately!

### Querying Your Data

1. Navigate to the **SQL Chat** tab
2. Ask questions in natural language:
   ```
   What are the top 10 customers by total revenue?
   ```
3. Click **Generate & Execute**
4. View the generated SQL and results

### Monitoring Your Pipeline

1. Navigate to the **Pipeline Status** tab
2. Click **Refresh Status** to see:
   - Configured connectors
   - Generated dbt models
   - Created BigQuery tables

## 📁 Project Structure

```
5tran/
├── src/
│   ├── agent/              # Gemini AI integration
│   │   └── gemini_agent.py
│   ├── connectors/         # Fivetran & OpenAPI
│   │   ├── fivetran_manager.py
│   │   └── openapi_parser.py
│   ├── transformations/    # dbt generation
│   │   └── dbt_generator.py
│   ├── warehouse/          # BigQuery management
│   │   └── bigquery_manager.py
│   ├── ui/                 # Gradio interface
│   │   └── app.py
│   ├── config.py           # Configuration
│   └── orchestrator.py     # Main orchestration
├── examples/               # Sample OpenAPI specs
│   ├── ecommerce_api.json
│   └── saas_metrics_api.yaml
├── configs/                # Generated configs
│   └── fivetran/
├── dbt_project/            # Generated dbt models
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   └── dbt_project.yml
├── .env.example            # Environment template
├── pyproject.toml          # Dependencies
└── README.md
```

## 🎓 Examples

### Complete End-to-End Example

Run the full programmatic example:
```bash
python examples/complete_example.py
```

This demonstrates the entire workflow:
- ✅ List Fivetran groups
- ✅ Generate connector SDK code
- ✅ Auto-deploy to Fivetran
- ✅ Create BigQuery tables
- ✅ Generate dbt models
- ✅ Check sync status
- ✅ Natural language queries

### UI Step-by-Step Guide

See **`examples/ui_example.md`** for:
- Complete UI walkthrough with step-by-step instructions
- Expected outputs at each stage
- Troubleshooting common issues
- Example queries and results

### Quick Examples

**Example 1: E-Commerce Pipeline**
```
Requirements: Track orders, customers, products. Calculate revenue metrics.
OpenAPI: examples/ecommerce_api.json
Generated: 3 staging + 1 mart model, auto-deployed
```

**Example 2: SaaS Metrics**
```
Requirements: Track users, subscriptions, usage. Calculate MRR and churn.
OpenAPI: examples/saas_metrics_api.yaml
Generated: 3 staging + 1 mart model, auto-deployed
```

## 🔌 Fivetran Connector SDK Integration

5Tran uses the **real Fivetran Connector SDK** with **one-click deployment from UI**:

- ✅ **Real API Integration**: No mocks - uses actual Fivetran REST API
- ✅ **Auto-Generated Connectors**: Creates production-ready `connector.py` files
- ✅ **One-Click Deploy**: Deploy directly from UI - no CLI needed!
- ✅ **No Manual IAC**: Automatic deployment without infrastructure setup

### Two Ways to Deploy

**Option 1: From UI (Recommended)**
1. Fill in requirements
2. Check "Auto-deploy to Fivetran"
3. Enter Group ID + API credentials
4. Click "Create & Deploy Pipeline"
5. ✅ Done! Connector is live and syncing

**Option 2: Via CLI**
```bash
python scripts/deploy_connector.py \
  --connector-dir configs/fivetran/connectors/your_connector \
  --group-id YOUR_GROUP_ID \
  --api-url https://api.example.com \
  --api-key YOUR_SOURCE_API_KEY
```

## 🔧 Configuration

### Gemini Settings

Adjust AI behavior in `src/config.py`:
```python
GEMINI_MODEL_FAST = "gemini-1.5-flash"  # Fast responses
GEMINI_MODEL_PRO = "gemini-1.5-pro"     # Better reasoning
GEMINI_TEMPERATURE = 0.2                 # Lower = more consistent
```

### BigQuery Settings

Configure warehouse in `.env`:
```env
GCP_PROJECT_ID=your_project
BIGQUERY_DATASET=dev_pipeline_test
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### dbt Settings

Generated dbt projects use:
- **Staging models**: Views in `staging` schema
- **Mart models**: Tables in `marts` schema
- **Authentication**: OAuth (default) or service account

## 📚 How It Works

### 1. Requirement Analysis
Gemini analyzes your natural language requirements to extract:
- Source type (REST API, database, SaaS)
- Entities (tables/resources)
- Business metrics
- Transformation needs

### 2. OpenAPI Parsing
If provided, the OpenAPI parser extracts:
- API endpoints
- Response schemas
- Authentication methods
- Data types

### 3. Connector Configuration
Fivetran configurations are generated with:
- Endpoint mappings
- Authentication setup
- Pagination strategies
- Primary keys

### 4. Schema Generation
BigQuery tables are created with:
- Inferred column types
- Metadata columns (_loaded_at, _source)
- Proper naming conventions

### 5. dbt Model Generation
Transformation models are generated:
- **Staging**: One per source table, basic cleaning
- **Marts**: Business metrics and aggregations
- **Schema**: Full documentation

### 6. SQL Generation
Natural language queries are converted to SQL:
- Context-aware (knows your schema)
- BigQuery-optimized syntax
- Executable and debuggable

## 🐛 Troubleshooting

### "Gemini API key not found"
- Check that `GEMINI_API_KEY` is set in `.env`
- Get a key at https://ai.google.dev/

### "BigQuery client initialization failed"
- This is expected without GCP credentials
- App runs in mock mode automatically
- To use real BigQuery, set up service account key

### "Failed to parse OpenAPI spec"
- Ensure spec is valid JSON or YAML
- Use OpenAPI 3.0 format
- Check for syntax errors

### Models not compiling
- Check dbt_project.yml configuration
- Verify BigQuery credentials
- Run `dbt compile` in dbt_project/ for details

## 🎯 Recent Updates

- ✅ **One-Click Deployment from UI** - Deploy connectors without leaving the UI!
- ✅ **Real Fivetran SDK Integration** - Production-ready, no mocks
- ✅ **Auto-Generated Connector Code** - SDK-compliant `connector.py` files
- ✅ **REST API Integration** - Real-time connector status and management
- ✅ **No CLI Required** - Everything can be done from the web interface

## 🎯 Roadmap

- [ ] Support for more source types (databases, webhooks)
- [ ] OAuth2 authentication flow
- [ ] Data quality tests
- [ ] Multi-environment support (dev/staging/prod)
- [ ] Advanced transformations (ML features)

## 🤝 Contributing

This is a development prototype. Contributions welcome!

Areas for improvement:
- Additional source connectors
- More sophisticated dbt models
- Better error handling
- Production deployment guide
- Test coverage

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [Google Gemini](https://ai.google.dev/) - AI capabilities
- [Fivetran](https://fivetran.com/) - Data connectors
- [dbt](https://www.getdbt.com/) - Transformations
- [BigQuery](https://cloud.google.com/bigquery) - Data warehouse
- [Gradio](https://gradio.app/) - UI framework

## 📞 Support

For issues and questions:
- Check the [examples/](examples/) directory
- Review [configs/](configs/) for generated files
- Check dbt compilation errors in `dbt_project/target/`

---

**5Tran** - Making data pipelines as easy as having a conversation 🚀


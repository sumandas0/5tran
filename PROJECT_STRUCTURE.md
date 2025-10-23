# 📁 Project Structure

Complete overview of the 5Tran project structure.

```
5tran/
│
├── 📄 README.md              # Main documentation
├── 📄 QUICKSTART.md          # 5-minute setup guide  
├── 📄 SETUP.md               # Detailed setup instructions
├── 📄 PROJECT_STRUCTURE.md   # This file
│
├── 📄 main.py                # Entry point
├── 📄 pyproject.toml         # Python dependencies
├── 📄 .env.example           # Environment template
├── 📄 .gitignore             # Git ignore rules
│
├── 📂 src/                   # Main source code
│   ├── 📄 __init__.py
│   ├── 📄 config.py          # Configuration management
│   ├── 📄 orchestrator.py    # Main pipeline orchestration
│   │
│   ├── 📂 agent/             # Gemini AI integration
│   │   ├── 📄 __init__.py
│   │   └── 📄 gemini_agent.py
│   │
│   ├── 📂 connectors/        # Data source connectors
│   │   ├── 📄 __init__.py
│   │   ├── 📄 fivetran_manager.py
│   │   └── 📄 openapi_parser.py
│   │
│   ├── 📂 transformations/   # dbt model generation
│   │   ├── 📄 __init__.py
│   │   └── 📄 dbt_generator.py
│   │
│   ├── 📂 warehouse/         # BigQuery management
│   │   ├── 📄 __init__.py
│   │   └── 📄 bigquery_manager.py
│   │
│   └── 📂 ui/                # Gradio interface
│       ├── 📄 __init__.py
│       └── 📄 app.py         # Main UI application
│
├── 📂 examples/              # Example OpenAPI specs
│   ├── 📄 README.md
│   ├── 📄 ecommerce_api.json
│   └── 📄 saas_metrics_api.yaml
│
├── 📂 scripts/               # Utility scripts
│   ├── 📄 setup.sh           # Automated setup
│   ├── 📄 run.sh             # Quick run script
│   └── 📄 test_pipeline.py   # Test suite
│
├── 📂 configs/               # Generated configurations
│   ├── 📄 README.md
│   └── 📂 fivetran/          # Fivetran connector configs
│       └── [generated].json
│
└── 📂 dbt_project/           # Generated dbt project
    ├── 📄 dbt_project.yml    # dbt configuration
    ├── 📄 profiles.yml       # BigQuery connection
    │
    ├── 📂 models/            # dbt models
    │   ├── 📂 staging/       # Staging models
    │   │   ├── [generated].sql
    │   │   └── sources.yml
    │   │
    │   └── 📂 marts/         # Business metrics
    │       ├── [generated].sql
    │       └── schema.yml
    │
    ├── 📂 macros/            # dbt macros
    ├── 📂 tests/             # dbt tests
    └── 📂 target/            # dbt compilation output
```

## Core Modules

### 🤖 Agent (`src/agent/`)
Handles AI interactions with Google Gemini:
- Requirement analysis
- SQL generation from natural language
- Schema extraction from OpenAPI specs
- dbt model suggestions

### 🔌 Connectors (`src/connectors/`)
Manages data source configurations:
- OpenAPI specification parsing
- Fivetran connector generation
- Authentication setup
- Endpoint mapping

### 🔄 Transformations (`src/transformations/`)
Generates dbt models:
- Staging models (one per source table)
- Mart models (business metrics)
- Schema documentation
- Source definitions

### 💾 Warehouse (`src/warehouse/`)
BigQuery schema management:
- Dataset creation
- Table schema generation
- Query execution
- Schema introspection

### 🎨 UI (`src/ui/`)
Gradio web interface:
- Pipeline creator
- SQL chat
- Status monitoring

### 🎯 Orchestrator (`src/orchestrator.py`)
Coordinates the entire pipeline:
- Requirement analysis
- Component initialization
- Pipeline creation flow
- Status tracking

## Generated Files

### During Pipeline Creation:

```
configs/fivetran/
└── {source_name}_connector.json    # Fivetran config

dbt_project/
├── dbt_project.yml                 # Project config
├── profiles.yml                    # Connection details
└── models/
    ├── staging/
    │   ├── stg_{source}_{table}.sql
    │   └── sources.yml
    └── marts/
        ├── mart_{name}.sql
        └── schema.yml
```

## File Responsibilities

| File | Purpose | When Created |
|------|---------|--------------|
| `.env` | Environment variables | Manual (from .env.example) |
| `configs/fivetran/*.json` | Connector configs | Pipeline creation |
| `dbt_project/dbt_project.yml` | dbt configuration | Pipeline creation |
| `dbt_project/models/staging/*.sql` | Staging models | Pipeline creation |
| `dbt_project/models/marts/*.sql` | Mart models | Pipeline creation |

## Development Workflow

```
1. User describes requirements
   ↓
2. src/ui/app.py receives input
   ↓
3. src/orchestrator.py coordinates
   ↓
4. src/agent/gemini_agent.py analyzes
   ↓
5. src/connectors/openapi_parser.py parses spec
   ↓
6. src/connectors/fivetran_manager.py creates config
   ↓
7. src/warehouse/bigquery_manager.py creates tables
   ↓
8. src/transformations/dbt_generator.py creates models
   ↓
9. Results displayed in UI
```

## Key Dependencies

| Package | Purpose | Used By |
|---------|---------|---------|
| `google-generativeai` | Gemini AI | agent/ |
| `gradio` | Web UI | ui/ |
| `fivetran` | Connector SDK | connectors/ |
| `dbt-core` | Transformations | transformations/ |
| `dbt-bigquery` | BigQuery adapter | transformations/ |
| `google-cloud-bigquery` | Warehouse | warehouse/ |
| `pyyaml` | Config parsing | connectors/ |
| `python-dotenv` | Environment | config.py |

## Configuration Flow

```
.env.example  →  .env  →  src/config.py  →  All modules
                                ↓
                         Environment variables
                         API keys
                         Project settings
```

## Execution Paths

### Running the UI:
```
python src/ui/app.py
  → Imports orchestrator
  → Initializes all components
  → Launches Gradio interface
```

### Running Tests:
```
python scripts/test_pipeline.py
  → Creates orchestrator
  → Runs pipeline creation
  → Validates outputs
```

### Quick Start:
```
bash scripts/setup.sh
  → Creates venv
  → Installs dependencies
  → Sets up .env

bash scripts/run.sh
  → Activates venv
  → Runs src/ui/app.py
```

## Extension Points

Want to extend 5Tran? Here's where to add features:

| Feature | Location | Notes |
|---------|----------|-------|
| New AI models | `src/agent/gemini_agent.py` | Add model selection |
| New connectors | `src/connectors/` | Create new manager class |
| Custom transformations | `src/transformations/` | Extend dbt_generator |
| New data warehouses | `src/warehouse/` | Create new manager |
| UI customization | `src/ui/app.py` | Modify Gradio blocks |

## Testing Structure

```
scripts/test_pipeline.py     # Integration tests
  → Test basic pipeline
  → Test with OpenAPI
  → Verify outputs
```

---

For more details on specific modules, see inline code documentation.


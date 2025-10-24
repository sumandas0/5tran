# 5tran Connector Generator

This project uses a multi-agent system built with Google's Agent Development Kit (ADK) to automate the creation of Fivetran connectors.

> **Note**: This project uses Firecrawl's `scrape` API endpoint for faster performance compared to the `extract` endpoint.

## How it works

1.  **Input**: You provide a project name, website URL, and a prompt describing the data you want to extract.
2.  **Data Extraction**: The Schema Generator agent uses Firecrawl's `scrape` endpoint to extract sample data from the website based on your prompt.
3.  **Dual Schema Generation**: The agent analyzes the scraped data and creates TWO schemas:
    - **Firecrawl Schema**: A JSON schema for data extraction via the Firecrawl API
    - **Fivetran SDK Schema**: A table definition for the Fivetran connector's `schema()` function
4.  **Template-Based Generation**: A parameterized connector template is populated with your URL, prompt, and both schemas to create the final connector code.
5.  **Project Creation**: A complete project folder is created with connector.py, configuration.json, and README.md.
6.  **Automatic Deployment**: The connector is automatically deployed to Fivetran using the Fivetran CLI.
7.  **Output**: A production-ready Fivetran connector deployed and ready to sync data.

## Project Structure

```
.
├── app.py                  # Gradio web interface (recommended)
├── main.py                 # Command-line interface
├── src
│   ├── agents
│   │   ├── agents.py              # Schema Generator agent definition
│   │   ├── config.py              # Agent configuration (model name)
│   │   ├── connector_template.py  # Parameterized connector template
│   │   └── tools
│   │       └── firecrawl_tool.py  # Firecrawl extract tool
│   └── connectors          # Generated connector projects
│       └── <project_name>
│           ├── connector.py         # Generated Fivetran connector
│           ├── configuration.json   # API keys and URL (git-ignored)
│           ├── requirements.txt     # Python dependencies
│           └── README.md           # Project documentation
├── pyproject.toml
├── .env                    # Environment variables (FIRECRAWL_API_KEY)
└── README.md
```

## Setup

### Local Development

1.  **Install dependencies**:
    ```bash
    uv pip install .
    ```

2.  **Install Fivetran CLI** (required for automatic deployment):
    ```bash
    pip install fivetran-cli
    ```
    Or follow the [official Fivetran CLI installation guide](https://github.com/fivetran/fivetran-cli).

3.  **Set up your environment variables**:
    Create a `.env` file in the root of the project and add your Firecrawl API key:
    ```
    FIRECRAWL_API_KEY="fc-YOUR-API-KEY"
    FIVETRAN_API_SECRET_BASE64="your-base64-key"
    GEMINI_API_KEY="your-gemini-key"
    ```
    The application will load these keys.

### Cloud Deployment (Google Cloud Run)

The application is containerized and ready for deployment to Google Cloud Run. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

**Quick Deploy:**
```bash
export PROJECT_ID="your-gcp-project-id"
export FIVETRAN_API_SECRET_BASE64="your_base64_key"
export FIRECRAWL_API_KEY="your_firecrawl_key"
export GEMINI_API_KEY="your_gemini_key"

./deploy.sh
```

**Required Environment Variables:**
- `FIVETRAN_API_SECRET_BASE64` - Base64-encoded Fivetran API credentials
- `FIRECRAWL_API_KEY` - Firecrawl API key for web scraping
- `GEMINI_API_KEY` - Google Gemini API key for AI generation

## Usage

### Option 1: Web Interface (Recommended)

Launch the professional Gradio web interface:

```bash
python app.py
```

The interface will be available at `http://localhost:7860` and provides:

- **Intuitive UI**: Clean, professional interface with real-time progress indicators
- **All-in-one Configuration**: Enter all required parameters in one place
- **Visual Feedback**: Live status updates and generation progress
- **Automatic Cleanup**: Removes old connectors before generating new ones
- **Automatic Deployment**: Deploys connectors directly to Fivetran
- **Secure Input**: Password-masked fields for API credentials

**Required Inputs:**
1. Destination Name - Your Fivetran destination identifier
2. Project Name - Name for your connector (auto-sanitized)
3. Target URL - Website to extract data from
4. Extraction Prompt - Description of data to extract
5. Fivetran API Key - Your Fivetran API credentials
6. Fivetran API Secret - Your Fivetran API secret
7. Firecrawl API Key - API key for web scraping

**Features:**
- 🔄 Real-time progress tracking with status updates
- 🗑️ Automatic deletion of old connectors before generation
- 🚀 Automatic deployment to Fivetran with CLI integration
- 🔒 Secure password-masked input fields for API keys
- 📊 Live generation logs with emoji indicators
- ✅ Success confirmation with deployment status
- 📁 Direct path to generated connector folder
- 🎨 Modern, responsive UI with professional styling
- ⚠️ Fallback instructions if deployment fails

### Option 2: Command Line

Run the connector generator with a project name, URL, and prompt:
```bash
python main.py <project_name> <url> <prompt>
```

### Examples

**Example 1: Google News Connector**
```bash
python main.py "google_news" "https://news.google.com" "Extract top news articles with title, URL, and summary"
```

**Example 2: Shopify Products with Wildcard**
```bash
python main.py "shopify_products" "https://shop.example.com/products/*" "Extract all product information including name, price, and description"
```

**Example 3: With Custom API Key**
```bash
python main.py "my_connector" "https://example.com" "Extract data" --api-key "fc-YOUR-API-KEY"
```

### What Gets Generated

For a project named `google_news`, the following structure is created:

```
src/connectors/google_news/
├── connector.py           # The Fivetran connector code
├── configuration.json     # Configuration with API keys and URL
├── requirements.txt       # Python dependencies
└── README.md             # Project-specific documentation
```

**Files:**
- **`connector.py`**: Complete Fivetran connector with schema(), update(), error handling, and debug mode
- **`configuration.json`**: Contains `firecrawl_api_key` and `url` for the connector
- **`requirements.txt`**: Python dependencies (firecrawl-py==1.5.0, fivetran-connector-sdk, python-dotenv)
- **`README.md`**: Instructions for testing and deploying the specific connector

**Note:** `configuration.json` files are automatically excluded from git to protect your API keys.

**Example `configuration.json`:**
```json
{
  "firecrawl_api_key": "fc-YOUR-API-KEY",
  "url": "https://news.google.com"
}
```

### Testing and Deployment

**Web Interface (Automatic):**
When using the web interface (`app.py`), connectors are automatically deployed to Fivetran after generation. No manual deployment needed!

**Command Line (Manual Deployment):**
If using the CLI (`main.py`) or need to manually redeploy:

**Install Dependencies:**
```bash
cd src/connectors/google_news
pip install -r requirements.txt
```

**Test Locally:**
```bash
python connector.py
```

**Deploy to Fivetran:**
```bash
export FIVETRAN_API_KEY="your_api_key"
export FIVETRAN_API_SECRET="your_api_secret"
fivetran deploy . --destination "your_destination_name"
```

### Scrape Endpoint Features

The Firecrawl `scrape` endpoint provides powerful capabilities:
- **Fast Performance**: Significantly faster than the extract endpoint for most use cases
- **Single Page Scraping**: Extract structured data from a single URL
- **Schema-based Extraction**: Define a JSON schema for structured data extraction
- **Prompt-based Extraction**: Use natural language prompts to describe the data you want
- **Flexible Timeout**: Configurable timeout up to 120 seconds for complex pages
- **Main Content Focus**: Option to extract only main content or full page

Example scrape call:
```python
result = app.scrape(
    'https://example.com',
    formats=[{
        "type": "json",
        "schema": schema_dict,
        "prompt": "Extract product information"
    }],
    only_main_content=False,
    timeout=120000
)
```

## Dual Schema Architecture

The system generates two complementary schemas:

### 1. Firecrawl Schema (JSON Schema)
Used by the Firecrawl `extract` API to extract structured data from web pages.

Example:
```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string", "description": "Article title"},
    "author": {"type": "string", "description": "Article author"},
    "published_date": {"type": "string", "description": "Publication date"}
  },
  "required": ["title", "published_date"]
}
```

### 2. Fivetran SDK Schema
Defines the database table structure for the Fivetran connector.

Example:
```json
[
  {
    "table": "articles",
    "primary_key": ["url"],
    "columns": {
      "url": "STRING",
      "title": "STRING",
      "author": "STRING",
      "published_date": "STRING"
    }
  }
]
```

This dual schema approach eliminates the need for manual conversion between formats and ensures consistency between data extraction and storage.

## Template-Based Architecture

The system uses a simple, efficient template-based approach:

### Generation Flow

```
┌─────────────────────────────────────────────────┐
│ 1. User Input                                   │
│    - Project name                               │
│    - URL to extract from                        │
│    - Extraction prompt                          │
│    - Fivetran API credentials                   │
│    - Destination name                           │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 2. Schema Generator Agent                       │
│    - Uses Firecrawl extract to get sample data │
│    - Analyzes data structure                    │
│    - Generates Firecrawl JSON schema            │
│    - Generates Fivetran SDK schema              │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 3. Template Population                          │
│    - Loads connector_template.py                │
│    - Replaces {url_to_extract}                  │
│    - Replaces {extraction_prompt}               │
│    - Replaces {firecrawl_schema}                │
│    - Replaces {fivetran_schema}                 │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 4. Project Creation                             │
│    - Creates project folder                     │
│    - Saves connector.py                         │
│    - Generates configuration.json               │
│    - Creates README.md                          │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 5. Automatic Deployment (Web Interface)         │
│    - Calls Fivetran CLI                         │
│    - Deploys to specified destination           │
│    - Reports deployment status                  │
└─────────────────────────────────────────────────┘
```

### Key Benefits

- **Fast**: No iterative LLM refinement loops
- **Reliable**: Template ensures consistent, working code every time
- **Predictable**: Same structure for all connectors
- **Maintainable**: Single template file to update for improvements
- **Cost-effective**: Only one LLM call for schema generation

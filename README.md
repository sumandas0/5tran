# 5tran Connector Generator

This project uses a multi-agent system built with Google's Agent Development Kit (ADK) to automate the creation of Fivetran connectors.

## How it works

1.  **Input**: You provide a project name, website URL, and a prompt describing the data you want to extract.
2.  **Data Extraction**: The Schema Generator agent uses Firecrawl's `extract` endpoint to extract sample data from the website based on your prompt.
3.  **Dual Schema Generation**: The agent analyzes the extracted data and creates TWO schemas:
    - **Firecrawl Schema**: A JSON schema for data extraction via the Firecrawl API
    - **Fivetran SDK Schema**: A table definition for the Fivetran connector's `schema()` function
4.  **Template-Based Generation**: A parameterized connector template is populated with your URL, prompt, and both schemas to create the final connector code.
5.  **Project Creation**: A complete project folder is created with connector.py, configuration.json, and README.md.
6.  **Output**: A production-ready Fivetran connector ready for testing and deployment.

## Project Structure

```
.
├── main.py                 # Main entry point
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

1.  **Install dependencies**:
    ```bash
    uv pip install .
    ```

2.  **Set up your environment variables**:
    Create a `.env` file in the root of the project and add your Firecrawl API key:
    ```
    FIRECRAWL_API_KEY="fc-YOUR-API-KEY"
    ```
    The application will load this key.

## Usage

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
fivetran deploy .
```

### Extract Endpoint Features

The Firecrawl `extract` endpoint provides powerful capabilities:
- **Single Page Extraction**: Extract structured data from a single URL
- **Multiple Pages**: Provide multiple URLs separated by commas
- **Wildcard Support**: Use `/*` to automatically crawl and extract from all discoverable URLs in a domain
- **Schema-based Extraction**: Define a JSON schema for structured data extraction
- **Prompt-based Extraction**: Use natural language prompts to describe the data you want

Example with multiple URLs:
```python
urls = ["https://example.com/page1", "https://example.com/page2"]
```

Example with wildcard for full domain:
```python
urls = ["https://example.com/*"]
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
└─────────────────────────────────────────────────┘
```

### Key Benefits

- **Fast**: No iterative LLM refinement loops
- **Reliable**: Template ensures consistent, working code every time
- **Predictable**: Same structure for all connectors
- **Maintainable**: Single template file to update for improvements
- **Cost-effective**: Only one LLM call for schema generation

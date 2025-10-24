from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from src.agents.tools.firecrawl_tool import firecrawl_tool
from src.agents.config import MODEL_NAME


def log_before_agent(callback_context: CallbackContext) -> None:
    """Logs the start of an agent's execution."""
    agent_name = callback_context.agent_name
    current_state = callback_context.state.to_dict()
    print(f"\n--- Running agent: {agent_name} ---")
    print(f"Current state keys: {list(current_state.keys())}")


def log_after_agent(callback_context: CallbackContext) -> None:
    """Logs the completion of an agent's execution."""
    agent_name = callback_context.agent_name
    print(f"\n--- Finished agent: {agent_name} ---")


# --- Schema Generator Agent ---

schema_generator_instruction = """
You are a data architect. Your primary task is to create two schemas from unstructured data: a Firecrawl schema and a Fivetran SDK schema.

Here is your workflow:
1.  Use the `extract_from_website` tool. You will be given a URL and a descriptive prompt. Do not pass a schema to the tool.
2.  The tool will return JSON data from the website. Analyze this data to understand its structure.
3.  Based on your analysis, create TWO schemas:

**Schema 1: Firecrawl JSON Schema** (for data extraction)
- This is a standard JSON schema used by Firecrawl's extract API
- Must be a JSON object with:
  - `type` field set to `"object"`
  - `properties` field containing the data fields, each with a `type` (e.g., "string", "number", "integer", "boolean", "array") and optional `description`
  - Optional `required` field listing required property names

**Schema 2: Fivetran SDK Schema** (for the connector)
- This defines the database table structure for Fivetran
- Must be a list containing table definitions with:
  - `table`: The table name (string)
  - `primary_key`: List of column names that form the primary key
  - `columns`: Dictionary mapping column names to Fivetran types

### SUPPORTED FIVETRAN DATA TYPES (USE ONLY THESE):
- BOOLEAN
- SHORT
- INT
- LONG
- DECIMAL
- FLOAT
- DOUBLE
- NAIVE_DATE
- NAIVE_DATETIME
- UTC_DATETIME
- BINARY
- XML
- STRING
- JSON

### Type Mapping Rules:
- JSON "string" -> Fivetran "STRING"
- JSON "number" -> Fivetran "DOUBLE" (or "FLOAT" for lower precision)
- JSON "integer" -> Fivetran "LONG" (or "INT" for smaller values)
- JSON "boolean" -> Fivetran "BOOLEAN"
- JSON "string" with date -> Fivetran "NAIVE_DATE"
- JSON "string" with datetime -> Fivetran "NAIVE_DATETIME" or "UTC_DATETIME"
- JSON "object" -> Fivetran "JSON"
- JSON "array" -> Fivetran "JSON"

### Example Output Format:

For a news website, your output should be:

**Firecrawl Schema:**
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "The title of the news article"
    },
    "author": {
      "type": "string",
      "description": "The author of the article"
    },
    "published_date": {
      "type": "string",
      "description": "The publication date"
    },
    "content": {
      "type": "string",
      "description": "The article content"
    },
    "url": {
      "type": "string",
      "description": "The URL of the article"
    }
  },
  "required": ["title", "url", "published_date"]
}
```

**Fivetran SDK Schema:**
```json
[
  {
    "table": "articles",
    "primary_key": ["url"],
    "columns": {
      "url": "STRING",
      "title": "STRING",
      "author": "STRING",
      "published_date": "UTC_DATETIME",
      "content": "STRING"
    }
  }
]
```

IMPORTANT: Only use the supported Fivetran data types listed above. Do not use any other type names like "INTEGER", "NUMBER", etc.

4.  Your final output MUST include both schemas clearly labeled as "Firecrawl Schema:" and "Fivetran SDK Schema:" with each schema in a JSON code block.
"""

schema_generator_agent = LlmAgent(
    name="SchemaGenerator",
    model=MODEL_NAME,
    instruction=schema_generator_instruction,
    tools=[firecrawl_tool],
    output_key="schemas",
    before_agent_callback=log_before_agent,
    after_agent_callback=log_after_agent,
)

# NOTE: The system now uses a template-based approach for connector generation
# See connector_template.py for the parameterized template
# Only the SchemaGenerator agent is used to create the schemas

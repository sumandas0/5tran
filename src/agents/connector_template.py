import traceback
import json
import os
from firecrawl import Firecrawl
from firecrawl.v2.types import AgentOptions
from fivetran_connector_sdk import Connector
from fivetran_connector_sdk import Logging as log
from fivetran_connector_sdk import Operations as op

# Configuration parameters (template placeholders - will be replaced during generation)
URL_TO_EXTRACT = "{url_to_extract}"  # noqa: F821
EXTRACTION_PROMPT = "{extraction_prompt}"  # noqa: F821

# These placeholders are replaced with actual schemas during generation
FIRECRAWL_EXTRACT_SCHEMA = {firecrawl_schema}  # noqa: F821

FIVETRAN_SCHEMA = {fivetran_schema}  # noqa: F821


def schema(configuration: dict):
    """Define the schema for the Fivetran connector."""
    return FIVETRAN_SCHEMA


def update(configuration: dict, state: dict):
    """Fetch data from the source and load it into the destination."""
    try:
        # Step 1: Validate and retrieve API key
        firecrawl_api_key = configuration.get("firecrawl_api_key") or os.getenv("FIRECRAWL_API_KEY")
        if not firecrawl_api_key:
            log.severe("firecrawl_api_key not found in configuration or environment variables")
            raise ValueError("firecrawl_api_key not found in configuration or environment variables.")
        
        # Step 2: Validate and retrieve URL
        url = configuration.get("url", URL_TO_EXTRACT)
        if not url:
            log.severe("url not found in configuration")
            raise ValueError("url not found in configuration.")
        
        # Log sync start
        log.warning(f"Starting data sync for URL: {url}")
        
        # Step 3: Initialize Firecrawl client
        try:
            app = Firecrawl(api_key=firecrawl_api_key)
            log.warning("Firecrawl client initialized successfully")
        except Exception as init_error:
            log.severe(f"Failed to initialize Firecrawl client: {str(init_error)}")
            raise
        
        # Step 4: Extract data using Firecrawl
        log.warning(f"Calling Firecrawl extract API with prompt: {EXTRACTION_PROMPT[:100]}...")
        try:
            result = app.extract(
                urls=[url],
                prompt=EXTRACTION_PROMPT,
                schema=FIRECRAWL_EXTRACT_SCHEMA,
                ignore_invalid_urls=True,
                agent=AgentOptions(
                    model="FIRE-1"
                )
            )
            log.warning("Firecrawl extract API call completed")
        except Exception as extract_error:
            log.severe(f"Firecrawl extraction failed: {str(extract_error)}")
            raise

        # Step 5: Process and validate extracted data
        if result and hasattr(result, 'data'):
            data = result.data
            
            if not data:
                log.warning("Firecrawl returned empty data")
                op.checkpoint(state)
                return
            
            # Log data details
            data_str = json.dumps(data)
            log.warning(f"Successfully extracted data: {len(data_str)} characters")
            log.warning(f"Data preview: {data_str[:200]}...")
            
            # Step 6: Get table name and validate
            table_name = FIVETRAN_SCHEMA[0]["table"]
            log.warning(f"Upserting data into table: {table_name}")
            
            # Step 7: Upsert data
            try:
                op.upsert(table=table_name, data=data)
                log.warning(f"Successfully upserted data into table '{table_name}'")
            except Exception as upsert_error:
                log.severe(f"Failed to upsert data: {str(upsert_error)}")
                raise
        else:
            log.warning("No data extracted from source - result is empty or malformed")
            if result:
                log.warning(f"Result object: {str(result)[:200]}")

        # Step 8: Checkpoint state
        log.warning("Saving checkpoint state")
        op.checkpoint(state)
        log.warning("Sync completed successfully")

    except ValueError as ve:
        # Configuration or validation errors
        error_msg = f"Configuration error: {str(ve)}"
        log.severe(error_msg)
        raise RuntimeError(error_msg)
    
    except Exception as e:
        # Unexpected errors with full stack trace
        exception_message = str(e)
        stack_trace = traceback.format_exc()
        
        log.severe(f"Unexpected error during sync: {exception_message}")
        log.severe("Full stack trace:")
        
        # Log stack trace in chunks to avoid truncation
        for line in stack_trace.split("\\n"):
            if line.strip():
                log.severe(line)
        
        detailed_message = f"Error: {exception_message}\\nStack Trace:\\n{stack_trace}"
        raise RuntimeError(detailed_message)


connector = Connector(update=update, schema=schema)


if __name__ == "__main__":
    with open("configuration.json", "r") as f:
        configuration = json.load(f)
    connector.debug(configuration=configuration)


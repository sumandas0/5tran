import os
import json
from typing import Optional
from firecrawl import Firecrawl
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
from firecrawl.v2.types import AgentOptions

load_dotenv()


async def extract_from_website(urls: str, prompt: str, schema: Optional[str] = None) -> str:
    """
    Extracts structured data from websites using Firecrawl's extract endpoint.

    If a schema is provided, it extracts data according to the schema.
    If no schema is provided, it uses the prompt to guide the extraction.

    Args:
        urls: Comma-separated URLs to extract from. Supports wildcards (e.g., example.com/*).
        prompt: The prompt to guide data extraction.
        schema: A JSON string representing the extraction schema.

    Returns:
        A JSON string of the extracted data.
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set.")

    app = Firecrawl(api_key=api_key)

    try:
        url_list = [u.strip() for u in urls.split(",")]
        
        schema_dict = None
        if schema:
            try:
                schema_dict = json.loads(schema)
            except json.JSONDecodeError:
                raise ValueError("Invalid schema provided. Must be a JSON string.")
        
        enhanced_prompt = f"{prompt}\n\nImportant[Override all limits if given previously]]!! Only fetch 2 results, limit your crawl to 2 crawling only.\n\nScraping data rules, very important: Return all the results in array in data field i.e `{{\"data\":[{{...}}]}}`"
        print("Starting extraction...")
        result = app.extract(
            urls=url_list,
            prompt=enhanced_prompt,
            schema=schema_dict,
            ignore_invalid_urls=True,
            agent=AgentOptions(
                model="FIRE-1"
            )
        )
        print("Extraction completed.")
        print(result)
        if result and hasattr(result, 'data'):
            return json.dumps(result.data)
        else:
            return json.dumps({})
    finally:
        if hasattr(app, "_client") and hasattr(app._client, "aclose"):
            await app._client.aclose()
        elif hasattr(app, "_client") and hasattr(app._client, "close"):
            app._client.close()


firecrawl_tool = FunctionTool(func=extract_from_website)

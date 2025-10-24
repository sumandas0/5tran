import os
import json
from typing import Optional
from firecrawl import Firecrawl
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

load_dotenv()


async def extract_from_website(urls: str, prompt: str, schema: Optional[str] = None) -> str:
    """
    Extracts structured data from websites using Firecrawl's scrape endpoint.

    If a schema is provided, it extracts data according to the schema.
    If no schema is provided, it uses the prompt to guide the extraction.

    Args:
        urls: Comma-separated URLs to scrape from.
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
        
        enhanced_prompt = f"{prompt}\n\nImportant: Only fetch 2 results for testing.\n\nCritical: Always return results as an array/list. Even for a single item, wrap it in an array. If no data found, return empty array []. Return in format `{{\"data\":[{{...}}]}}`"
        
        print("Starting scrape...")
        
        formats_config = {
            "type": "json"
        }
        
        if schema_dict:
            formats_config["schema"] = schema_dict
        
        formats_config["prompt"] = enhanced_prompt
        
        url = url_list[0]
        
        result = app.scrape(
            url,
            formats=[formats_config],
            only_main_content=False,
            timeout=120000,
            block_ads=True,
            wait_for=10000,
            proxy="auto",
            remove_base64_images=True
        )
        data = result.json
        
        print(f"Data: {str(data)}")
        return json.dumps(data)
    finally:
        if hasattr(app, "_client") and hasattr(app._client, "aclose"):
            await app._client.aclose()
        elif hasattr(app, "_client") and hasattr(app._client, "close"):
            app._client.close()


firecrawl_tool = FunctionTool(func=extract_from_website)

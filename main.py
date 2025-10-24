import asyncio
import argparse
import os
import json
from urllib.parse import urlparse
from dotenv import load_dotenv

from google.adk.runners import InMemoryRunner
from google.genai import types
from src.agents.agents import schema_generator_agent

load_dotenv()


def generate_connector_from_template(url: str, prompt: str, firecrawl_schema: dict, fivetran_schema: list) -> str:
    """Generate connector code from template with provided parameters."""
    template_path = "src/agents/connector_template.py"
    
    with open(template_path, "r") as f:
        template_code = f.read()
    
    connector_code = template_code.replace("{url_to_extract}", url)
    connector_code = connector_code.replace("{extraction_prompt}", prompt)
    connector_code = connector_code.replace("{firecrawl_schema}", json.dumps(firecrawl_schema, indent=4))
    connector_code = connector_code.replace("{fivetran_schema}", json.dumps(fivetran_schema, indent=4))
    
    return connector_code

def create_connector_project(code: str, url: str, project_name: str, api_key: str = None):
    """Creates a connector project folder with connector.py and configuration.json."""
    safe_project_name = "".join(c if c.isalnum() or c in ["_", "-"] else "_" for c in project_name)
    project_dir = f"src/connectors/{safe_project_name}"
    
    os.makedirs(project_dir, exist_ok=True)
    
    connector_file = os.path.join(project_dir, "connector.py")
    with open(connector_file, "w") as f:
        f.write(code)
    print(f"✓ Connector code saved to {connector_file}")
    
    firecrawl_api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
    if not firecrawl_api_key:
        print("⚠ Warning: FIRECRAWL_API_KEY not provided and not found in environment")
        firecrawl_api_key = "YOUR_FIRECRAWL_API_KEY_HERE"
    
    config = {
        "firecrawl_api_key": firecrawl_api_key,
        "url": url
    }
    
    config_file = os.path.join(project_dir, "configuration.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✓ Configuration saved to {config_file}")
    
    readme_content = f"""# {project_name} Connector

This Fivetran connector extracts data from: {url}

## Files

- `connector.py`: The main connector implementation
- `configuration.json`: Configuration with API keys and URL
- `requirements.txt`: Python dependencies

## Setup

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Testing Locally

```bash
python connector.py
```

## Deploying to Fivetran

```bash
fivetran deploy {project_dir}
```

Make sure you have the Fivetran CLI installed and configured.
"""
    
    readme_file = os.path.join(project_dir, "README.md")
    with open(readme_file, "w") as f:
        f.write(readme_content)
    print(f"✓ README saved to {readme_file}")
    
    requirements_content = """firecrawl-py==4.5.0
"""
    
    requirements_file = os.path.join(project_dir, "requirements.txt")
    with open(requirements_file, "w") as f:
        f.write(requirements_content)
    print(f"✓ Requirements saved to {requirements_file}")
    
    print(f"\n{'='*60}")
    print(f"✓ Project '{safe_project_name}' created successfully!")
    print(f"{'='*60}")
    print(f"Location: {project_dir}")
    print(f"\nNext steps:")
    print(f"1. Install dependencies: cd {project_dir} && pip install -r requirements.txt")
    print(f"2. Review the configuration in {config_file}")
    print(f"3. Test locally: python connector.py")
    print(f"4. Deploy: fivetran deploy {project_dir}")
    
    return project_dir

async def main():
    parser = argparse.ArgumentParser(
        description="Generate a Fivetran connector from a website."
    )
    parser.add_argument("project_name", help="The project name for the connector (e.g., 'google_news', 'shopify_products').")
    parser.add_argument("url", help="The URL of the website to scrape.")
    parser.add_argument("prompt", help="The prompt for data extraction.")
    parser.add_argument("--api-key", help="Firecrawl API key (optional, will use FIRECRAWL_API_KEY from .env if not provided).")
    args = parser.parse_args()

    print(f"Starting connector generation for project: {args.project_name}")
    print(f"URL: {args.url}")

    initial_state = {
        "url": args.url,
        "prompt": args.prompt,
    }

    app_name = "schema_generation"
    user_id = "user"
    session_id = "session"

    runner = InMemoryRunner(
        agent=schema_generator_agent, app_name=app_name
    )
    session_service = runner.session_service

    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=initial_state,
    )

    print("\n" + "="*60)
    print("STEP 1: Generating schemas from website data...")
    print("="*60)

    user_input = f"Generate schemas for {args.url} with prompt: {args.prompt}"
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(parts=[types.Part(text=user_input)]),
    ):
        if event.error_code is not None:
            print(f"Error Event: {event.error_code}")

    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    print("\n" + "="*60)
    print("STEP 2: Parsing schemas and generating connector...")
    print("="*60)

    if session and hasattr(session, 'state') and session.state:
        state_dict = session.state.to_dict() if hasattr(session.state, 'to_dict') else session.state
        schemas_text = state_dict.get('schemas', '')
        
        firecrawl_schema = None
        fivetran_schema = None
        
        if '```json' in schemas_text or '```' in schemas_text:
            json_blocks = []
            parts = schemas_text.split('```')
            for i in range(1, len(parts), 2):
                block = parts[i]
                if block.startswith('json\n'):
                    block = block[5:]
                json_blocks.append(block.strip())
            
            if len(json_blocks) >= 2:
                try:
                    firecrawl_schema = json.loads(json_blocks[0])
                    fivetran_schema = json.loads(json_blocks[1])
                    print(f"✓ Parsed Firecrawl schema: {len(str(firecrawl_schema))} chars")
                    print(f"✓ Parsed Fivetran schema: {len(str(fivetran_schema))} chars")
                except json.JSONDecodeError as e:
                    print(f"⚠ Error parsing schemas: {e}")
        
        if firecrawl_schema and fivetran_schema:
            connector_code = generate_connector_from_template(
                url=args.url,
                prompt=args.prompt,
                firecrawl_schema=firecrawl_schema,
                fivetran_schema=fivetran_schema
            )
            print(f"✓ Generated connector code: {len(connector_code)} chars")
            
            print("\n" + "="*60)
            print("STEP 3: Creating project structure...")
            print("="*60)
            create_connector_project(connector_code, args.url, args.project_name, args.api_key)
        else:
            print("⚠ Could not parse schemas from agent output")
            print(f"Schemas output preview:\n{schemas_text[:500] if schemas_text else 'N/A'}")
    else:
        print("⚠ Could not retrieve session state")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
import json
import shutil
from pathlib import Path
import gradio as gr
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
    
    enhanced_prompt = f"{prompt} Critical: Always return results as an array/list. Even for a single item, wrap it in an array. If no data found, return empty array []."
    
    connector_code = template_code.replace("{url_to_extract}", url)
    connector_code = connector_code.replace("{extraction_prompt}", enhanced_prompt)
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
    
    firecrawl_api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
    if not firecrawl_api_key:
        firecrawl_api_key = "YOUR_FIRECRAWL_API_KEY_HERE"
    
    config = {
        "firecrawl_api_key": firecrawl_api_key,
        "url": url
    }
    
    config_file = os.path.join(project_dir, "configuration.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
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
    
    requirements_content = """firecrawl-py==4.5.0
"""
    
    requirements_file = os.path.join(project_dir, "requirements.txt")
    with open(requirements_file, "w") as f:
        f.write(requirements_content)
    
    return project_dir


def delete_all_connectors():
    """Delete all existing connector folders."""
    connectors_dir = Path("src/connectors")
    if connectors_dir.exists():
        for item in connectors_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
                yield f"🗑️ Deleted: {item.name}"


async def generate_connector(
    destination_name: str,
    project_name: str,
    url: str,
    prompt: str,
    fivetran_api_key: str,
    fivetran_api_secret: str,
    firecrawl_api_key: str,
    progress=gr.Progress()
):
    """Main function to generate connector with progress tracking."""
    try:
        if not all([destination_name, project_name, url, prompt, fivetran_api_key, fivetran_api_secret, firecrawl_api_key]):
            yield "❌ Error: All fields are required!", None
            return
        
        progress(0, desc="🧹 Cleaning up old connectors...")
        yield "🧹 **Cleaning up old connectors...**\n", None
        
        deletion_logs = []
        for log in delete_all_connectors():
            deletion_logs.append(log)
        
        if deletion_logs:
            yield "🧹 **Cleaned up old connectors:**\n" + "\n".join(deletion_logs) + "\n\n", None
        else:
            yield "🧹 **No existing connectors to clean up**\n\n", None
        
        progress(0.2, desc="🔧 Initializing agent system...")
        yield "🔧 **Initializing agent system...**\n\n", None
        
        initial_state = {
            "url": url,
            "prompt": prompt,
        }
        
        app_name = "schema_generation"
        user_id = "user"
        session_id = f"session_{destination_name}_{project_name}"
        
        runner = InMemoryRunner(agent=schema_generator_agent, app_name=app_name)
        session_service = runner.session_service
        
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=initial_state,
        )
        
        progress(0.3, desc="🤖 Scraping website and generating schemas...")
        yield "🤖 **Scraping website and generating schemas...**\n", None
        yield f"📍 Target URL: `{url}`\n", None
        yield f"📝 Scraping Prompt: _{prompt}_\n\n", None
        
        user_input = f"Generate schemas for {url} with prompt: {prompt}"
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(parts=[types.Part(text=user_input)]),
        ):
            if event.error_code is not None:
                yield f"❌ **Error during schema generation:** {event.error_code}\n", None
                return
        
        progress(0.6, desc="📋 Parsing schemas...")
        yield "📋 **Parsing generated schemas...**\n\n", None
        
        session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        if not session or not hasattr(session, 'state') or not session.state:
            yield "❌ **Error:** Could not retrieve session state\n", None
            return
        
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
                    yield f"✅ **Parsed Firecrawl schema:** {len(str(firecrawl_schema))} characters\n", None
                    yield f"✅ **Parsed Fivetran schema:** {len(str(fivetran_schema))} characters\n\n", None
                except json.JSONDecodeError as e:
                    yield f"❌ **Error parsing schemas:** {e}\n", None
                    return
        
        if not firecrawl_schema or not fivetran_schema:
            yield "❌ **Error:** Could not parse schemas from agent output\n", None
            yield f"**Schemas output preview:**\n```\n{schemas_text[:500] if schemas_text else 'N/A'}\n```\n", None
            return
        
        progress(0.75, desc="🔨 Generating connector code...")
        yield "🔨 **Generating connector code from template...**\n\n", None
        
        connector_code = generate_connector_from_template(
            url=url,
            prompt=prompt,
            firecrawl_schema=firecrawl_schema,
            fivetran_schema=fivetran_schema
        )
        
        yield f"✅ **Generated connector code:** {len(connector_code)} characters\n\n", None
        
        progress(0.9, desc="📦 Creating project structure...")
        yield "📦 **Creating project structure...**\n\n", None
        
        project_dir = create_connector_project(connector_code, url, project_name, firecrawl_api_key)
        
        progress(1.0, desc="✅ Complete!")
        
        result = f"""
# ✅ Connector Generated Successfully!

## 📊 Project Details
- **Destination:** `{destination_name}`
- **Project Name:** `{project_name}`
- **Location:** `{project_dir}`
- **Target URL:** `{url}`

## 📁 Generated Files
- ✅ `connector.py` - Main connector implementation
- ✅ `configuration.json` - API keys and configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `README.md` - Documentation

## 🚀 Next Steps

### 1. Install Dependencies
```bash
cd {project_dir} && pip install -r requirements.txt
```

### 2. Test Locally
```bash
python {project_dir}/connector.py
```

### 3. Deploy to Fivetran
```bash
fivetran deploy {project_dir}
```

## 🔑 Configuration Summary
- **Fivetran API Key:** `{fivetran_api_key[:8]}...`
- **Fivetran API Secret:** `{fivetran_api_secret[:8]}...`
- **Firecrawl API Key:** `{firecrawl_api_key[:8]}...`

---

**Ready to sync your data! 🎉**
"""
        
        yield result, project_dir
        
    except Exception as e:
        error_message = f"""
# ❌ Error Occurred

**Error Type:** `{type(e).__name__}`

**Error Message:**
```
{str(e)}
```

Please check your inputs and try again.
"""
        yield error_message, None


def create_interface():
    """Create the Gradio interface."""
    
    custom_css = """
    .main-container {
        max-width: 1200px !important;
        margin: auto;
    }
    .output-markdown {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
    }
    .input-group {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    """
    
    with gr.Blocks(
        title="5tran - Fivetran Connector Generator",
        theme=gr.themes.Soft(primary_hue="green", secondary_hue="blue"),
        css=custom_css
    ) as interface:
        
        gr.Markdown(
            """
            # 🚀 5tran - Fivetran Connector Generator
            
            **Automatically generate Fivetran connectors from any website**
            
            Fill in the details below to generate a custom connector that extracts data from your target website.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 📋 Configuration")
                
                destination_name = gr.Textbox(
                    label="Destination Name",
                    placeholder="e.g., BigQuery-Production",
                    info="The name of your Fivetran destination"
                )
                
                project_name = gr.Textbox(
                    label="Project Name",
                    placeholder="e.g., google_news_scraper",
                    info="Name for your connector project (will be sanitized)"
                )
                
                url = gr.Textbox(
                    label="Target URL",
                    placeholder="https://example.com",
                    info="The website URL to scrape data from"
                )
                
                prompt = gr.Textbox(
                    label="Scraping Prompt",
                    placeholder="Extract top 10 news articles with title, URL, and summary",
                    lines=3,
                    info="Describe what data you want to scrape from the website"
                )
                
                gr.Markdown("## 🔑 API Credentials")
                
                fivetran_api_key = gr.Textbox(
                    label="Fivetran API Key",
                    type="password",
                    placeholder="Enter your Fivetran API Key"
                )
                
                fivetran_api_secret = gr.Textbox(
                    label="Fivetran API Secret",
                    type="password",
                    placeholder="Enter your Fivetran API Secret"
                )
                
                firecrawl_api_key = gr.Textbox(
                    label="Firecrawl API Key",
                    type="password",
                    placeholder="Enter your Firecrawl API Key",
                    info="Used for website scraping"
                )
                
                generate_btn = gr.Button(
                    "🚀 Generate Connector",
                    variant="primary",
                    size="lg"
                )
                
            with gr.Column(scale=1):
                gr.Markdown("## 📊 Generation Progress")
                
                output_status = gr.Markdown(
                    value="**Ready to generate connector...**\n\nFill in all fields and click 'Generate Connector' to begin.",
                    elem_classes=["output-markdown"]
                )
                
                output_path = gr.Textbox(
                    label="Generated Connector Path",
                    interactive=False,
                    visible=False
                )
        
        gr.Markdown(
            """
            ---
            
            ### 💡 Tips
            - Ensure all API keys are valid before generating
            - The project name will be sanitized (special characters replaced with underscores)
            - All existing connectors will be deleted before generation
            - Generated connectors can be tested locally before deploying to Fivetran
            
            ### 📚 Documentation
            - [Fivetran Documentation](https://fivetran.com/docs)
            - [Firecrawl Documentation](https://firecrawl.dev/docs)
            """
        )
        
        async def handle_generation(*args):
            async for status, path in generate_connector(*args):
                if path:
                    yield status, gr.update(value=path, visible=True)
                else:
                    yield status, gr.update(visible=False)
        
        generate_btn.click(
            fn=handle_generation,
            inputs=[
                destination_name,
                project_name,
                url,
                prompt,
                fivetran_api_key,
                fivetran_api_secret,
                firecrawl_api_key
            ],
            outputs=[output_status, output_path]
        )
    
    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.queue()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


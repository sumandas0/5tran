import asyncio
import os
import json
import shutil
import subprocess
import base64
import zipfile
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


def deploy_to_fivetran(project_dir: str, api_key_base64: str, destination_name: str, project_name: str) -> tuple[bool, str]:
    """Deploy connector to Fivetran using CLI."""
    try:
        cmd = [
            'fivetran',
            'deploy',
            project_dir,
            '--api-key',
            api_key_base64,
            '--destination',
            destination_name,
            '--connection',
            project_name,
            '--configuration',
            'configuration.json',
            '--force'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, f"Deployment failed:\n{result.stderr}\n{result.stdout}"
    
    except subprocess.TimeoutExpired:
        return False, "Deployment timed out after 5 minutes"
    except FileNotFoundError:
        return False, "Fivetran CLI not found. Please install it using: pip install fivetran-cli"
    except Exception as e:
        return False, f"Deployment error: {str(e)}"


def delete_all_connectors():
    """Delete all existing connector folders."""
    connectors_dir = Path("src/connectors")
    if connectors_dir.exists():
        for item in connectors_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
                yield f"🗑️ Deleted: {item.name}"


def create_zip_from_directory(source_dir: str, output_filename: str) -> str:
    """Create a zip file from a directory."""
    zip_path = f"{output_filename}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        source_path = Path(source_dir)
        for file_path in source_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(source_path.parent)
                zipf.write(file_path, arcname)
    return zip_path


async def generate_connector(
    access_password: str,
    destination_name: str,
    project_name: str,
    url: str,
    prompt: str,
    fivetran_api_key_base64: str,
    firecrawl_api_key: str,
    progress=gr.Progress()
):
    """Main function to generate connector with progress tracking."""
    try:
        if not all([access_password, destination_name, project_name, url, prompt]):
            yield "❌ Error: Access password, destination name, project name, URL, and prompt are required!", None
            return
        
        correct_password = os.getenv("ACCESS_PASSWORD")
        if not correct_password:
            yield "❌ Error: ACCESS_PASSWORD environment variable is not set on the server. Please contact the administrator.", None
            return
        
        if access_password != correct_password:
            yield "❌ Error: Invalid access password. Please enter the correct password to continue.", None
            return
        
        if not fivetran_api_key_base64:
            fivetran_api_key_base64 = os.getenv("FIVETRAN_API_SECRET_BASE64")
            if not fivetran_api_key_base64:
                yield "❌ Error: Fivetran API Key is required. Either provide it in the form or set FIVETRAN_API_SECRET_BASE64 environment variable.", None
                return
            yield f"ℹ️ Using Fivetran API key from environment variable\n\n", None
        
        if not firecrawl_api_key:
            firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
            if not firecrawl_api_key:
                yield "❌ Error: Firecrawl API Key is required. Either provide it in the form or set FIRECRAWL_API_KEY environment variable.", None
                return
            yield f"ℹ️ Using Firecrawl API key from environment variable\n\n", None
        
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
        
        yield f"✅ **Project created at:** `{project_dir}`\n\n", None
        
        progress(0.95, desc="🚀 Deploying to Fivetran...")
        yield "🚀 **Deploying connector to Fivetran...**\n", None
        yield f"📍 Destination: `{destination_name}`\n\n", None
        
        success, deploy_message = deploy_to_fivetran(
            project_dir=project_dir,
            api_key_base64=fivetran_api_key_base64,
            destination_name=destination_name,
            project_name=project_name
        )
        
        progress(1.0, desc="✅ Complete!")
        
        if success:
            gr.Info(
                f"🎉 Deployment Successful!\n\n"
                f"Your connector '{project_name}' has been successfully deployed to Fivetran destination '{destination_name}'.\n\n"
                f"The connector is now live and ready to sync data!",
                duration=10
            )
            
            result = f"""
# ✅ Connector Generated & Deployed Successfully!

## 📊 Project Details
- **Destination:** `{destination_name}`
- **Project Name:** `{project_name}`
- **Location:** `{project_dir}`
- **Target URL:** `{url}`
- **Status:** ✅ Deployed to Fivetran

## 📁 Generated Files
- ✅ `connector.py` - Main connector implementation
- ✅ `configuration.json` - API keys and configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `README.md` - Documentation

## 🔧 Local Testing (Optional)

### 1. Install Dependencies
```bash
cd {project_dir} && pip install -r requirements.txt
```

### 2. Test Locally
```bash
python {project_dir}/connector.py
```

## 🔑 Configuration Summary
- **Fivetran API Key (Base64):** `{fivetran_api_key_base64[:12]}...`
- **Firecrawl API Key:** `{firecrawl_api_key[:8]}...`

---

**Your connector is now live and syncing data! 🎉**
"""
            zip_file = create_zip_from_directory(project_dir, project_dir)
            yield result, zip_file
        else:
            gr.Warning(
                f"⚠️ Deployment Failed\n\n"
                f"Connector generated successfully but deployment to Fivetran failed.\n\n"
                f"Error: {deploy_message[:200]}...\n\n"
                f"Please check the details below for manual deployment instructions.",
                duration=15
            )
            
            result = f"""
# ⚠️ Connector Generated But Deployment Failed

## 📊 Project Details
- **Destination:** `{destination_name}`
- **Project Name:** `{project_name}`
- **Location:** `{project_dir}`
- **Target URL:** `{url}`
- **Status:** ⚠️ Deployment failed

## 📁 Generated Files
- ✅ `connector.py` - Main connector implementation
- ✅ `configuration.json` - API keys and configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `README.md` - Documentation

## ❌ Deployment Error Details

```
{deploy_message}
```

## 🔧 Manual Deployment Steps

You can deploy manually using these steps:

### 1. Install Dependencies
```bash
cd {project_dir} && pip install -r requirements.txt
```

### 2. Test Locally
```bash
python {project_dir}/connector.py
```

### 3. Deploy Manually
```bash
fivetran deploy {project_dir} --api-key {fivetran_api_key_base64} --destination {destination_name} --connection {project_name} --configuration configuration.json --force
```

## 🔑 Configuration Summary
- **Fivetran API Key (Base64):** `{fivetran_api_key_base64[:12]}...`
- **Firecrawl API Key:** `{firecrawl_api_key[:8]}...`

---

**Please resolve the deployment issue and try again.**
"""
            zip_file = create_zip_from_directory(project_dir, project_dir)
            yield result, zip_file
        
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
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        min-height: 400px;
    }
    .output-markdown * {
        color: #e0e0e0 !important;
    }
    .output-markdown h1 {
        color: #4CAF50 !important;
    }
    .output-markdown h2 {
        color: #66BB6A !important;
    }
    .output-markdown code {
        background-color: #2d2d2d !important;
        color: #81C784 !important;
        padding: 2px 6px;
        border-radius: 3px;
    }
    .output-markdown pre {
        background-color: #2d2d2d !important;
        border: 1px solid #3d3d3d;
        padding: 10px;
        border-radius: 5px;
    }
    .output-markdown strong {
        color: #ffffff !important;
        font-weight: 600;
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
            
            **Automatically generate and deploy Fivetran connectors from any website**
            
            Fill in the details below to generate a custom connector that extracts data from your target website and automatically deploy it to Fivetran.
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
                
                gr.Markdown("## 🔑 Authentication & API Credentials")
                
                access_password = gr.Textbox(
                    label="Access Password",
                    type="password",
                    placeholder="Enter the access password",
                    info="Required to prevent API misuse - provided by administrator"
                )
                
                fivetran_api_key_base64 = gr.Textbox(
                    label="Fivetran API Key (Base64 Encoded)",
                    type="password",
                    placeholder="Enter your Base64-encoded Fivetran API key (optional)",
                    info="Optional - Will use FIVETRAN_API_SECRET_BASE64 env var if not provided"
                )
                
                firecrawl_api_key = gr.Textbox(
                    label="Firecrawl API Key",
                    type="password",
                    placeholder="Enter your Firecrawl API Key (optional)",
                    info="Optional - Will use FIRECRAWL_API_KEY env var if not provided"
                )
                
                generate_btn = gr.Button(
                    "🚀 Generate & Deploy Connector",
                    variant="primary",
                    size="lg"
                )
                
            with gr.Column(scale=1):
                gr.Markdown("## 📊 Generation Progress")
                
                output_status = gr.Markdown(
                    value="**Ready to generate and deploy connector...**\n\nFill in all fields and click 'Generate & Deploy Connector' to begin.",
                    elem_classes=["output-markdown"]
                )
                
                download_btn = gr.File(
                    label="📦 Download Connector (ZIP)",
                    visible=False,
                    interactive=False
                )
        
        gr.Markdown(
            """
            ---
            
            ### 💡 Tips
            - **Access Password Required**: You must enter the correct access password to use this service
            - **API Keys**: Fivetran and Firecrawl API keys are optional if set in environment variables
            - **Download**: After generation, download the connector as a ZIP file using the download button
            - The project name will be sanitized (special characters replaced with underscores)
            - All existing connectors will be deleted before generation
            - The connector will be automatically deployed to Fivetran after generation
            - If deployment fails, you can deploy manually using the provided commands
            
            ### 📚 Documentation
            - [Fivetran Documentation](https://fivetran.com/docs)
            - [Firecrawl Documentation](https://firecrawl.dev/docs)
            - [Fivetran CLI](https://github.com/fivetran/fivetran-cli)
            """
        )
        
        async def handle_generation(*args):
            async for status, zip_file in generate_connector(*args):
                if zip_file:
                    yield status, gr.update(value=zip_file, visible=True)
                else:
                    yield status, gr.update(visible=False)
        
        generate_btn.click(
            fn=handle_generation,
            inputs=[
                access_password,
                destination_name,
                project_name,
                url,
                prompt,
                fivetran_api_key_base64,
                firecrawl_api_key
            ],
            outputs=[output_status, download_btn]
        )
    
    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.queue()
    port = int(os.getenv("PORT", 7860))
    interface.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True
    )


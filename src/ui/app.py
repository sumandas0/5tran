"""Gradio UI for 5Tran AI Pipeline Automation."""

import gradio as gr
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrator import PipelineOrchestrator
from src.config import validate_config


class FiveTranUI:
    """Gradio UI for 5Tran pipeline automation."""
    
    def __init__(self):
        """Initialize UI components."""
        self.orchestrator = PipelineOrchestrator()
        self.current_pipeline = None
    
    def create_pipeline(self, requirements: str, openapi_file,
                       auth_method: str, auth_header_name: str, auth_header_prefix: str,
                       auto_deploy: bool, group_id: str, 
                       api_url: str, api_key: str, auth_type: str,
                       progress=gr.Progress()):
        """Create a new data pipeline from requirements."""
        try:
            progress(0, desc="Analyzing requirements...")
            
            # Read OpenAPI spec if provided
            openapi_spec = None
            if openapi_file is not None:
                with open(openapi_file.name, 'r') as f:
                    openapi_spec = f.read()
            
            progress(0.2, desc="Parsing specifications...")
            
            # Prepare deployment credentials if auto-deploy enabled
            source_api_credentials = None
            fivetran_group_id = None
            
            # Store auth configuration for connector generation
            auth_config = {
                "method": auth_method,
                "header_name": auth_header_name if auth_header_name else "Authorization",
                "header_prefix": auth_header_prefix if auth_header_prefix else "Bearer"
            }
            
            if auto_deploy:
                if not group_id or not api_url or not api_key:
                    return "❌ Auto-deploy enabled but missing required fields: Fivetran Group ID, API URL, or API Key"
                
                fivetran_group_id = group_id.strip()
                source_api_credentials = {
                    "api_url": api_url.strip(),
                    "api_key": api_key.strip(),
                    "auth_type": auth_method,
                    "auth_config": auth_config
                }
            
            # Create pipeline
            progress(0.3, desc="Creating pipeline...")
            result = self.orchestrator.create_pipeline(
                requirements=requirements,
                openapi_spec=openapi_spec,
                auto_deploy=auto_deploy,
                fivetran_group_id=fivetran_group_id,
                source_api_credentials=source_api_credentials,
                auth_config=auth_config
            )
            
            progress(0.8, desc="Generating artifacts...")
            
            self.current_pipeline = result
            
            progress(1.0, desc="Pipeline created!")
            
            # Format output
            output = f"""
## ✅ Pipeline Created Successfully!

**Source:** {result['analysis']['source_name']}
**Type:** {result['analysis']['source_type']}

### 📊 Entities
{', '.join(result['analysis']['entities'])}

### 📈 Business Metrics
{', '.join(result['analysis']['business_metrics'])}

### 🔧 Created Components

**Fivetran Connector:**
- Name: `{result['fivetran']['connector_name']}`
- Directory: `{result['fivetran']['connector_dir']}`
"""
            
            # Add deployment status
            if result['fivetran'].get('deployed'):
                output += f"""
- ✅ **DEPLOYED** to Fivetran
- Connector ID: `{result['fivetran'].get('connector_id', 'N/A')}`
- Status: Syncing data to your warehouse!
"""
            elif auto_deploy:
                output += f"""
- ❌ **Deployment Failed**
- Error: {result['fivetran'].get('deployment', {}).get('error', 'Unknown error')}
- You can deploy manually using CLI scripts
"""
            else:
                output += """
- 📝 Not deployed (auto-deploy was disabled)
- Deploy using CLI: `python scripts/deploy_connector.py`
"""
            
            output += f"""

**dbt Models:**
- Staging: {', '.join(result['dbt']['staging_models'])}
- Marts: {', '.join(result['dbt']['mart_models'])}

**BigQuery:**
- Dataset: {result['bigquery']['dataset']}
- Tables: {len(result['bigquery']['tables'])} tables created

### 📁 Files Created
{len(result.get('files_created', []))} files generated in project directory
"""
            
            return output
            
        except Exception as e:
            return f"❌ Error creating pipeline: {str(e)}"
    
    def execute_nl_query(self, query: str, progress=gr.Progress()):
        """Execute natural language query and return results."""
        try:
            progress(0.3, desc="Generating SQL...")
            
            result = self.orchestrator.execute_nl_query(query)
            
            progress(0.7, desc="Executing query...")
            
            # Format SQL
            sql_output = f"```sql\n{result['sql']}\n```"
            
            # Format results
            if "error" in result:
                results_output = f"❌ Error: {result['error']}"
                df = pd.DataFrame()
            else:
                rows = result.get('rows', [])
                if rows:
                    df = pd.DataFrame(rows)
                    results_output = f"✅ Query executed successfully! {len(rows)} rows returned."
                else:
                    df = pd.DataFrame()
                    results_output = "✅ Query executed successfully! No rows returned."
            
            progress(1.0, desc="Complete!")
            
            return sql_output, results_output, df
            
        except Exception as e:
            return f"```sql\n-- Error generating SQL\n```", f"❌ Error: {str(e)}", pd.DataFrame()
    
    def get_pipeline_status(self):
        """Get status of current pipeline."""
        try:
            status = self.orchestrator.get_status()
            
            if not status:
                return "No pipeline created yet. Create a pipeline in the Pipeline Creator tab."
            
            output = f"""
## 📊 Pipeline Status

### Connectors
"""
            for connector in status['connectors']:
                output += f"- **{connector['name']}**: {connector.get('status', 'configured')}\n"
            
            output += "\n### dbt Models\n"
            models = status['dbt_models']
            output += f"- Staging: {len(models['staging'])} models\n"
            output += f"- Marts: {len(models['marts'])} models\n"
            
            output += "\n### BigQuery Tables\n"
            for table in status['bigquery_tables']:
                output += f"- {table}\n"
            
            return output
            
        except Exception as e:
            return f"❌ Error getting status: {str(e)}"
    
    def launch(self):
        """Launch Gradio interface."""
        
        # Check configuration
        config_valid = validate_config()
        
        with gr.Blocks(title="5Tran AI Pipeline Automation", theme=gr.themes.Soft()) as demo:
            gr.Markdown("""
# 🚀 5Tran AI Pipeline Automation
Create end-to-end data pipelines with AI - from source to warehouse to insights.
""")
            
            if not config_valid:
                gr.Markdown("""
⚠️ **Configuration Warning**: Some required environment variables are missing.
Please create a `.env` file based on `.env.example` for full functionality.

Running in development/mock mode.
""")
            
            with gr.Tabs():
                # Tab 1: Pipeline Creator
                with gr.Tab("🔧 Pipeline Creator"):
                    gr.Markdown("""
### Create Your Data Pipeline
Describe your data requirements in natural language, and optionally provide an OpenAPI specification.
""")
                    
                    requirements_input = gr.Textbox(
                        label="Requirements",
                        placeholder="Example: I want to sync data from our e-commerce API including orders, customers, and products. Calculate monthly revenue and customer lifetime value.",
                        lines=5
                    )
                    
                    openapi_file = gr.File(
                        label="OpenAPI Specification (optional)",
                        file_types=[".json", ".yaml", ".yml"]
                    )
                    
                    gr.Markdown("### 🔑 Authentication Configuration")
                    gr.Markdown("Configure how to authenticate with your source API")
                    
                    with gr.Group():
                        gr.Markdown("**Authentication Method**")
                        
                        auth_method_dropdown = gr.Dropdown(
                            label="Auth Method",
                            choices=[
                                "bearer",
                                "api_key_header",
                                "basic_auth",
                                "custom_header"
                            ],
                            value="bearer",
                            info="How does your API authenticate requests?"
                        )
                        
                        with gr.Row():
                            auth_header_name = gr.Textbox(
                                label="Header Name (for custom_header or api_key_header)",
                                placeholder="e.g., X-API-Key, Authorization",
                                value="Authorization",
                                visible=False
                            )
                            auth_header_prefix = gr.Textbox(
                                label="Header Prefix (optional)",
                                placeholder="e.g., Bearer, Token",
                                value="Bearer",
                                visible=False
                            )
                        
                        gr.Markdown("""
**Auth Method Guide:**
- `bearer`: Authorization: Bearer {token} (most common)
- `api_key_header`: Custom header like X-API-Key: {key}
- `basic_auth`: Authorization: Basic {base64(user:pass)}
- `custom_header`: Any custom header format
                        """)
                        
                        # Show/hide fields based on auth method
                        def update_auth_fields(method):
                            if method == "custom_header" or method == "api_key_header":
                                return gr.update(visible=True), gr.update(visible=True)
                            elif method == "bearer":
                                return gr.update(visible=False), gr.update(visible=False)
                            else:
                                return gr.update(visible=False), gr.update(visible=False)
                        
                        auth_method_dropdown.change(
                            fn=update_auth_fields,
                            inputs=[auth_method_dropdown],
                            outputs=[auth_header_name, auth_header_prefix]
                        )
                    
                    gr.Markdown("### 🚀 Auto-Deploy Settings (Optional)")
                    gr.Markdown("Enable to automatically deploy connector to Fivetran after generation")
                    
                    auto_deploy_checkbox = gr.Checkbox(
                        label="Auto-deploy to Fivetran",
                        value=False,
                        info="Check to deploy immediately after generation"
                    )
                    
                    with gr.Group(visible=True) as deploy_settings:
                        with gr.Row():
                            group_id_input = gr.Textbox(
                                label="Fivetran Group ID",
                                placeholder="Enter your Fivetran group ID",
                                info="Get this from: python scripts/list_fivetran_groups.py"
                            )
                        
                        gr.Markdown("**Source API Credentials** (for the data source you're connecting)")
                        
                        with gr.Row():
                            api_url_input = gr.Textbox(
                                label="API Base URL",
                                placeholder="https://api.example.com",
                                scale=2
                            )
                            auth_type_dropdown = gr.Dropdown(
                                label="Auth Type",
                                choices=["bearer", "api_key", "oauth2"],
                                value="bearer",
                                scale=1
                            )
                        
                        api_key_input = gr.Textbox(
                            label="API Key / Token",
                            placeholder="your_api_key_here",
                            type="password"
                        )
                    
                    create_btn = gr.Button("Create & Deploy Pipeline", variant="primary", size="lg")
                    
                    pipeline_output = gr.Markdown(label="Pipeline Details")
                    
                    create_btn.click(
                        fn=self.create_pipeline,
                        inputs=[
                            requirements_input, 
                            openapi_file,
                            auth_method_dropdown,
                            auth_header_name,
                            auth_header_prefix,
                            auto_deploy_checkbox,
                            group_id_input,
                            api_url_input,
                            api_key_input,
                            auth_type_dropdown
                        ],
                        outputs=pipeline_output
                    )
                
                # Tab 2: SQL Chat
                with gr.Tab("💬 SQL Chat"):
                    gr.Markdown("""
### Ask Questions About Your Data
Ask questions in natural language, and get SQL queries and results.
""")
                    
                    nl_query_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Example: What are the top 10 customers by revenue this month?",
                        lines=3
                    )
                    
                    query_btn = gr.Button("Generate & Execute", variant="primary")
                    
                    with gr.Row():
                        sql_output = gr.Markdown(label="Generated SQL")
                    
                    with gr.Row():
                        query_status = gr.Markdown(label="Status")
                    
                    with gr.Row():
                        results_df = gr.Dataframe(label="Results", wrap=True)
                    
                    query_btn.click(
                        fn=self.execute_nl_query,
                        inputs=[nl_query_input],
                        outputs=[sql_output, query_status, results_df]
                    )
                
                # Tab 3: Pipeline Status
                with gr.Tab("📊 Pipeline Status"):
                    gr.Markdown("""
### View Your Pipeline Status
Check the status of connectors, models, and tables.
""")
                    
                    status_btn = gr.Button("Refresh Status", variant="secondary")
                    status_output = gr.Markdown(label="Status")
                    
                    status_btn.click(
                        fn=self.get_pipeline_status,
                        inputs=[],
                        outputs=status_output
                    )
                    
                    # Auto-load status on tab open
                    demo.load(
                        fn=self.get_pipeline_status,
                        inputs=[],
                        outputs=status_output
                    )
            
            gr.Markdown("""
---
**5Tran AI Pipeline Automation** - Development Prototype  
Powered by Google Gemini, Fivetran, dbt, and BigQuery
""")
        
        return demo


def main():
    """Main entry point for Gradio app."""
    print("🚀 Starting 5Tran AI Pipeline Automation...")
    print("=" * 50)
    
    # Validate configuration
    validate_config()
    
    # Create and launch UI
    ui = FiveTranUI()
    demo = ui.launch()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    main()


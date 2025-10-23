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
    
    def create_pipeline(self, requirements: str, openapi_file, progress=gr.Progress()):
        """Create a new data pipeline from requirements."""
        try:
            progress(0, desc="Analyzing requirements...")
            
            # Read OpenAPI spec if provided
            openapi_spec = None
            if openapi_file is not None:
                with open(openapi_file.name, 'r') as f:
                    openapi_spec = f.read()
            
            progress(0.2, desc="Parsing specifications...")
            
            # Create pipeline
            result = self.orchestrator.create_pipeline(
                requirements=requirements,
                openapi_spec=openapi_spec
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
- Configuration: `{result['fivetran']['config_file']}`

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
                    
                    create_btn = gr.Button("Create Pipeline", variant="primary", size="lg")
                    
                    pipeline_output = gr.Markdown(label="Pipeline Details")
                    
                    create_btn.click(
                        fn=self.create_pipeline,
                        inputs=[requirements_input, openapi_file],
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


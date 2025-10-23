"""Generate command - scaffolds pipeline from OpenAPI spec."""

import typer
import yaml
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from typing import Optional

from src.connectors.openapi_parser import OpenAPIParser
from src.connectors.fivetran_sdk_generator import FivetranSDKGenerator
from src.transformations.dbt_generator import DBTGenerator
from src.config import GCP_PROJECT_ID, BIGQUERY_DATASET

generate_app = typer.Typer()
console = Console()


@generate_app.command()
def pipeline(
    description: str = typer.Argument(..., help="Pipeline description (e.g., 'Pipeline to get github api to bigquery')"),
    spec: Path = typer.Option(..., "--spec", "-s", help="Path to OpenAPI spec file (JSON or YAML)"),
    output: Path = typer.Option("./generated", "--output", "-o", help="Output directory for generated files"),
    project_id: Optional[str] = typer.Option(None, "--project", "-p", help="GCP Project ID"),
    dataset: Optional[str] = typer.Option(None, "--dataset", "-d", help="BigQuery dataset name"),
):
    """
    Generate complete pipeline from OpenAPI specification.
    
    This command:
    - Parses OpenAPI spec
    - Generates Fivetran Connector SDK skeleton
    - Creates dbt project with staging models
    - Emits .5tran.yml deployment config
    
    Example:
        5tran generate "GitHub API to BigQuery" --spec openapi.yaml
    """
    console.print(Panel.fit(
        f"[bold cyan]Generating Pipeline[/bold cyan]\n{description}",
        border_style="cyan"
    ))
    
    # Validate spec file
    if not spec.exists():
        console.print(f"[red]Error:[/red] OpenAPI spec not found: {spec}")
        raise typer.Exit(1)
    
    # Read OpenAPI spec
    with console.status(f"[bold green]Reading OpenAPI spec from {spec}..."):
        try:
            with open(spec, 'r') as f:
                spec_content = f.read()
            parser = OpenAPIParser(spec_content)
            api_summary = parser.get_summary()
            console.print(f"[green]✓[/green] Parsed API: {api_summary['title']}")
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to parse OpenAPI spec: {e}")
            raise typer.Exit(1)
    
    # Display API summary
    summary_table = Table(title="API Summary", show_header=True)
    summary_table.add_column("Property", style="cyan")
    summary_table.add_column("Value", style="white")
    summary_table.add_row("Title", api_summary.get("title", "N/A"))
    summary_table.add_row("Version", api_summary.get("version", "N/A"))
    summary_table.add_row("Base URL", api_summary.get("base_url", "N/A"))
    summary_table.add_row("Auth Type", api_summary.get("auth_type", "N/A"))
    summary_table.add_row("Endpoints", str(len(api_summary.get("endpoints", []))))
    summary_table.add_row("Entities", ", ".join(api_summary.get("entities", [])))
    console.print(summary_table)
    
    # Create output directory
    output.mkdir(parents=True, exist_ok=True)
    
    # Generate pipeline name from description
    pipeline_name = description.lower().replace(" ", "_").replace("-", "_")
    pipeline_name = ''.join(c for c in pipeline_name if c.isalnum() or c == '_')
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Step 1: Generate Fivetran Connector SDK
        task1 = progress.add_task("[cyan]Generating Fivetran Connector SDK...", total=1)
        sdk_generator = FivetranSDKGenerator()
        connector_dir = output / "connector"
        sdk_files = sdk_generator.generate_connector(
            api_summary=api_summary,
            output_dir=connector_dir,
            connector_name=pipeline_name
        )
        progress.update(task1, completed=1)
        console.print(f"[green]✓[/green] Generated Fivetran SDK at {connector_dir}")
        
        # Step 2: Generate dbt project
        task2 = progress.add_task("[cyan]Generating dbt project...", total=1)
        dbt_dir = output / "dbt"
        dbt_dir.mkdir(parents=True, exist_ok=True)
        
        dbt_generator = DBTGenerator(project_name=pipeline_name)
        dbt_generator.project_dir = dbt_dir
        dbt_generator.models_dir = dbt_dir / "models"
        dbt_generator._setup_project_structure()
        
        # Initialize dbt project
        gcp_project = project_id or GCP_PROJECT_ID or "your-gcp-project"
        bq_dataset = dataset or BIGQUERY_DATASET or "your_dataset"
        dbt_generator.initialize_project(gcp_project, bq_dataset)
        
        # Create staging models for each entity
        source_name = pipeline_name
        entities = api_summary.get("entities", [])
        staging_models = []
        
        for entity in entities:
            # Get schema for this entity/endpoint
            endpoint = next((e for e in api_summary.get("endpoints", []) if entity in e), None)
            if endpoint:
                schema = parser.get_endpoint_schema(endpoint)
            else:
                schema = None
            
            # Create columns from schema
            columns = []
            if schema and "properties" in schema:
                for prop_name, prop_info in schema.get("properties", {}).items():
                    columns.append({
                        "name": prop_name,
                        "type": prop_info.get("type", "STRING")
                    })
            else:
                # Default columns
                columns = [
                    {"name": "id", "type": "STRING"},
                    {"name": "data", "type": "JSON"},
                    {"name": "created_at", "type": "TIMESTAMP"}
                ]
            
            model_file = dbt_generator.create_staging_model(
                source_name=source_name,
                table_name=entity,
                columns=columns
            )
            staging_models.append(model_file.stem)
        
        # Create sources.yml
        tables_for_sources = [
            {
                "name": entity,
                "description": f"{entity} data from {api_summary['title']}",
                "columns": [{"name": "id", "type": "STRING"}]
            }
            for entity in entities
        ]
        dbt_generator.create_sources_yml(source_name, tables_for_sources)
        
        # Create schema.yml
        dbt_generator.create_schema_yml(staging_models)
        
        progress.update(task2, completed=1)
        console.print(f"[green]✓[/green] Generated dbt project at {dbt_dir}")
        
        # Step 3: Generate deployment config
        task3 = progress.add_task("[cyan]Creating deployment config...", total=1)
        config_file = output / ".5tran.yml"
        
        deploy_config = {
            "pipeline": {
                "name": pipeline_name,
                "description": description,
            },
            "source": {
                "api_title": api_summary.get("title"),
                "base_url": api_summary.get("base_url"),
                "auth_type": api_summary.get("auth_type"),
                "entities": entities,
                "endpoints": api_summary.get("endpoints", [])[:10],  # Limit endpoints
            },
            "fivetran": {
                "group_name": f"{pipeline_name}_group",
                "connector_name": pipeline_name,
                "connector_type": "connector_sdk",
                "connector_dir": "./connector",
                "sync_frequency": 360,  # 6 hours in minutes
            },
            "destination": {
                "type": "bigquery",
                "project_id": gcp_project,
                "dataset": bq_dataset,
            },
            "dbt": {
                "project_dir": "./dbt",
                "run_after_sync": True,
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(deploy_config, f, default_flow_style=False, sort_keys=False)
        
        progress.update(task3, completed=1)
        console.print(f"[green]✓[/green] Created deployment config at {config_file}")
    
    # Summary
    console.print("\n")
    console.print(Panel.fit(
        "[bold green]✓ Pipeline Generated Successfully![/bold green]\n\n"
        f"[cyan]Output Directory:[/cyan] {output}\n"
        f"[cyan]Connector SDK:[/cyan] {connector_dir}\n"
        f"[cyan]dbt Project:[/cyan] {dbt_dir}\n"
        f"[cyan]Deploy Config:[/cyan] {config_file}\n\n"
        "[yellow]Next Steps:[/yellow]\n"
        f"1. Review and customize generated files\n"
        f"2. Update connector credentials in {connector_dir}/configuration.json\n"
        f"3. Run: [bold]5tran deploy --config {config_file}[/bold]",
        border_style="green"
    ))


if __name__ == "__main__":
    generate_app()


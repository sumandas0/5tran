"""5tran CLI - Data pipeline automation from OpenAPI to BigQuery via Fivetran."""

import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="5tran",
    help="🚀 Automate data pipelines from OpenAPI specs to BigQuery via Fivetran",
    add_completion=False,
)

console = Console()

# Import commands
from src.cli.commands.generate import generate_app
from src.cli.commands.deploy import deploy_app
from src.cli.commands.status import status_app

# Add sub-commands
app.add_typer(generate_app, name="generate", help="Generate pipeline from OpenAPI spec")
app.add_typer(deploy_app, name="deploy", help="Deploy pipeline to Fivetran")
app.add_typer(status_app, name="status", help="Check pipeline status")


@app.callback()
def callback():
    """
    5tran - Data Pipeline Automation
    
    Scaffold data pipelines from OpenAPI specs and deploy to Fivetran.
    """
    pass


@app.command()
def version():
    """Show version information."""
    console.print(Panel.fit(
        "[bold cyan]5tran[/bold cyan] v0.1.0\n"
        "Data Pipeline Automation Tool\n"
        "OpenAPI → Fivetran → BigQuery → dbt",
        border_style="cyan"
    ))


def main():
    """Main entry point for CLI."""
    app()


if __name__ == "__main__":
    main()


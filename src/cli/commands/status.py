"""Status command - check pipeline status."""

import typer
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional
import os

from src.connectors.fivetran_api_client import FivetranAPIClient
from src.config import FIVETRAN_API_KEY, FIVETRAN_API_SECRET

status_app = typer.Typer()
console = Console()


@status_app.command()
def check(
    config: Path = typer.Option("./.5tran-deployment.yml", "--config", "-c", help="Path to deployment config"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Fivetran API key"),
    api_secret: Optional[str] = typer.Option(None, "--api-secret", help="Fivetran API secret"),
    connector_id: Optional[str] = typer.Option(None, "--connector-id", help="Specific connector ID to check"),
):
    """
    Check pipeline deployment and sync status.
    
    Example:
        5tran status check
        5tran status check --connector-id abc123
    """
    console.print(Panel.fit(
        "[bold cyan]Pipeline Status Check[/bold cyan]",
        border_style="cyan"
    ))
    
    # Get API credentials
    api_key = api_key or FIVETRAN_API_KEY or os.getenv("FIVETRAN_API_KEY")
    api_secret = api_secret or FIVETRAN_API_SECRET or os.getenv("FIVETRAN_API_SECRET")
    
    if not api_key or not api_secret:
        console.print("[red]Error:[/red] Fivetran API credentials not found")
        raise typer.Exit(1)
    
    # Initialize client
    try:
        client = FivetranAPIClient(api_key, api_secret)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to initialize Fivetran client: {e}")
        raise typer.Exit(1)
    
    # Get connector ID from config or parameter
    if not connector_id and config.exists():
        with open(config, 'r') as f:
            deployment_info = yaml.safe_load(f)
            connector_id = deployment_info.get("resources", {}).get("connector_id")
    
    if not connector_id:
        console.print("[yellow]No connector ID found. Listing all connectors...[/yellow]\n")
        _list_all_connectors(client)
        return
    
    # Get connector status
    with console.status(f"[bold green]Fetching status for connector {connector_id}..."):
        try:
            status_info = client.get_sync_status(connector_id)
            connector = client.get_connector(connector_id)
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to fetch status: {e}")
            raise typer.Exit(1)
    
    # Display status
    _display_connector_status(connector, status_info)


@status_app.command()
def list(
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Fivetran API key"),
    api_secret: Optional[str] = typer.Option(None, "--api-secret", help="Fivetran API secret"),
    group_id: Optional[str] = typer.Option(None, "--group", "-g", help="Filter by group ID"),
):
    """
    List all connectors.
    
    Example:
        5tran status list
        5tran status list --group abc123
    """
    # Get API credentials
    api_key = api_key or FIVETRAN_API_KEY or os.getenv("FIVETRAN_API_KEY")
    api_secret = api_secret or FIVETRAN_API_SECRET or os.getenv("FIVETRAN_API_SECRET")
    
    if not api_key or not api_secret:
        console.print("[red]Error:[/red] Fivetran API credentials not found")
        raise typer.Exit(1)
    
    # Initialize client
    try:
        client = FivetranAPIClient(api_key, api_secret)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to initialize Fivetran client: {e}")
        raise typer.Exit(1)
    
    _list_all_connectors(client, group_id)


def _display_connector_status(connector: dict, status_info: dict):
    """Display detailed connector status."""
    
    # Main status table
    status_table = Table(title="Connector Status", show_header=True, show_lines=True)
    status_table.add_column("Property", style="cyan", width=20)
    status_table.add_column("Value", style="white")
    
    # Get status colors
    setup_state = status_info.get("setup_state", "unknown")
    sync_state = status_info.get("sync_state", "unknown")
    
    setup_color = "green" if setup_state == "connected" else "yellow" if setup_state == "incomplete" else "red"
    sync_color = "green" if sync_state == "syncing" else "yellow"
    
    status_table.add_row("Connector ID", connector.get("id", "N/A"))
    status_table.add_row("Schema", connector.get("schema", "N/A"))
    status_table.add_row("Service", connector.get("service", "N/A"))
    status_table.add_row(
        "Setup State",
        f"[{setup_color}]{setup_state}[/{setup_color}]"
    )
    status_table.add_row(
        "Sync State",
        f"[{sync_color}]{sync_state}[/{sync_color}]"
    )
    status_table.add_row(
        "Update State",
        status_info.get("update_state", "N/A")
    )
    status_table.add_row(
        "Historical Sync",
        "Yes" if status_info.get("is_historical_sync") else "No"
    )
    status_table.add_row(
        "Last Success",
        status_info.get("succeeded_at", "Never")
    )
    status_table.add_row(
        "Last Failure",
        status_info.get("failed_at", "None") or "None"
    )
    status_table.add_row(
        "Sync Frequency",
        f"{connector.get('sync_frequency', 'N/A')} minutes"
    )
    
    console.print(status_table)
    
    # Show sync summary
    if setup_state == "connected":
        console.print("\n[green]✓ Connector is healthy and syncing[/green]")
    elif setup_state == "incomplete":
        console.print("\n[yellow]⚠ Connector setup incomplete - may need configuration[/yellow]")
    else:
        console.print("\n[red]✗ Connector has issues - check Fivetran dashboard[/red]")


def _list_all_connectors(client: FivetranAPIClient, group_id: Optional[str] = None):
    """List all connectors in a table."""
    
    try:
        connectors = client.list_connectors(group_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to list connectors: {e}")
        return
    
    if not connectors:
        console.print("[yellow]No connectors found[/yellow]")
        return
    
    table = Table(title=f"Connectors ({len(connectors)})", show_header=True)
    table.add_column("ID", style="cyan", width=20)
    table.add_column("Schema", style="white", width=20)
    table.add_column("Service", style="white", width=15)
    table.add_column("Status", style="white", width=15)
    table.add_column("Last Sync", style="white")
    
    for conn in connectors:
        status = conn.get("status", {})
        setup_state = status.get("setup_state", "unknown")
        
        status_color = "green" if setup_state == "connected" else "yellow" if setup_state == "incomplete" else "red"
        
        table.add_row(
            conn.get("id", "N/A")[:20],
            conn.get("schema", "N/A"),
            conn.get("service", "N/A"),
            f"[{status_color}]{setup_state}[/{status_color}]",
            conn.get("succeeded_at", "Never")
        )
    
    console.print(table)
    console.print(f"\n[dim]Use '5tran status check --connector-id ID' for detailed status[/dim]")


if __name__ == "__main__":
    status_app()


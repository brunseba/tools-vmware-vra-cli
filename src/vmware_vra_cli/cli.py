import click
import requests
from requests.auth import HTTPBasicAuth
import rich
import json
import os
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import keyring
import yaml

from vmware_vra_cli.api.catalog import CatalogClient
from vmware_vra_cli.auth import VRAAuthenticator, TokenManager
from vmware_vra_cli.config import get_config, save_login_config, config_manager
from vmware_vra_cli.commands.generic_catalog import schema_catalog
from vmware_vra_cli import __version__

console = Console()

def get_catalog_client(verbose: bool = False) -> CatalogClient:
    """Get configured catalog client with automatic token refresh."""
    config = get_config()
    token = TokenManager.get_access_token()
    
    # Try to refresh token if access token is not available or expired
    if not token:
        token = TokenManager.refresh_access_token(
            config["api_url"], 
            config["verify_ssl"]
        )
    
    if not token:
        console.print("[red]No valid authentication token found. Please run 'vra auth login' first.[/red]")
        raise click.Abort()
    
    return CatalogClient(
        base_url=config["api_url"],
        token=token,
        verify_ssl=config["verify_ssl"],
        verbose=verbose
    )

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'yaml']), 
              default='table', help='Output format')
@click.version_option(version=__version__, prog_name='vra-cli')
@click.pass_context
def main(ctx, verbose, output_format):
    """
    CLI tool to interact with VMware vRealize Automation 8 Service Catalog
    
    This tool provides comprehensive access to vRA 8 Service Catalog functionality
    including catalog items, deployments, and workflow operations.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['format'] = output_format

# Authentication commands
@main.group()
def auth():
    """Authentication operations."""
    pass

@auth.command()
@click.option('--username', prompt=True, help='Username for vRA access')
@click.option('--password', prompt=True, hide_input=True, help='Password for vRA access')
@click.option('--url', help='vRA server URL', default=lambda: get_config()["api_url"])
@click.option('--tenant', help='vRA tenant', default=lambda: get_config()["tenant"])
@click.option('--domain', help='Domain for multiple identity sources (optional)')
def login(username, password, url, tenant, domain):
    """
    Authenticate to vRA using the two-step procedure.
    
    This implements the official VMware vRA authentication process:
    1. Obtain refresh token from Identity Service API (valid for 90 days)
    2. Exchange refresh token for access token via IaaS API (valid for 8 hours)
    
    The URL, tenant, and domain parameters are saved to configuration for future use.
    """
    config = get_config()
    
    with console.status("[bold green]Authenticating..."):
        try:
            authenticator = VRAAuthenticator(url, config["verify_ssl"])
            tokens = authenticator.authenticate(username, password, domain)
            
            # Store tokens securely
            TokenManager.store_tokens(
                tokens['access_token'], 
                tokens['refresh_token']
            )
            
            # Save configuration parameters for future use
            save_login_config(api_url=url, tenant=tenant, domain=domain)
            
            console.print("[bold green]✅ Authentication successful![/bold green]")
            console.print("[green]🔑 Tokens saved securely[/green]")
            console.print(f"[cyan]💾 Configuration saved: {url}[/cyan]")
            if tenant:
                console.print(f"[cyan]🏢 Tenant: {tenant}[/cyan]")
            if domain:
                console.print(f"[cyan]🌐 Domain: {domain}[/cyan]")
            
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]❌ Authentication failed: {e}[/bold red]")
            raise click.Abort()

@auth.command()
def logout():
    """Clear stored authentication tokens."""
    try:
        TokenManager.clear_tokens()
        console.print("[green]✅ Logged out successfully[/green]")
    except Exception:
        console.print("[yellow]No stored credentials found[/yellow]")

@auth.command()
def status():
    """Check authentication status."""
    access_token = TokenManager.get_access_token()
    refresh_token = TokenManager.get_refresh_token()
    
    if access_token:
        console.print("[green]✅ Authenticated (Access token available)[/green]")
        if refresh_token:
            console.print("[green]🔄 Refresh token available for automatic renewal[/green]")
    elif refresh_token:
        console.print("[yellow]⚠️ Only refresh token available - will obtain new access token on next use[/yellow]")
    else:
        console.print("[red]❌ Not authenticated[/red]")

@auth.command()
def refresh():
    """Manually refresh the access token."""
    config = get_config()
    new_token = TokenManager.refresh_access_token(
        config["api_url"], 
        config["verify_ssl"]
    )
    
    if new_token:
        console.print("[green]✅ Access token refreshed successfully[/green]")
    else:
        console.print("[red]❌ Failed to refresh token. Please login again.[/red]")

# Configuration commands
@main.group()
def config():
    """Configuration management operations."""
    pass

# Add schema catalog commands
main.add_command(schema_catalog)

@config.command('show')
@click.pass_context
def show_config(ctx):
    """Show current configuration."""
    current_config = get_config()
    
    if ctx.obj['format'] == 'table':
        table = Table(title="VMware vRA CLI Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Source", style="yellow")
        
        # Check which values come from environment vs config file
        for key, value in current_config.items():
            env_key = f"VRA_{key.upper()}"
            if key == "api_url":
                env_key = "VRA_URL"
            
            source = "Default"
            if os.getenv(env_key):
                source = f"Environment ({env_key})"
            elif config_manager.config_file.exists():
                try:
                    with open(config_manager.config_file, 'r') as f:
                        file_config = json.load(f)
                    if key in file_config:
                        source = "Config file"
                except Exception:
                    pass
            
            # Mask sensitive or long values
            display_value = str(value) if value is not None else "Not set"
            if key == "domain" and not value:
                display_value = "Not set"
                
            table.add_row(key.replace('_', ' ').title(), display_value, source)
        
        console.print(table)
        console.print(f"\n[dim]Config file: {config_manager.config_file}[/dim]")
        
    elif ctx.obj['format'] == 'json':
        console.print(json.dumps(current_config, indent=2))
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump(current_config, default_flow_style=False))

@config.command('set')
@click.argument('key')
@click.argument('value')
def set_config_value(key, value):
    """Set a configuration value.
    
    Examples:
        vra config set api_url https://vra.company.com
        vra config set tenant mydomain.local
        vra config set verify_ssl false
    """
    # Handle boolean values
    if key == "verify_ssl":
        value = value.lower() == "true"
    elif key == "timeout":
        try:
            value = int(value)
        except ValueError:
            console.print(f"[red]❌ Invalid timeout value: {value}[/red]")
            raise click.Abort()
    
    config_manager.set_config_value(key, value)
    console.print(f"[green]✅ Configuration updated: {key} = {value}[/green]")
    console.print(f"[dim]Saved to: {config_manager.config_file}[/dim]")

@config.command('reset')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def reset_config(confirm):
    """Reset configuration to defaults."""
    if not confirm:
        if not click.confirm("Are you sure you want to reset all configuration to defaults?"):
            return
    
    config_manager.reset_config()
    console.print("[green]✅ Configuration reset to defaults[/green]")
    console.print(f"[dim]Config file removed: {config_manager.config_file}[/dim]")

@config.command('edit')
def edit_config():
    """Edit configuration file in default editor."""
    import subprocess
    
    # Ensure config file exists
    if not config_manager.config_file.exists():
        config_manager.save_config(config_manager.DEFAULT_CONFIG)
    
    editor = os.getenv('EDITOR', 'nano' if os.name != 'nt' else 'notepad')
    
    try:
        subprocess.run([editor, str(config_manager.config_file)], check=True)
        console.print(f"[green]✅ Configuration file edited[/green]")
        console.print(f"[dim]File: {config_manager.config_file}[/dim]")
    except subprocess.CalledProcessError:
        console.print(f"[red]❌ Failed to open editor: {editor}[/red]")
        console.print(f"[dim]You can manually edit: {config_manager.config_file}[/dim]")
    except FileNotFoundError:
        console.print(f"[red]❌ Editor not found: {editor}[/red]")
        console.print(f"[dim]Set EDITOR environment variable or manually edit: {config_manager.config_file}[/dim]")

# Service Catalog commands
@main.group()
def catalog():
    """Service Catalog operations."""
    pass

@catalog.command('list')
@click.option('--project', help='Filter by project ID')
@click.option('--page-size', type=int, default=100, help='Number of items per page (default: 100, max: 2000)')
@click.option('--first-page-only', is_flag=True, help='Fetch only the first page instead of all items')
@click.pass_context
def list_catalog_items(ctx, project, page_size, first_page_only):
    """List available catalog items.
    
    By default, this command fetches all catalog items across all pages.
    Use --first-page-only to limit to just the first page for faster results.
    """
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    status_msg = "[bold blue]Fetching catalog items..."  
    if not first_page_only:
        status_msg += " (all pages)"
    
    with console.status(status_msg):
        items = client.list_catalog_items(
            project_id=project, 
            page_size=page_size,
            fetch_all=not first_page_only
        )
    
    if ctx.obj['format'] == 'table':
        table_title = f"Service Catalog Items ({len(items)} items)"
        if first_page_only:
            table_title += " - First Page Only"
        
        table = Table(title=table_title)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Version", style="blue")
        
        for item in items:
            table.add_row(
                item.id,
                item.name,
                item.type.name,
                item.status or "N/A",
                item.version or "N/A"
            )
        
        console.print(table)
    elif ctx.obj['format'] == 'json':
        console.print(json.dumps([item.dict() for item in items], indent=2))
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump([item.dict() for item in items], default_flow_style=False))

@catalog.command('show')
@click.argument('item_id')
@click.pass_context
def show_catalog_item(ctx, item_id):
    """Show details of a specific catalog item."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold blue]Fetching catalog item {item_id}..."):
        item = client.get_catalog_item(item_id)
    
    if ctx.obj['format'] == 'table':
        table = Table(title=f"Catalog Item: {item.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("ID", item.id)
        table.add_row("Name", item.name)
        table.add_row("Type", item.type.name)
        table.add_row("Status", item.status or "N/A")
        table.add_row("Version", item.version or "N/A")
        table.add_row("Description", item.description or "N/A")
        
        console.print(table)
    else:
        data = item.dict()
        if ctx.obj['format'] == 'json':
            console.print(json.dumps(data, indent=2))
        elif ctx.obj['format'] == 'yaml':
            console.print(yaml.dump(data, default_flow_style=False))

@catalog.command('schema')
@click.argument('item_id')
@click.pass_context
def show_catalog_item_schema(ctx, item_id):
    """Show request schema for a catalog item."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold blue]Fetching schema for {item_id}..."):
        schema = client.get_catalog_item_schema(item_id)
    
    if ctx.obj['format'] == 'json':
        console.print(json.dumps(schema, indent=2))
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump(schema, default_flow_style=False))
    else:
        console.print(json.dumps(schema, indent=2))

@catalog.command('schema-export-all')
@click.option('--project', help='Filter by project ID')
@click.option('--output-dir', default='./schema_exports', help='Directory to save schema files (default: ./schema_exports)')
@click.option('--format', 'format_type', type=click.Choice(['json', 'yaml']), default='json', help='Output format')
@click.pass_context
def export_all_schemas(ctx, project, output_dir, format_type):
    """Export all catalog item schemas to files."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    status_msg = "[bold blue]Exporting all catalog item schemas..."
    if project:
        status_msg += f" (project: {project})"
    
    with console.status(status_msg):
        export_summary = client.export_catalog_schemas(project_id=project, output_dir=output_dir, format_type=format_type)
    
    # Display summary
    console.print("\n[green]✅ Schema export completed successfully![/green]")
    console.print(f"[cyan]Output directory: {output_dir}[/cyan]")
    console.print(f"[cyan]Files created: {export_summary['files_created']}[/cyan]")
    
    console.print(f"\n[bold]Export Statistics:[/bold]")
    console.print(f"  Total catalog items: {export_summary['statistics']['total_catalog_items']}")
    console.print(f"  Items with schemas exported: {export_summary['statistics']['successful_exports']}")
    console.print(f"  Items failed to export: {export_summary['statistics']['failed_exports']}")
    console.print(f"  Items without schemas: {export_summary['statistics']['items_without_schema']}")
    
    if export_summary['statistics']['failed_exports'] > 0:
        console.print("\n[red]Failed export details:[/red]")
        for failure in export_summary['failed_items']:
            console.print(f"  - {failure['name']} (ID: {failure['id']}): {failure['error']}")

    if export_summary['statistics']['items_without_schema'] > 0:
        console.print("\n[yellow]Items without schema details:[/yellow]")
        for item in export_summary['items_without_schema']:
            console.print(f"  - {item['name']} (ID: {item['id']}): {item['reason']}")

@catalog.command('request')
@click.argument('item_id')
@click.option('--inputs', help='Input parameters as JSON string')
@click.option('--inputs-file', help='Input parameters from YAML/JSON file')
@click.option('--project', required=True, help='Project ID for the request')
@click.option('--reason', help='Reason for the request')
@click.option('--name', help='Deployment name')
@click.pass_context
def request_catalog_item(ctx, item_id, inputs, inputs_file, project, reason, name):
    """Request a catalog item."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    # Parse inputs
    inputs_dict = {}
    if inputs:
        inputs_dict = json.loads(inputs)
    elif inputs_file:
        with open(inputs_file, 'r') as f:
            if inputs_file.endswith('.yaml') or inputs_file.endswith('.yml'):
                inputs_dict = yaml.safe_load(f)
            else:
                inputs_dict = json.load(f)
    
    if name:
        inputs_dict['deploymentName'] = name
    
    with console.status(f"[bold blue]Requesting catalog item {item_id}..."):
        result = client.request_catalog_item(item_id, inputs_dict, project, reason)
    
    console.print(f"[green]✅ Request submitted successfully![/green]")
    console.print(f"[cyan]Deployment ID: {result.get('deploymentId')}[/cyan]")
    
    if result.get('requestId'):
        console.print(f"[cyan]Request ID: {result.get('requestId')}[/cyan]")

# Deployment commands
@main.group()
def deployment():
    """Deployment operations."""
    pass

@deployment.command('list')
@click.option('--project', help='Filter by project ID')
@click.option('--status', help='Filter by status')
@click.option('--page-size', type=int, default=100, help='Number of items per page (default: 100, max: 2000)')
@click.option('--first-page-only', is_flag=True, help='Fetch only the first page instead of all items')
@click.pass_context
def list_deployments(ctx, project, status, page_size, first_page_only):
    """List deployments.
    
    By default, this command fetches all deployments across all pages.
    Use --first-page-only to limit to just the first page for faster results.
    """
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    status_msg = "[bold blue]Fetching deployments..."
    if not first_page_only:
        status_msg += " (all pages)"
    
    with console.status(status_msg):
        deployments = client.list_deployments(
            project_id=project, 
            status=status,
            page_size=page_size,
            fetch_all=not first_page_only
        )
    
    if ctx.obj['format'] == 'table':
        table_title = f"Deployments ({len(deployments)} items)"
        if first_page_only:
            table_title += " - First Page Only"
        
        table = Table(title=table_title)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Project", style="magenta")
        table.add_column("Created", style="blue")
        
        for deployment in deployments:
            table.add_row(
                deployment.get('id', 'N/A'),
                deployment.get('name', 'N/A'),
                deployment.get('status', 'N/A'),
                deployment.get('projectId', 'N/A'),
                deployment.get('createdAt', 'N/A')
            )
        
        console.print(table)
    elif ctx.obj['format'] == 'json':
        console.print(json.dumps(deployments, indent=2))
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump(deployments, default_flow_style=False))

@deployment.command('show')
@click.argument('deployment_id')
@click.pass_context
def show_deployment(ctx, deployment_id):
    """Show deployment details."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold blue]Fetching deployment {deployment_id}..."):
        deployment = client.get_deployment(deployment_id)
    
    if ctx.obj['format'] == 'json':
        console.print(json.dumps(deployment, indent=2))
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump(deployment, default_flow_style=False))
    else:
        table = Table(title=f"Deployment: {deployment.get('name', 'N/A')}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in deployment.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, indent=2)
            table.add_row(str(key), str(value))
        
        console.print(table)

@deployment.command('delete')
@click.argument('deployment_id')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete_deployment(ctx, deployment_id, confirm):
    """Delete a deployment."""
    if not confirm:
        if not click.confirm(f"Are you sure you want to delete deployment {deployment_id}?"):
            return
    
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold red]Deleting deployment {deployment_id}..."):
        result = client.delete_deployment(deployment_id)
    
    console.print(f"[green]✅ Deployment {deployment_id} deletion initiated[/green]")

@deployment.command('resources')
@click.argument('deployment_id')
@click.pass_context
def show_deployment_resources(ctx, deployment_id):
    """Show deployment resources."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold blue]Fetching resources for deployment {deployment_id}..."):
        resources = client.get_deployment_resources(deployment_id)
    
    if ctx.obj['format'] == 'table':
        table = Table(title=f"Resources for Deployment {deployment_id}")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="magenta")
        
        for resource in resources:
            table.add_row(
                resource.get('id', 'N/A'),
                resource.get('name', 'N/A'),
                resource.get('type', 'N/A'),
                resource.get('status', 'N/A')
            )
        
        console.print(table)
    elif ctx.obj['format'] == 'json':
        console.print(json.dumps(resources, indent=2))
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump(resources, default_flow_style=False))

@deployment.command('export-all')
@click.option('--project', help='Filter deployments by project ID')
@click.option('--output-dir', default='./exports', help='Directory to save export files (default: ./exports)')
@click.option('--include-resources', is_flag=True, help='Include resource details for each deployment (slower)')
@click.option('--no-unsynced', is_flag=True, help='Exclude deployments not linked to catalog items')
@click.pass_context
def export_all_deployments(ctx, project, output_dir, include_resources, no_unsynced):
    """Export all deployments grouped by catalog item to separate JSON files.
    
    This command fetches all deployments and groups them by their associated
    catalog item ID, then exports each group to a separate JSON file in the
    specified output directory. This is useful for backup, analysis, or
    migration purposes.
    
    Each catalog item's deployments are saved to a file named:
    {catalog_item_name}_{catalog_item_id}.json
    
    Deployments that cannot be linked to catalog items are saved to:
    unsynced_deployments.json (unless --no-unsynced is specified)
    
    An export summary with statistics is saved to:
    export_summary.json
    
    Examples:
    
        # Export all deployments with default settings
        vmware-vra deployment export-all
        
        # Export to specific directory with resource details
        vmware-vra deployment export-all --output-dir /path/to/exports --include-resources
        
        # Export for specific project, excluding unsynced deployments
        vmware-vra deployment export-all --project abc123 --no-unsynced
    """
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    include_unsynced = not no_unsynced
    
    # Progress message
    status_parts = ["Exporting deployments grouped by catalog item"]
    if project:
        status_parts.append(f"(project: {project})")
    if include_resources:
        status_parts.append("(including resources)")
    
    status_msg = f"[bold blue]{' '.join(status_parts)}..."
    
    try:
        with console.status(status_msg):
            export_summary = client.export_deployments_by_catalog_item(
                project_id=project,
                output_dir=output_dir,
                include_resources=include_resources,
                include_unsynced=include_unsynced
            )
        
        # Display success summary
        console.print(f"\n[green]✅ Export completed successfully![/green]")
        console.print(f"[cyan]Output directory: {output_dir}[/cyan]")
        console.print(f"[cyan]Files created: {export_summary['files_created']}[/cyan]")
        
        stats = export_summary['statistics']
        console.print(f"\n[bold]Export Statistics:[/bold]")
        console.print(f"  Total deployments: {stats['total_deployments']}")
        console.print(f"  Synced deployments: {stats['synced_deployments']}")
        console.print(f"  Unsynced deployments: {stats['unsynced_deployments']}")
        console.print(f"  Catalog items with deployments: {stats['catalog_items_with_deployments']}")
        console.print(f"  Total catalog items: {stats['total_catalog_items']}")
        
        # Display file list
        if export_summary['exported_files']:
            console.print(f"\n[bold]Exported Files:[/bold]")
            
            # Create table for exported files
            files_table = Table()
            files_table.add_column("Filename", style="cyan")
            files_table.add_column("Catalog Item", style="green")
            files_table.add_column("Deployments", style="yellow", justify="right")
            
            for file_info in export_summary['exported_files']:
                files_table.add_row(
                    file_info['filename'],
                    file_info['catalog_item_name'],
                    str(file_info['deployment_count'])
                )
            
            console.print(files_table)
        
        # Display additional info if including resources
        if include_resources:
            console.print(f"\n[yellow]ℹ️  Resource details included - this may have taken longer to complete[/yellow]")
        
        # Display info about unsynced deployments
        if not include_unsynced and stats['unsynced_deployments'] > 0:
            console.print(f"\n[yellow]ℹ️  {stats['unsynced_deployments']} unsynced deployments were excluded (use without --no-unsynced to include them)[/yellow]")
        elif include_unsynced and stats['unsynced_deployments'] > 0:
            console.print(f"\n[yellow]ℹ️  {stats['unsynced_deployments']} unsynced deployments were included in unsynced_deployments.json[/yellow]")
        
        console.print(f"\n[blue]💡 View export_summary.json for detailed export information[/blue]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Export failed: {str(e)}[/red]")
        if ctx.obj['verbose']:
            import traceback
            console.print(f"[red]Full error: {traceback.format_exc()}[/red]")
        raise click.Abort()

# Tag commands
@main.group()
def tag():
    """Tag management operations."""
    pass

@tag.command('list')
@click.option('--search', help='Search term to filter tags')
@click.option('--page-size', type=int, default=100, help='Number of items per page (default: 100, max: 2000)')
@click.option('--first-page-only', is_flag=True, help='Fetch only the first page instead of all items')
@click.pass_context
def list_tags(ctx, search, page_size, first_page_only):
    """List available tags.
    
    By default, this command fetches all tags across all pages.
    Use --first-page-only to limit to just the first page for faster results.
    """
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    status_msg = "[bold blue]Fetching tags..."
    if not first_page_only:
        status_msg += " (all pages)"
    
    with console.status(status_msg):
        tags = client.list_tags(
            search=search,
            page_size=page_size,
            fetch_all=not first_page_only
        )
    
    if ctx.obj['format'] == 'table':
        table_title = f"Tags ({len(tags)} items)"
        if first_page_only:
            table_title += " - First Page Only"
        
        table = Table(title=table_title)
        table.add_column("ID", style="cyan")
        table.add_column("Key", style="green")
        table.add_column("Value", style="yellow")
        table.add_column("Description", style="magenta")
        table.add_column("Created By", style="blue")
        
        for tag in tags:
            table.add_row(
                tag.id,
                tag.key,
                tag.value or "N/A",
                tag.description or "N/A",
                tag.created_by or "N/A"
            )
        
        console.print(table)
    elif ctx.obj['format'] == 'json':
        console.print(json.dumps([tag.dict() for tag in tags], indent=2))
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump([tag.dict() for tag in tags], default_flow_style=False))

@tag.command('show')
@click.argument('tag_id')
@click.pass_context
def show_tag(ctx, tag_id):
    """Show details of a specific tag."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold blue]Fetching tag {tag_id}..."):
        tag = client.get_tag(tag_id)
    
    if ctx.obj['format'] == 'table':
        table = Table(title=f"Tag: {tag.key}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("ID", tag.id)
        table.add_row("Key", tag.key)
        table.add_row("Value", tag.value or "N/A")
        table.add_row("Description", tag.description or "N/A")
        table.add_row("Created At", tag.created_at or "N/A")
        table.add_row("Updated At", tag.updated_at or "N/A")
        table.add_row("Created By", tag.created_by or "N/A")
        table.add_row("Updated By", tag.updated_by or "N/A")
        
        console.print(table)
    else:
        data = tag.dict()
        if ctx.obj['format'] == 'json':
            console.print(json.dumps(data, indent=2))
        elif ctx.obj['format'] == 'yaml':
            console.print(yaml.dump(data, default_flow_style=False))

@tag.command('create')
@click.argument('key')
@click.option('--value', help='Tag value (optional)')
@click.option('--description', help='Tag description (optional)')
@click.pass_context
def create_tag(ctx, key, value, description):
    """Create a new tag."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold blue]Creating tag {key}..."):
        tag = client.create_tag(key=key, value=value, description=description)
    
    console.print(f"[green]✅ Tag created successfully![/green]")
    console.print(f"[cyan]Tag ID: {tag.id}[/cyan]")
    console.print(f"[cyan]Key: {tag.key}[/cyan]")
    if tag.value:
        console.print(f"[cyan]Value: {tag.value}[/cyan]")
    if tag.description:
        console.print(f"[cyan]Description: {tag.description}[/cyan]")

@tag.command('update')
@click.argument('tag_id')
@click.option('--key', help='New tag key')
@click.option('--value', help='New tag value')
@click.option('--description', help='New tag description')
@click.pass_context
def update_tag(ctx, tag_id, key, value, description):
    """Update an existing tag."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold blue]Updating tag {tag_id}..."):
        tag = client.update_tag(tag_id=tag_id, key=key, value=value, description=description)
    
    console.print(f"[green]✅ Tag updated successfully![/green]")
    console.print(f"[cyan]Tag ID: {tag.id}[/cyan]")
    console.print(f"[cyan]Key: {tag.key}[/cyan]")
    if tag.value:
        console.print(f"[cyan]Value: {tag.value}[/cyan]")
    if tag.description:
        console.print(f"[cyan]Description: {tag.description}[/cyan]")

@tag.command('delete')
@click.argument('tag_id')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete_tag(ctx, tag_id, confirm):
    """Delete a tag."""
    if not confirm:
        if not click.confirm(f"Are you sure you want to delete tag {tag_id}?"):
            return
    
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold red]Deleting tag {tag_id}..."):
        result = client.delete_tag(tag_id)
    
    if result:
        console.print(f"[green]✅ Tag {tag_id} deleted successfully[/green]")
    else:
        console.print(f"[red]❌ Failed to delete tag {tag_id}[/red]")

@tag.command('assign')
@click.argument('resource_id')
@click.argument('tag_id')
@click.option('--resource-type', type=click.Choice(['deployment', 'catalog-item']), 
              default='deployment', help='Type of resource to tag')
@click.pass_context
def assign_tag(ctx, resource_id, tag_id, resource_type):
    """Assign a tag to a resource."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold blue]Assigning tag {tag_id} to {resource_type} {resource_id}..."):
        result = client.assign_tag_to_resource(resource_id, tag_id, resource_type)
    
    if result:
        console.print(f"[green]✅ Tag assigned successfully![/green]")
        console.print(f"[cyan]Resource: {resource_type} {resource_id}[/cyan]")
        console.print(f"[cyan]Tag: {tag_id}[/cyan]")
    else:
        console.print(f"[red]❌ Failed to assign tag[/red]")

@tag.command('remove')
@click.argument('resource_id')
@click.argument('tag_id')
@click.option('--resource-type', type=click.Choice(['deployment', 'catalog-item']), 
              default='deployment', help='Type of resource to untag')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def remove_tag(ctx, resource_id, tag_id, resource_type, confirm):
    """Remove a tag from a resource."""
    if not confirm:
        if not click.confirm(f"Are you sure you want to remove tag {tag_id} from {resource_type} {resource_id}?"):
            return
    
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold blue]Removing tag {tag_id} from {resource_type} {resource_id}..."):
        result = client.remove_tag_from_resource(resource_id, tag_id, resource_type)
    
    if result:
        console.print(f"[green]✅ Tag removed successfully![/green]")
        console.print(f"[cyan]Resource: {resource_type} {resource_id}[/cyan]")
        console.print(f"[cyan]Tag: {tag_id}[/cyan]")
    else:
        console.print(f"[red]❌ Failed to remove tag[/red]")

@tag.command('resource-tags')
@click.argument('resource_id')
@click.option('--resource-type', type=click.Choice(['deployment', 'catalog-item']), 
              default='deployment', help='Type of resource')
@click.pass_context
def show_resource_tags(ctx, resource_id, resource_type):
    """Show tags assigned to a resource."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    with console.status(f"[bold blue]Fetching tags for {resource_type} {resource_id}..."):
        tags = client.get_resource_tags(resource_id, resource_type)
    
    if ctx.obj['format'] == 'table':
        table = Table(title=f"Tags for {resource_type.title()} {resource_id}")
        table.add_column("ID", style="cyan")
        table.add_column("Key", style="green")
        table.add_column("Value", style="yellow")
        table.add_column("Description", style="magenta")
        
        for tag in tags:
            table.add_row(
                tag.id,
                tag.key,
                tag.value or "N/A",
                tag.description or "N/A"
            )
        
        console.print(table)
    elif ctx.obj['format'] == 'json':
        console.print(json.dumps([tag.dict() for tag in tags], indent=2))
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump([tag.dict() for tag in tags], default_flow_style=False))

# Report commands
@main.group()
def report():
    """Generate reports and analytics."""
    pass

@report.command('activity-timeline')
@click.option('--project', help='Filter by project ID')
@click.option('--days-back', type=int, default=30, help='Days back for activity timeline (default: 30)')
@click.option('--group-by', type=click.Choice(['day', 'week', 'month', 'year']), 
              default='day', help='Group results by time period (default: day)')
@click.option('--statuses', help='Comma-separated list of statuses to include (default: all)',
              default='CREATE_SUCCESSFUL,UPDATE_SUCCESSFUL,SUCCESSFUL,CREATE_FAILED,UPDATE_FAILED,FAILED,CREATE_INPROGRESS,UPDATE_INPROGRESS,INPROGRESS')
@click.pass_context
def activity_timeline_report(ctx, project, days_back, group_by, statuses):
    """Generate an activity timeline for service catalog items.
    
    This timeline provides a historical view of deployment activities over a specified period,
    allowing you to see patterns, peak activity periods, and trends.
    
    Group options:
    - day: Daily activity (default)
    - week: Weekly activity (shows week number and year)
    - month: Monthly activity (shows month and year) 
    - year: Yearly activity (shows annual totals)
    """
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    console.print("[bold blue]📈 Generating Activity Timeline Report...[/bold blue]")
    
    # Convert status string to list
    include_statuses = [status.strip().upper() for status in statuses.split(',')]
    
    with console.status("[bold green]Analyzing activity timeline..."):
        timeline_data = client.get_activity_timeline(
            project_id=project, 
            days_back=days_back, 
            include_statuses=include_statuses,
            group_by=group_by
        )
    
    # Display results
    if ctx.obj['format'] == 'table':
        # Summary statistics
        summary = timeline_data['summary']
        console.print("\n[bold green]📊 Summary Statistics[/bold green]")
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        for key, value in summary.items():
            summary_table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(summary_table)
        
        # Activity table with dynamic title based on grouping
        group_titles = {
            'day': '📅 Daily Activity',
            'week': '📊 Weekly Activity', 
            'month': '🗓️ Monthly Activity',
            'year': '🗓️ Yearly Activity'
        }
        
        period_titles = {
            'day': 'Daily Deployment Activity',
            'week': 'Weekly Deployment Activity',
            'month': 'Monthly Deployment Activity', 
            'year': 'Yearly Deployment Activity'
        }
        
        period_labels = {
            'day': 'Date',
            'week': 'Week',
            'month': 'Month',
            'year': 'Year'
        }
        
        console.print(f"\n[bold green]{group_titles[group_by]}[/bold green]")
        activity_table = Table(title=period_titles[group_by])
        activity_table.add_column(period_labels[group_by], style="blue")
        activity_table.add_column("Deployments", style="cyan", justify="right")
        activity_table.add_column("Success", style="green", justify="right")
        activity_table.add_column("Failed", style="red", justify="right")
        activity_table.add_column("In Progress", style="yellow", justify="right")
        activity_table.add_column("Unique Items", style="magenta", justify="right")
        activity_table.add_column("Unique Projects", style="white", justify="right")
        
        for period, data in sorted(timeline_data['period_activity'].items()):
            activity_table.add_row(
                period,
                str(data['total_deployments']),
                str(data['successful_deployments']),
                str(data['failed_deployments']),
                str(data['in_progress_deployments']),
                str(data['unique_catalog_items']),
                str(data['unique_projects'])
            )
        
        console.print(activity_table)
        
    elif ctx.obj['format'] == 'json':
        console.print(json.dumps(timeline_data, indent=2))
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump(timeline_data, default_flow_style=False))

@report.command('catalog-usage')
@click.option('--project', help='Filter by project ID')
@click.option('--include-zero', is_flag=True, help='Include catalog items with zero deployments')
@click.option('--sort-by', type=click.Choice(['deployments', 'resources', 'name']), 
              default='deployments', help='Sort results by field')
@click.option('--detailed-resources', is_flag=True, 
              help='Fetch exact resource counts (slower but more accurate)')
@click.pass_context
def catalog_usage_report(ctx, project, include_zero, sort_by, detailed_resources):
    """Generate a usage report for service catalog items.
    
    This report shows:
    - All catalog items in the specified project (or all projects)
    - Number of deployments created from each catalog item
    - Total number of resources created from each catalog item
    - Success rate and other deployment statistics
    
    By default, only catalog items with at least one deployment are shown.
    Use --include-zero to show all catalog items.
    Use --detailed-resources to fetch exact resource counts (slower).
    """
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    console.print("[bold blue]📊 Generating Service Catalog Usage Report...[/bold blue]")
    
    if detailed_resources:
        console.print("[yellow]⚠️  Detailed resource counting enabled - this may take longer[/yellow]")
    
    with console.status("[bold green]Analyzing catalog usage statistics..."):
        usage_stats = client.get_catalog_usage_stats(
            project_id=project, 
            fetch_resource_counts=detailed_resources
        )
        
        # Also get total deployment count for accurate summary
        all_deployments = client.list_deployments(project_id=project)
    
    # Filter out zero deployments unless requested
    if not include_zero:
        usage_stats = [stats for stats in usage_stats if stats['deployment_count'] > 0]
    
    # Sort results
    if sort_by == 'deployments':
        usage_stats.sort(key=lambda x: x['deployment_count'], reverse=True)
    elif sort_by == 'resources':
        usage_stats.sort(key=lambda x: x['resource_count'], reverse=True)
    elif sort_by == 'name':
        usage_stats.sort(key=lambda x: x['catalog_item'].name.lower())
        
    # Display results
    if ctx.obj['format'] == 'table':
        # Summary statistics
        catalog_deployments = sum(stat['deployment_count'] for stat in usage_stats)
        catalog_resources = sum(stat['resource_count'] for stat in usage_stats)
        total_items = len(usage_stats)
        active_items = len([s for s in usage_stats if s['deployment_count'] > 0])
        
        # Get original stats before filtering for accurate totals
        original_usage_stats = client.get_catalog_usage_stats(
            project_id=project, 
            fetch_resource_counts=False  # Use fast estimation for totals
        )
        total_catalog_deployments = sum(stat['deployment_count'] for stat in original_usage_stats)
        total_catalog_items = len(original_usage_stats)
        
        console.print("\n[bold green]📈 Summary Statistics[/bold green]")
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        summary_table.add_column("Note", style="dim")
        
        summary_table.add_row("Total Catalog Items", str(total_catalog_items), "All items in catalog")
        summary_table.add_row("Active Items (with deployments)", str(len([s for s in original_usage_stats if s['deployment_count'] > 0])), "Items with ≥1 deployment")
        summary_table.add_row("", "", "")
        summary_table.add_row("[bold]System-wide Totals[/bold]", "[bold]Count[/bold]", "[bold]Description[/bold]")
        summary_table.add_row("Total Deployments (all)", str(len(all_deployments)), "All deployments in vRA")
        summary_table.add_row("Catalog-linked Deployments", str(total_catalog_deployments), "Can match to catalog items")
        summary_table.add_row("Unlinked Deployments", str(len(all_deployments) - total_catalog_deployments), "Cannot match to catalog items")
        summary_table.add_row("", "", "")
        summary_table.add_row("[bold]Table Display[/bold]", "[bold]Count[/bold]", "[bold]Description[/bold]")
        summary_table.add_row("Items Shown Below", str(total_items), "After filtering" if not include_zero else "All items")
        summary_table.add_row("Deployments Shown Below", str(catalog_deployments), "Sum of table deployment column")
        summary_table.add_row("Resources Shown Below", str(catalog_resources), "Sum of table resource column")
        if active_items > 0:
            avg_deployments = catalog_deployments / active_items if not include_zero else total_catalog_deployments / len([s for s in original_usage_stats if s['deployment_count'] > 0])
            summary_table.add_row("Avg Deployments per Active Item", f"{avg_deployments:.1f}")
        
        console.print(summary_table)
        
        # Add verification note
        if catalog_deployments != total_catalog_deployments and not include_zero:
            console.print(f"\n[yellow]💡 Note: The table below shows {catalog_deployments} deployments from {total_items} filtered catalog items.")
            console.print(f"[yellow]   {total_catalog_deployments - catalog_deployments} additional deployments come from {total_catalog_items - total_items} catalog items with zero deployments (use --include-zero to see all).[/yellow]")
        elif catalog_deployments == total_catalog_deployments:
            console.print(f"\n[green]✅ All {total_catalog_deployments} catalog-linked deployments are shown in the table below.[/green]")
        
        # Detailed table
        console.print("\n[bold green]📋 Detailed Usage Report[/bold green]")
        
        table = Table(title="Service Catalog Usage Report")
        table.add_column("Catalog Item", style="green", width=30)
        table.add_column("Type", style="yellow", width=15)
        table.add_column("Deployments", style="cyan", justify="right")
        table.add_column("Resources", style="magenta", justify="right")
        table.add_column("Success", style="green", justify="right")
        table.add_column("Failed", style="red", justify="right")
        table.add_column("In Progress", style="yellow", justify="right")
        table.add_column("Success Rate", style="blue", justify="right")
        
        for stat in usage_stats:
            item = stat['catalog_item']
            success_rate_str = f"{stat['success_rate']:.1f}%" if stat['deployment_count'] > 0 else "N/A"
            
            table.add_row(
                item.name[:30] + "..." if len(item.name) > 30 else item.name,
                item.type.name.replace("com.vmw.", "").replace("vro.workflow", "Workflow").replace("blueprint", "Blueprint"),
                str(stat['deployment_count']),
                str(stat['resource_count']),
                str(stat['success_count']),
                str(stat['failed_count']),
                str(stat['in_progress_count']),
                success_rate_str
            )
        
        console.print(table)
        
    elif ctx.obj['format'] == 'json':
        # Get original stats for accurate totals in JSON output
        original_usage_stats = client.get_catalog_usage_stats(
            project_id=project, 
            fetch_resource_counts=False
        )
        
        # Convert to JSON-serializable format
        json_data = {
            'summary': {
                'total_catalog_items': len(original_usage_stats),
                'active_items': len([s for s in original_usage_stats if s['deployment_count'] > 0]),
                'total_deployments_system_wide': len(all_deployments),
                'catalog_linked_deployments': sum(stat['deployment_count'] for stat in original_usage_stats),
                'unlinked_deployments': len(all_deployments) - sum(stat['deployment_count'] for stat in original_usage_stats),
                'showing_items': len(usage_stats),
                'showing_deployments': sum(stat['deployment_count'] for stat in usage_stats),
                'total_resources': sum(stat['resource_count'] for stat in usage_stats)
            },
            'catalog_items': [
                {
                    'id': stat['catalog_item'].id,
                    'name': stat['catalog_item'].name,
                    'type': stat['catalog_item'].type.name,
                    'deployment_count': stat['deployment_count'],
                    'resource_count': stat['resource_count'],
                    'success_count': stat['success_count'],
                    'failed_count': stat['failed_count'],
                    'in_progress_count': stat['in_progress_count'],
                    'success_rate': stat['success_rate'],
                    'status_breakdown': stat['status_counts']
                }
                for stat in usage_stats
            ]
        }
        console.print(json.dumps(json_data, indent=2))
    
    elif ctx.obj['format'] == 'yaml':
        # Get original stats for accurate totals in YAML output  
        original_usage_stats = client.get_catalog_usage_stats(
            project_id=project, 
            fetch_resource_counts=False
        )
        
        # Convert to YAML format
        yaml_data = {
            'summary': {
                'total_catalog_items': len(original_usage_stats),
                'active_items': len([s for s in original_usage_stats if s['deployment_count'] > 0]),
                'total_deployments_system_wide': len(all_deployments),
                'catalog_linked_deployments': sum(stat['deployment_count'] for stat in original_usage_stats),
                'unlinked_deployments': len(all_deployments) - sum(stat['deployment_count'] for stat in original_usage_stats),
                'showing_items': len(usage_stats),
                'showing_deployments': sum(stat['deployment_count'] for stat in usage_stats),
                'total_resources': sum(stat['resource_count'] for stat in usage_stats)
            },
            'catalog_items': [
                {
                    'id': stat['catalog_item'].id,
                    'name': stat['catalog_item'].name,
                    'type': stat['catalog_item'].type.name,
                    'deployment_count': stat['deployment_count'],
                    'resource_count': stat['resource_count'],
                    'success_count': stat['success_count'],
                    'failed_count': stat['failed_count'],
                    'in_progress_count': stat['in_progress_count'],
                    'success_rate': round(stat['success_rate'], 1),
                    'status_breakdown': stat['status_counts']
                }
                for stat in usage_stats
            ]
        }
        console.print(yaml.dump(yaml_data, default_flow_style=False))

@report.command('resources-usage')
@click.option('--project', help='Filter by project ID')
@click.option('--detailed-resources', is_flag=True, default=True,
              help='Fetch detailed resource information (enabled by default, use --no-detailed-resources to disable)')
@click.option('--no-detailed-resources', is_flag=True,
              help='Skip detailed resource fetching for faster execution')
@click.option('--sort-by', type=click.Choice(['deployment-name', 'catalog-item', 'resource-count', 'status']),
              default='catalog-item', help='Sort deployments by field (default: catalog-item)')
@click.option('--group-by', type=click.Choice(['catalog-item', 'resource-type', 'deployment-status']),
              default='catalog-item', help='Group results by field (default: catalog-item)')
@click.pass_context
def resources_usage_report(ctx, project, detailed_resources, no_detailed_resources, sort_by, group_by):
    """Generate a consolidated resources usage report across all deployments.
    
    This report provides a comprehensive view of all resources existing in each deployment,
    showing resource types, counts, states, and their relationship to catalog items.
    
    The report includes:
    - Total resource counts by type and status
    - Resource breakdown per deployment
    - Catalog item resource utilization
    - Unlinked deployments and their resources
    
    Examples:
    
        # Basic resources usage report
        vra report resources-usage
        
        # Fast report without detailed resource fetching
        vra report resources-usage --no-detailed-resources
        
        # Report for specific project, grouped by resource type
        vra report resources-usage --project abc123 --group-by resource-type
        
        # Detailed report sorted by resource count
        vra report resources-usage --sort-by resource-count --detailed-resources
    """
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    # Handle conflicting flags
    if no_detailed_resources:
        detailed_resources = False
    
    console.print("[bold blue]📊 Generating Resources Usage Report...[/bold blue]")
    
    if detailed_resources:
        console.print("[yellow]⚠️  Detailed resource fetching enabled - this may take longer for many deployments[/yellow]")
    else:
        console.print("[cyan]💨 Using fast mode - resource counts will be estimated[/cyan]")
    
    with console.status("[bold green]Analyzing resource usage across all deployments..."):
        report_data = client.get_resources_usage_report(
            project_id=project,
            include_detailed_resources=detailed_resources
        )
    
    # Display results based on format
    if ctx.obj['format'] == 'table':
        # Summary statistics
        summary = report_data['summary']
        console.print("\n[bold green]📈 Resource Usage Summary[/bold green]")
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        summary_table.add_column("Note", style="dim")
        
        summary_table.add_row("Total Deployments", str(summary['total_deployments']), "All deployments in scope")
        summary_table.add_row("Linked Deployments", str(summary['linked_deployments']), "Linked to catalog items")
        summary_table.add_row("Unlinked Deployments", str(summary['unlinked_deployments']), "Cannot link to catalog items")
        summary_table.add_row("", "", "")
        summary_table.add_row("Total Resources", str(summary['total_resources']), "Across all deployments")
        summary_table.add_row("Unique Resource Types", str(summary['unique_resource_types']), "Different resource types found")
        summary_table.add_row("Unique Catalog Items", str(summary['unique_catalog_items']), "Catalog items with deployments")
        
        if summary['total_deployments'] > 0:
            avg_resources = summary['total_resources'] / summary['total_deployments']
            summary_table.add_row("Avg Resources per Deployment", f"{avg_resources:.1f}", "Average resource density")
        
        console.print(summary_table)
        
        # Resource type breakdown
        if summary['resource_types']:
            console.print("\n[bold green]🔧 Resource Type Breakdown[/bold green]")
            resource_table = Table(title="Resources by Type")
            resource_table.add_column("Resource Type", style="yellow")
            resource_table.add_column("Count", style="cyan", justify="right")
            resource_table.add_column("Percentage", style="green", justify="right")
            
            # Sort resource types by count
            sorted_types = sorted(summary['resource_types'].items(), key=lambda x: x[1], reverse=True)
            
            for resource_type, count in sorted_types:
                percentage = (count / summary['total_resources']) * 100 if summary['total_resources'] > 0 else 0
                resource_table.add_row(
                    resource_type,
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(resource_table)
        
        # Resource state breakdown
        if summary['resource_states']:
            console.print("\n[bold green]📊 Resource State Breakdown[/bold green]")
            state_table = Table(title="Resources by State")
            state_table.add_column("Resource State", style="magenta")
            state_table.add_column("Count", style="cyan", justify="right")
            state_table.add_column("Percentage", style="green", justify="right")
            
            # Sort resource states by count
            sorted_states = sorted(summary['resource_states'].items(), key=lambda x: x[1], reverse=True)
            
            for resource_state, count in sorted_states:
                percentage = (count / summary['total_resources']) * 100 if summary['total_resources'] > 0 else 0
                state_table.add_row(
                    resource_state,
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(state_table)
        
        # Display deployment details based on grouping
        if group_by == 'catalog-item':
            console.print("\n[bold green]📋 Resources by Catalog Item[/bold green]")
            
            if report_data['catalog_item_summary']:
                catalog_table = Table(title="Catalog Item Resource Summary")
                catalog_table.add_column("Catalog Item", style="green", width=30)
                catalog_table.add_column("Type", style="yellow", width=15)
                catalog_table.add_column("Deployments", style="cyan", justify="right")
                catalog_table.add_column("Total Resources", style="magenta", justify="right")
                catalog_table.add_column("Avg per Deployment", style="blue", justify="right")
                catalog_table.add_column("Top Resource Type", style="white")
                
                # Sort catalog items by total resources
                sorted_catalog_items = sorted(
                    report_data['catalog_item_summary'].items(),
                    key=lambda x: x[1]['total_resources'],
                    reverse=True
                )
                
                for catalog_item_id, item_summary in sorted_catalog_items:
                    catalog_info = item_summary['catalog_item_info']
                    if catalog_info:
                        item_name = catalog_info['name'][:30] + "..." if len(catalog_info['name']) > 30 else catalog_info['name']
                        item_type = catalog_info['type'].replace("com.vmw.", "").replace("vro.workflow", "Workflow").replace("blueprint", "Blueprint")
                    else:
                        item_name = "Unknown"
                        item_type = "Unknown"
                    
                    deployment_count = item_summary['deployment_count']
                    total_resources = item_summary['total_resources']
                    avg_resources = total_resources / deployment_count if deployment_count > 0 else 0
                    
                    # Find top resource type
                    resource_types = item_summary['resource_types']
                    if resource_types:
                        top_resource_type = max(resource_types.items(), key=lambda x: x[1])[0]
                    else:
                        top_resource_type = "N/A"
                    
                    catalog_table.add_row(
                        item_name,
                        item_type,
                        str(deployment_count),
                        str(total_resources),
                        f"{avg_resources:.1f}",
                        top_resource_type
                    )
                
                console.print(catalog_table)
        
        elif group_by == 'resource-type':
            console.print("\n[bold green]🔧 Deployments by Resource Type[/bold green]")
            
            # Group deployments by their primary resource type
            resource_type_groups = {}
            for deployment in report_data['deployments']:
                if detailed_resources and 'resource_breakdown' in deployment:
                    # Find the most common resource type in this deployment
                    resource_breakdown = deployment['resource_breakdown']
                    if resource_breakdown:
                        primary_type = max(resource_breakdown.items(), key=lambda x: x[1])[0]
                    else:
                        primary_type = "No Resources"
                else:
                    primary_type = "Unknown (Fast Mode)"
                
                if primary_type not in resource_type_groups:
                    resource_type_groups[primary_type] = []
                resource_type_groups[primary_type].append(deployment)
            
            for resource_type, deployments in sorted(resource_type_groups.items(), key=lambda x: len(x[1]), reverse=True):
                console.print(f"\n[bold yellow]🔧 {resource_type}[/bold yellow] ({len(deployments)} deployments)")
                
                type_table = Table()
                type_table.add_column("Deployment", style="green")
                type_table.add_column("Status", style="yellow")
                type_table.add_column("Resources", style="cyan", justify="right")
                type_table.add_column("Catalog Item", style="magenta")
                
                for deployment in deployments[:10]:  # Limit to top 10 per type
                    catalog_item_name = "Unlinked"
                    if deployment.get('catalog_item_info'):
                        catalog_item_name = deployment['catalog_item_info']['name'][:20] + "..." if len(deployment['catalog_item_info']['name']) > 20 else deployment['catalog_item_info']['name']
                    
                    type_table.add_row(
                        deployment['name'][:25] + "..." if len(deployment['name']) > 25 else deployment['name'],
                        deployment['status'],
                        str(deployment['resource_count']),
                        catalog_item_name
                    )
                
                console.print(type_table)
                if len(deployments) > 10:
                    console.print(f"[dim]... and {len(deployments) - 10} more deployments[/dim]")
        
        elif group_by == 'deployment-status':
            console.print("\n[bold green]📊 Resources by Deployment Status[/bold green]")
            
            # Group deployments by status
            status_groups = {}
            for deployment in report_data['deployments']:
                status = deployment['status']
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(deployment)
            
            for status, deployments in sorted(status_groups.items(), key=lambda x: len(x[1]), reverse=True):
                total_resources_in_status = sum(d['resource_count'] for d in deployments)
                console.print(f"\n[bold yellow]📊 {status}[/bold yellow] ({len(deployments)} deployments, {total_resources_in_status} resources)")
                
                status_table = Table()
                status_table.add_column("Deployment", style="green")
                status_table.add_column("Resources", style="cyan", justify="right")
                status_table.add_column("Catalog Item", style="magenta")
                status_table.add_column("Created", style="blue")
                
                # Sort by resource count within status
                sorted_deployments = sorted(deployments, key=lambda x: x['resource_count'], reverse=True)
                
                for deployment in sorted_deployments[:10]:  # Limit to top 10 per status
                    catalog_item_name = "Unlinked"
                    if deployment.get('catalog_item_info'):
                        catalog_item_name = deployment['catalog_item_info']['name'][:20] + "..." if len(deployment['catalog_item_info']['name']) > 20 else deployment['catalog_item_info']['name']
                    
                    created_date = "Unknown"
                    if deployment.get('created_at'):
                        try:
                            from datetime import datetime
                            import re
                            clean_timestamp = re.sub(r'\+\d{2}:\d{2}$|Z$', '', deployment['created_at'])
                            if '.' in clean_timestamp:
                                clean_timestamp = clean_timestamp.split('.')[0]
                            created_at = datetime.fromisoformat(clean_timestamp)
                            created_date = created_at.strftime('%Y-%m-%d')
                        except Exception:
                            created_date = "Invalid"
                    
                    status_table.add_row(
                        deployment['name'][:25] + "..." if len(deployment['name']) > 25 else deployment['name'],
                        str(deployment['resource_count']),
                        catalog_item_name,
                        created_date
                    )
                
                console.print(status_table)
                if len(deployments) > 10:
                    console.print(f"[dim]... and {len(deployments) - 10} more deployments[/dim]")
        
        # Show unlinked deployments if any
        if report_data['unlinked_deployments']:
            console.print(f"\n[bold yellow]⚠️  Unlinked Deployments ({len(report_data['unlinked_deployments'])})[/bold yellow]")
            
            unlinked_table = Table(title="Deployments Not Linked to Catalog Items")
            unlinked_table.add_column("Deployment", style="green")
            unlinked_table.add_column("Status", style="yellow")
            unlinked_table.add_column("Resources", style="cyan", justify="right")
            unlinked_table.add_column("Reason", style="red")
            
            # Sort unlinked deployments by resource count
            sorted_unlinked = sorted(report_data['unlinked_deployments'], key=lambda x: x['resource_count'], reverse=True)
            
            for deployment in sorted_unlinked[:10]:  # Show top 10 unlinked deployments
                reason = deployment.get('unlinked_reason', {}).get('primary_reason', 'unknown')
                reason_display = reason.replace('_', ' ').title()
                
                unlinked_table.add_row(
                    deployment['name'][:25] + "..." if len(deployment['name']) > 25 else deployment['name'],
                    deployment['status'],
                    str(deployment['resource_count']),
                    reason_display
                )
            
            console.print(unlinked_table)
            if len(report_data['unlinked_deployments']) > 10:
                console.print(f"[dim]... and {len(report_data['unlinked_deployments']) - 10} more unlinked deployments[/dim]")
    
    elif ctx.obj['format'] == 'json':
        console.print(json.dumps(report_data, indent=2))
    
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump(report_data, default_flow_style=False))

@report.command('unsync')
@click.option('--project', help='Filter by project ID')
@click.option('--detailed-resources', is_flag=True, 
              help='Fetch exact resource counts (slower but more accurate)')
@click.option('--show-details', is_flag=True,
              help='Show detailed analysis for each unsynced deployment')
@click.option('--reason-filter', help='Filter by specific reason (e.g., missing_catalog_references, catalog_item_deleted)')
@click.pass_context
def unsync_report(ctx, project, detailed_resources, show_details, reason_filter):
    """Generate a report of deployments that don't match to catalog items.
    
    This report identifies "unsynced" deployments that cannot be linked back to any 
    catalog item in the system. These deployments may indicate:
    - Deployments created outside the service catalog
    - Catalog items that were deleted after deployment
    - Issues with deployment tracking or naming
    - Failed deployments that lost their catalog associations
    
    The report provides detailed analysis of why each deployment is unsynced
    and suggests potential remediation actions.
    """
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    console.print("[bold blue]🔍 Generating Unsynced Deployments Report...[/bold blue]")
    
    if detailed_resources:
        console.print("[yellow]⚠️  Detailed resource counting enabled - this may take longer[/yellow]")
    
    with console.status("[bold green]Analyzing unsynced deployments..."):
        unsync_data = client.get_unsynced_deployments(
            project_id=project, 
            fetch_resource_counts=detailed_resources
        )
    
    # Apply reason filter if specified
    if reason_filter:
        filtered_deployments = []
        for unsync in unsync_data['unsynced_deployments']:
            if unsync['analysis']['primary_reason'] == reason_filter:
                filtered_deployments.append(unsync)
        
        unsync_data['unsynced_deployments'] = filtered_deployments
        # Recalculate summary for filtered data
        unsync_data['summary']['unsynced_deployments'] = len(filtered_deployments)
        unsync_data['summary']['unsynced_percentage'] = (
            len(filtered_deployments) / max(unsync_data['summary']['total_deployments'], 1) * 100
        )
    
    # Display results
    if ctx.obj['format'] == 'table':
        summary = unsync_data['summary']
        
        # Summary statistics
        console.print("\n[bold green]📊 Unsynced Deployments Summary[/bold green]")
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        summary_table.add_column("Note", style="dim")
        
        summary_table.add_row("Total Deployments", str(summary['total_deployments']), "All deployments in system")
        summary_table.add_row("Linked Deployments", str(summary['linked_deployments']), "Successfully matched to catalog items")
        summary_table.add_row("[bold red]Unsynced Deployments[/bold red]", str(summary['unsynced_deployments']), "Cannot match to catalog items")
        summary_table.add_row("Unsynced Percentage", f"{summary['unsynced_percentage']}%", "Percentage of total deployments")
        summary_table.add_row("Unsynced Resources", str(summary['total_unsynced_resources']), "Resources in unsynced deployments")
        summary_table.add_row("Total Catalog Items", str(summary['catalog_items_count']), "Available for matching")
        
        console.print(summary_table)
        
        if reason_filter:
            console.print(f"\n[yellow]🔎 Filtered by reason: {reason_filter}[/yellow]")
        
        # Reason breakdown
        if unsync_data['reason_groups']:
            console.print("\n[bold green]🔍 Root Cause Analysis[/bold green]")
            reason_table = Table()
            reason_table.add_column("Reason", style="yellow", width=25)
            reason_table.add_column("Count", style="cyan", justify="right")
            reason_table.add_column("Description", style="white")
            
            reason_descriptions = {
                'missing_catalog_references': 'No catalog item ID/name in deployment',
                'catalog_item_deleted': 'Referenced catalog item no longer exists', 
                'catalog_name_mismatch': 'Catalog item name not found',
                'blueprint_deleted': 'Referenced blueprint no longer exists',
                'matching_logic_issue': 'Item exists but matching failed',
                'weak_name_association': 'Possible match based on name similarity',
                'failed_deployment': 'Deployment failed and lost associations',
                'external_creation': 'Created outside service catalog',
                'unknown': 'Could not determine cause'
            }
            
            for reason, count in sorted(unsync_data['reason_groups'].items(), key=lambda x: x[1], reverse=True):
                description = reason_descriptions.get(reason, 'Unknown reason type')
                reason_table.add_row(reason.replace('_', ' ').title(), str(count), description)
            
            console.print(reason_table)
        
        # Status breakdown
        if unsync_data['status_breakdown']:
            console.print("\n[bold green]📈 Status Breakdown[/bold green]")
            status_table = Table()
            status_table.add_column("Status", style="blue")
            status_table.add_column("Count", style="cyan", justify="right")
            status_table.add_column("Note", style="dim")
            
            for status, count in sorted(unsync_data['status_breakdown'].items(), key=lambda x: x[1], reverse=True):
                note = ""
                if status in ['FAILED', 'CREATE_FAILED', 'UPDATE_FAILED']:
                    note = "Failed deployments often lose catalog links"
                elif status in ['CREATE_SUCCESSFUL', 'UPDATE_SUCCESSFUL', 'SUCCESSFUL']:
                    note = "Successful but untracked deployments"
                elif status in ['CREATE_INPROGRESS', 'UPDATE_INPROGRESS', 'INPROGRESS']:
                    note = "May link once deployment completes"
                
                status_table.add_row(status, str(count), note)
            
            console.print(status_table)
        
        # Age breakdown
        if unsync_data['age_breakdown']:
            console.print("\n[bold green]🕐 Age Distribution[/bold green]")
            age_table = Table()
            age_table.add_column("Age Range", style="magenta")
            age_table.add_column("Count", style="cyan", justify="right")
            age_table.add_column("Implication", style="white")
            
            age_implications = {
                '<24h': 'Recent - may be deployment in progress',
                '1-7d': 'Recent - likely legitimate unsynced deployment',
                '1-4w': 'Aging - should be investigated',
                '>1m': 'Old - likely requires cleanup or investigation'
            }
            
            for age_range, count in unsync_data['age_breakdown'].items():
                if count > 0:
                    implication = age_implications.get(age_range, '')
                    age_table.add_row(age_range, str(count), implication)
            
            console.print(age_table)
        
        # Detailed deployments list
        if show_details and unsync_data['unsynced_deployments']:
            console.print("\n[bold green]📋 Detailed Unsynced Deployments[/bold green]")
            
            for i, unsync in enumerate(unsync_data['unsynced_deployments'][:20]):  # Limit to 20 for readability
                deployment = unsync['deployment']
                analysis = unsync['analysis']
                
                # Deployment header
                console.print(f"\n[bold cyan]{i+1}. {deployment.get('name', 'Unknown')}[/bold cyan]")
                console.print(f"   ID: {deployment.get('id', 'N/A')}")
                console.print(f"   Status: {deployment.get('status', 'N/A')}")
                console.print(f"   Created: {deployment.get('createdAt', 'N/A')}")
                console.print(f"   Resources: {unsync['resource_count']}")
                
                # Analysis
                console.print(f"   [yellow]Reason: {analysis['primary_reason'].replace('_', ' ').title()}[/yellow]")
                
                if analysis['details']:
                    for detail in analysis['details']:
                        console.print(f"   • {detail}")
                
                if analysis['suggestions']:
                    console.print(f"   [green]Suggestions:[/green]")
                    for suggestion in analysis['suggestions']:
                        console.print(f"   → {suggestion}")
                
                if analysis['potential_matches']:
                    console.print(f"   [blue]Potential Matches:[/blue]")
                    for match in analysis['potential_matches']:
                        console.print(f"   → {match['name']} (ID: {match['id']}) - {match['similarity_reason']}")
            
            if len(unsync_data['unsynced_deployments']) > 20:
                remaining = len(unsync_data['unsynced_deployments']) - 20
                console.print(f"\n[dim]... and {remaining} more unsynced deployments (use JSON/YAML format for full list)[/dim]")
        
        elif unsync_data['unsynced_deployments'] and not show_details:
            console.print("\n[dim]💡 Use --show-details to see detailed analysis of each unsynced deployment[/dim]")
        
        if not unsync_data['unsynced_deployments']:
            console.print("\n[bold green]✅ No unsynced deployments found! All deployments are properly linked to catalog items.[/bold green]")
    
    elif ctx.obj['format'] == 'json':
        # Convert to JSON-serializable format
        json_data = {
            'summary': unsync_data['summary'],
            'reason_groups': unsync_data['reason_groups'],
            'status_breakdown': unsync_data['status_breakdown'],
            'age_breakdown': unsync_data['age_breakdown'],
            'unsynced_deployments': [
                {
                    'deployment': {
                        'id': unsync['deployment'].get('id'),
                        'name': unsync['deployment'].get('name'),
                        'status': unsync['deployment'].get('status'),
                        'createdAt': unsync['deployment'].get('createdAt'),
                        'projectId': unsync['deployment'].get('projectId'),
                        'catalogItemId': unsync['deployment'].get('catalogItemId'),
                        'catalogItemName': unsync['deployment'].get('catalogItemName'),
                        'blueprintId': unsync['deployment'].get('blueprintId')
                    },
                    'resource_count': unsync['resource_count'],
                    'analysis': unsync['analysis']
                }
                for unsync in unsync_data['unsynced_deployments']
            ]
        }
        console.print(json.dumps(json_data, indent=2))
    
    elif ctx.obj['format'] == 'yaml':
        # Convert to YAML format
        yaml_data = {
            'summary': unsync_data['summary'],
            'reason_groups': unsync_data['reason_groups'],
            'status_breakdown': unsync_data['status_breakdown'],
            'age_breakdown': unsync_data['age_breakdown'],
            'unsynced_deployments': [
                {
                    'deployment': {
                        'id': unsync['deployment'].get('id'),
                        'name': unsync['deployment'].get('name'),
                        'status': unsync['deployment'].get('status'),
                        'createdAt': unsync['deployment'].get('createdAt'),
                        'projectId': unsync['deployment'].get('projectId'),
                        'catalogItemId': unsync['deployment'].get('catalogItemId'),
                        'catalogItemName': unsync['deployment'].get('catalogItemName'),
                        'blueprintId': unsync['deployment'].get('blueprintId')
                    },
                    'resource_count': unsync['resource_count'],
                    'analysis': unsync['analysis']
                }
                for unsync in unsync_data['unsynced_deployments']
            ]
        }
        console.print(yaml.dump(yaml_data, default_flow_style=False))

# Workflow commands
@main.group()
def workflow():
    """Workflow operations."""
    pass

@workflow.command('list')
@click.option('--page-size', type=int, default=100, help='Number of items per page (default: 100, max: 2000)')
@click.option('--first-page-only', is_flag=True, help='Fetch only the first page instead of all items')
@click.pass_context
def list_workflows(ctx, page_size, first_page_only):
    """List available workflows.
    
    By default, this command fetches all workflows across all pages.
    Use --first-page-only to limit to just the first page for faster results.
    """
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    status_msg = "[bold blue]Fetching workflows..."
    if not first_page_only:
        status_msg += " (all pages)"
    
    with console.status(status_msg):
        workflows = client.list_workflows(
            page_size=page_size,
            fetch_all=not first_page_only
        )
    
    if ctx.obj['format'] == 'table':
        table_title = f"Available Workflows ({len(workflows)} items)"
        if first_page_only:
            table_title += " - First Page Only"
        
        table = Table(title=table_title)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description", style="yellow")
        
        for wf in workflows:
            attrs = wf.get('attributes', [])
            name = next((attr.get('value') for attr in attrs if attr.get('name') == 'name'), 'N/A')
            description = next((attr.get('value') for attr in attrs if attr.get('name') == 'description'), 'N/A')
            
            table.add_row(
                wf.get('href', '').split('/')[-1] if wf.get('href') else 'N/A',
                name,
                description
            )
        
        console.print(table)
    elif ctx.obj['format'] == 'json':
        console.print(json.dumps(workflows, indent=2))
    elif ctx.obj['format'] == 'yaml':
        console.print(yaml.dump(workflows, default_flow_style=False))

@workflow.command('run')
@click.argument('workflow_id')
@click.option('--inputs', help='Input parameters as JSON string')
@click.option('--inputs-file', help='Input parameters from YAML/JSON file')
@click.pass_context
def run_workflow(ctx, workflow_id, inputs, inputs_file):
    """Execute a workflow."""
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    # Parse inputs
    inputs_dict = {}
    if inputs:
        inputs_dict = json.loads(inputs)
    elif inputs_file:
        with open(inputs_file, 'r') as f:
            if inputs_file.endswith('.yaml') or inputs_file.endswith('.yml'):
                inputs_dict = yaml.safe_load(f)
            else:
                inputs_dict = json.load(f)
    
    with console.status(f"[bold blue]Running workflow {workflow_id}..."):
        run = client.run_workflow(workflow_id, inputs_dict)
    
    console.print(f"[green]✅ Workflow execution started![/green]")
    console.print(f"[cyan]Execution ID: {run.id}[/cyan]")
    console.print(f"[cyan]State: {run.state}[/cyan]")

if __name__ == '__main__':
    main()


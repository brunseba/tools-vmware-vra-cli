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
@click.option('--statuses', help='Comma-separated list of statuses to include (default: all)',
              default='CREATE_SUCCESSFUL,UPDATE_SUCCESSFUL,SUCCESSFUL,CREATE_FAILED,UPDATE_FAILED,FAILED,CREATE_INPROGRESS,UPDATE_INPROGRESS,INPROGRESS')
@click.pass_context
def activity_timeline_report(ctx, project, days_back, statuses):
    """Generate an activity timeline for service catalog items.
    
    This timeline provides a historical view of deployment activities over a specified period,
    allowing you to see patterns, peak activity periods, and trends.
    """
    client = get_catalog_client(verbose=ctx.obj['verbose'])
    
    console.print("[bold blue]📈 Generating Activity Timeline Report...[/bold blue]")
    
    # Convert status string to list
    include_statuses = [status.strip().upper() for status in statuses.split(',')]
    
    with console.status("[bold green]Analyzing activity timeline..."):
        timeline_data = client.get_activity_timeline(
            project_id=project, 
            days_back=days_back, 
            include_statuses=include_statuses
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
        
        # Daily activity table
        console.print("\n[bold green]📅 Daily Activity[/bold green]")
        daily_table = Table(title="Daily Deployment Activity")
        daily_table.add_column("Date", style="blue")
        daily_table.add_column("Deployments", style="cyan", justify="right")
        daily_table.add_column("Success", style="green", justify="right")
        daily_table.add_column("Failed", style="red", justify="right")
        daily_table.add_column("In Progress", style="yellow", justify="right")
        daily_table.add_column("Unique Items", style="magenta", justify="right")
        daily_table.add_column("Unique Projects", style="white", justify="right")
        
        for date, data in sorted(timeline_data['daily_activity'].items()):
            daily_table.add_row(
                date,
                str(data['total_deployments']),
                str(data['successful_deployments']),
                str(data['failed_deployments']),
                str(data['in_progress_deployments']),
                str(data['unique_catalog_items']),
                str(data['unique_projects'])
            )
        
        console.print(daily_table)
        
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
        
        summary_table.add_row("Total Catalog Items", str(total_catalog_items))
        summary_table.add_row("Active Items (with deployments)", str(len([s for s in original_usage_stats if s['deployment_count'] > 0])))
        summary_table.add_row("Total Deployments (system-wide)", str(len(all_deployments)))
        summary_table.add_row("Catalog-linked Deployments", str(total_catalog_deployments))
        summary_table.add_row("Unlinked Deployments", str(len(all_deployments) - total_catalog_deployments))
        if not include_zero:
            summary_table.add_row("Showing Items", str(total_items))
            summary_table.add_row("Showing Deployments", str(catalog_deployments))
        summary_table.add_row("Total Resources (estimated)", str(catalog_resources))
        if active_items > 0:
            avg_deployments = catalog_deployments / active_items if not include_zero else total_catalog_deployments / len([s for s in original_usage_stats if s['deployment_count'] > 0])
            summary_table.add_row("Avg Deployments per Active Item", f"{avg_deployments:.1f}")
        
        console.print(summary_table)
        
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


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

console = Console()

# Default configuration
DEFAULT_CONFIG = {
    "api_url": "https://vra.example.com",
    "tenant": "vsphere.local",
    "verify_ssl": True,
    "timeout": 30
}

def get_config() -> Dict[str, Any]:
    """Get configuration from environment or config file."""
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables
    config["api_url"] = os.getenv("VRA_URL", config["api_url"])
    config["tenant"] = os.getenv("VRA_TENANT", config["tenant"])
    config["verify_ssl"] = os.getenv("VRA_VERIFY_SSL", "true").lower() == "true"
    
    return config

def get_token() -> Optional[str]:
    """Get stored authentication token."""
    try:
        return keyring.get_password("vmware-vra-cli", "access_token")
    except Exception:
        return None

def store_token(token: str) -> None:
    """Store authentication token securely."""
    try:
        keyring.set_password("vmware-vra-cli", "access_token", token)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not store token securely: {e}[/yellow]")

def get_catalog_client() -> CatalogClient:
    """Get configured catalog client."""
    config = get_config()
    token = get_token()
    
    if not token:
        console.print("[red]No authentication token found. Please run 'vra auth login' first.[/red]")
        raise click.Abort()
    
    return CatalogClient(
        base_url=config["api_url"],
        token=token,
        verify_ssl=config["verify_ssl"]
    )

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'yaml']), 
              default='table', help='Output format')
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
def login(username, password, url, tenant):
    """
    Authenticate to vRA and obtain bearer token.
    """
    auth_url = f"{url}/csp/gateway/am/api/login?access_token"
    
    with console.status("[bold green]Authenticating..."):
        try:
            response = requests.post(
                auth_url, 
                auth=HTTPBasicAuth(username, password),
                verify=get_config()["verify_ssl"]
            )
            response.raise_for_status()
            
            token = response.json()['access_token']
            store_token(token)
            
            console.print("[bold green]✅ Authentication successful![/bold green]")
            console.print("[green]🔑 Token saved securely[/green]")
            
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]❌ Authentication failed: {e}[/bold red]")
            raise click.Abort()

@auth.command()
def logout():
    """Clear stored authentication token."""
    try:
        keyring.delete_password("vmware-vra-cli", "access_token")
        console.print("[green]✅ Logged out successfully[/green]")
    except Exception:
        console.print("[yellow]No stored credentials found[/yellow]")

@auth.command()
def status():
    """Check authentication status."""
    token = get_token()
    if token:
        console.print("[green]✅ Authenticated[/green]")
    else:
        console.print("[red]❌ Not authenticated[/red]")

# Service Catalog commands
@main.group()
def catalog():
    """Service Catalog operations."""
    pass

@catalog.command('list')
@click.option('--project', help='Filter by project ID')
@click.pass_context
def list_catalog_items(ctx, project):
    """List available catalog items."""
    client = get_catalog_client()
    
    with console.status("[bold blue]Fetching catalog items..."):
        items = client.list_catalog_items(project_id=project)
    
    if ctx.obj['format'] == 'table':
        table = Table(title="Service Catalog Items")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Version", style="blue")
        
        for item in items:
            table.add_row(
                item.id,
                item.name,
                item.type,
                item.status,
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
    client = get_catalog_client()
    
    with console.status(f"[bold blue]Fetching catalog item {item_id}..."):
        item = client.get_catalog_item(item_id)
    
    if ctx.obj['format'] == 'table':
        table = Table(title=f"Catalog Item: {item.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("ID", item.id)
        table.add_row("Name", item.name)
        table.add_row("Type", item.type)
        table.add_row("Status", item.status)
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
    client = get_catalog_client()
    
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
    client = get_catalog_client()
    
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
@click.pass_context
def list_deployments(ctx, project, status):
    """List deployments."""
    client = get_catalog_client()
    
    with console.status("[bold blue]Fetching deployments..."):
        deployments = client.list_deployments(project_id=project, status=status)
    
    if ctx.obj['format'] == 'table':
        table = Table(title="Deployments")
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
    client = get_catalog_client()
    
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
def delete_deployment(deployment_id, confirm):
    """Delete a deployment."""
    if not confirm:
        if not click.confirm(f"Are you sure you want to delete deployment {deployment_id}?"):
            return
    
    client = get_catalog_client()
    
    with console.status(f"[bold red]Deleting deployment {deployment_id}..."):
        result = client.delete_deployment(deployment_id)
    
    console.print(f"[green]✅ Deployment {deployment_id} deletion initiated[/green]")

@deployment.command('resources')
@click.argument('deployment_id')
@click.pass_context
def show_deployment_resources(ctx, deployment_id):
    """Show deployment resources."""
    client = get_catalog_client()
    
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
@click.pass_context
def list_tags(ctx, search):
    """List available tags."""
    client = get_catalog_client()
    
    with console.status("[bold blue]Fetching tags..."):
        tags = client.list_tags(search=search)
    
    if ctx.obj['format'] == 'table':
        table = Table(title="Tags")
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
    client = get_catalog_client()
    
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
    client = get_catalog_client()
    
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
    client = get_catalog_client()
    
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
def delete_tag(tag_id, confirm):
    """Delete a tag."""
    if not confirm:
        if not click.confirm(f"Are you sure you want to delete tag {tag_id}?"):
            return
    
    client = get_catalog_client()
    
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
def assign_tag(resource_id, tag_id, resource_type):
    """Assign a tag to a resource."""
    client = get_catalog_client()
    
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
def remove_tag(resource_id, tag_id, resource_type, confirm):
    """Remove a tag from a resource."""
    if not confirm:
        if not click.confirm(f"Are you sure you want to remove tag {tag_id} from {resource_type} {resource_id}?"):
            return
    
    client = get_catalog_client()
    
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
    client = get_catalog_client()
    
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

# Workflow commands
@main.group()
def workflow():
    """Workflow operations."""
    pass

@workflow.command('list')
@click.pass_context
def list_workflows(ctx):
    """List available workflows."""
    client = get_catalog_client()
    
    with console.status("[bold blue]Fetching workflows..."):
        workflows = client.list_workflows()
    
    if ctx.obj['format'] == 'table':
        table = Table(title="Available Workflows")
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
    client = get_catalog_client()
    
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


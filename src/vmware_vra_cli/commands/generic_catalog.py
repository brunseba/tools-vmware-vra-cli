"""Generic catalog CLI commands with schema-driven functionality."""

import json
import click
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..config import get_config
from ..api.catalog import CatalogClient
from ..auth import TokenManager
from ..catalog.schema_registry import registry
from ..catalog.schema_engine import SchemaEngine
from ..catalog.form_builder import FormBuilder
from ..models.catalog_schema import ExecutionContext

console = Console()


def ensure_schemas_loaded():
    """Ensure schemas are loaded, auto-discover if needed."""
    if len(registry) == 0:
        current_dir = Path.cwd()
        default_dir = current_dir / 'inputs' / 'schema_exports'
        if default_dir.exists():
            registry.add_schema_directory(default_dir)
            registry.load_schemas()


def get_catalog_client() -> CatalogClient:
    """Get configured catalog client."""
    config = get_config()
    token = TokenManager.get_access_token()
    
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
        verify_ssl=config["verify_ssl"]
    )


@click.group(name='schema-catalog')
def schema_catalog():
    """Schema-driven catalog operations."""
    pass


@schema_catalog.command()
@click.option('--schema-dir', '-d', type=click.Path(exists=True, file_okay=False, path_type=Path),
              help='Directory containing schema files')
@click.option('--pattern', default='*_schema.json', help='Schema file pattern')
def load_schemas(schema_dir: Optional[Path], pattern: str):
    """Load catalog item schemas from directory."""
    # Clear existing directories and add new ones
    registry.schema_dirs.clear()
    
    if schema_dir:
        registry.add_schema_directory(schema_dir)
    
    # Add default schema directories if no specific directory provided
    if not schema_dir:
        current_dir = Path.cwd()
        possible_dirs = [
            current_dir / 'inputs' / 'schema_exports',
            current_dir / 'schemas',
            Path.home() / '.vmware-vra-cli' / 'schemas'
        ]
        
        for dir_path in possible_dirs:
            if dir_path.exists():
                registry.add_schema_directory(dir_path)
    
    count = registry.load_schemas(pattern=pattern, force_reload=True)
    
    if count == 0:
        console.print("[yellow]⚠️ No schemas found. Please check your schema directories.[/yellow]")
        console.print("\\nSchema directories searched:")
        for dir_path in registry.schema_dirs:
            console.print(f"  - {dir_path}")
    else:
        console.print(f"[green]✅ Successfully loaded {count} catalog schemas[/green]")


@schema_catalog.command()
@click.option('--type', 'item_type', help='Filter by catalog item type')
@click.option('--name', 'name_filter', help='Filter by name')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table')
def list_schemas(item_type: Optional[str], name_filter: Optional[str], output_format: str):
    """List available catalog schemas."""
    ensure_schemas_loaded()
    schemas = registry.list_schemas(item_type=item_type, name_filter=name_filter)
    
    if not schemas:
        console.print("[yellow]No schemas found matching criteria[/yellow]")
        return
    
    if output_format == 'json':
        schema_data = [
            {
                'id': schema.id,
                'name': schema.name,
                'type': schema.type,
                'description': schema.description
            }
            for schema in schemas
        ]
        console.print(json.dumps(schema_data, indent=2))
        return
    
    # Table output
    table = Table(title=f"📋 Catalog Schemas ({len(schemas)} found)")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Type", style="blue")
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Description", style="green")
    
    for schema in schemas:
        description = (schema.description or "")[:50] + "..." if schema.description and len(schema.description) > 50 else (schema.description or "")
        table.add_row(schema.name, schema.type, schema.id, description)
    
    console.print(table)


@schema_catalog.command()
@click.argument('query')
def search_schemas(query: str):
    """Search catalog schemas by name or description."""
    ensure_schemas_loaded()
    matches = registry.search_schemas(query)
    
    if not matches:
        console.print(f"[yellow]No schemas found matching '{query}'[/yellow]")
        return
    
    console.print(f"[green]Found {len(matches)} matching schemas:[/green]\\n")
    
    for match in matches:
        console.print(f"📄 [cyan]{match.name}[/cyan]")
        console.print(f"   ID: [dim]{match.id}[/dim]")
        console.print(f"   Type: [blue]{match.type}[/blue]")
        if match.description:
            console.print(f"   Description: {match.description}")
        console.print()


@schema_catalog.command()
@click.argument('catalog_item_id')
def show_schema(catalog_item_id: str):
    """Show detailed schema information for a catalog item."""
    ensure_schemas_loaded()
    schema = registry.get_schema(catalog_item_id)
    
    if not schema:
        console.print(f"[red]Schema not found for catalog item: {catalog_item_id}[/red]")
        return
    
    # Display schema info
    info = schema.catalog_item_info
    console.print(Panel(
        f"[bold]{info.name}[/bold]\\n"
        f"Type: [cyan]{info.type}[/cyan]\\n"
        f"ID: [dim]{info.id}[/dim]\\n"
        f"Description: {info.description or 'None'}",
        title="📋 Catalog Item Schema",
        border_style="blue"
    ))
    
    # Display fields
    engine = SchemaEngine()
    fields = engine.extract_form_fields(schema)
    
    if fields:
        table = Table(title="Schema Fields")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Required", style="red")
        table.add_column("Description", style="green")
        table.add_column("Constraints", style="yellow")
        
        for field in fields:
            required = "✓" if field.required else ""
            constraints = []
            
            if field.validation:
                if 'minimum' in field.validation:
                    constraints.append(f"min: {field.validation['minimum']}")
                if 'maximum' in field.validation:
                    constraints.append(f"max: {field.validation['maximum']}")
                if 'min_length' in field.validation:
                    constraints.append(f"min chars: {field.validation['min_length']}")
                if 'max_length' in field.validation:
                    constraints.append(f"max chars: {field.validation['max_length']}")
                if field.choices:
                    constraints.append(f"choices: {len(field.choices)}")
            
            constraint_str = ", ".join(constraints) if constraints else ""
            table.add_row(
                field.name,
                field.type,
                required,
                field.description or "",
                constraint_str
            )
        
        console.print(table)


@schema_catalog.command()
@click.argument('catalog_item_id')
@click.option('--project-id', required=True, help='vRA project ID')
@click.option('--deployment-name', help='Custom deployment name')
@click.option('--input-file', type=click.Path(exists=True, path_type=Path), 
              help='JSON file with input values')
@click.option('--skip-optional', is_flag=True, help='Skip optional fields')
@click.option('--dry-run', is_flag=True, help='Validate inputs without executing')
def execute_schema(catalog_item_id: str, project_id: str, deployment_name: Optional[str],
                  input_file: Optional[Path], skip_optional: bool, dry_run: bool):
    """Execute a catalog item using its schema for input collection."""
    ensure_schemas_loaded()
    schema = registry.get_schema(catalog_item_id)
    
    if not schema:
        console.print(f"[red]Schema not found for catalog item: {catalog_item_id}[/red]")
        console.print("💡 Run 'vra schema-catalog load-schemas' to load available schemas.")
        return
    
    engine = SchemaEngine()
    form_builder = FormBuilder(engine)
    
    # Load initial inputs from file if provided
    initial_inputs = {}
    if input_file:
        try:
            with open(input_file) as f:
                initial_inputs = json.load(f)
            console.print(f"[green]✅ Loaded inputs from {input_file}[/green]")
        except Exception as e:
            console.print(f"[red]Error loading input file: {e}[/red]")
            return
    
    # Collect inputs interactively
    try:
        inputs = form_builder.collect_inputs(
            schema, 
            initial_values=initial_inputs,
            skip_optional=skip_optional
        )
    except click.Abort:
        return
    
    # Validate inputs
    validation_result = engine.validate_inputs(schema, inputs)
    
    if not validation_result.valid:
        console.print("[red]❌ Input validation failed:[/red]")
        for error in validation_result.errors:
            console.print(f"  • {error}")
        return
    
    if validation_result.warnings:
        console.print("[yellow]⚠️ Warnings:[/yellow]")
        for warning in validation_result.warnings:
            console.print(f"  • {warning}")
    
    # Generate deployment name if not provided
    if not deployment_name:
        deployment_name = f"deployment-{schema.catalog_item_info.name.lower().replace(' ', '-').replace('_', '-')}"
    
    # Create execution context
    context = ExecutionContext(
        schema=schema,
        inputs=validation_result.processed_inputs,
        project_id=project_id,
        deployment_name=deployment_name,
        dry_run=dry_run
    )
    
    # Show execution summary
    summary = engine.get_execution_summary(context)
    
    if dry_run:
        console.print(Panel(
            f"[bold]DRY RUN - No actual execution[/bold]\\n"
            f"Catalog Item: {summary['catalog_item']['name']}\\n"
            f"Deployment: {summary['deployment']['name']}\\n"
            f"Project: {summary['deployment']['project_id']}\\n"
            f"Inputs: {len(summary['inputs'])} fields",
            title="🧪 Dry Run Summary",
            border_style="yellow"
        ))
        
        form_builder.display_inputs_summary(context.inputs)
        return
    
    # Confirm execution
    if not form_builder.confirm_execution(schema, context.inputs, deployment_name, project_id):
        console.print("[yellow]Execution cancelled by user[/yellow]")
        return
    
    # Execute the catalog item
    try:
        client = get_catalog_client()
        payload = engine.generate_request_payload(context)
        
        console.print("[blue]🚀 Executing catalog item...[/blue]")
        
        # Make the request (using existing catalog client)
        response = client.request_catalog_item(
            catalog_item_id=catalog_item_id,
            project_id=project_id,
            deployment_name=deployment_name,
            inputs=context.inputs
        )
        
        console.print("[green]✅ Catalog item execution started successfully![/green]")
        console.print(f"Deployment ID: [cyan]{response.get('deploymentId', 'N/A')}[/cyan]")
        console.print(f"Request ID: [dim]{response.get('id', 'N/A')}[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Execution failed: {e}[/red]")


@schema_catalog.command()
def status():
    """Show schema registry status."""
    ensure_schemas_loaded()
    summary = registry.export_schema_summary()
    
    console.print(Panel(
        f"[bold]Total Schemas:[/bold] {summary['total_schemas']}\\n"
        f"[bold]Schema Directories:[/bold] {len(summary['directories'])}\\n"
        f"[bold]Types:[/bold] {', '.join(f'{k}: {v}' for k, v in summary['types'].items())}",
        title="📊 Schema Registry Status",
        border_style="blue"
    ))
    
    if summary['directories']:
        console.print("\\n[bold]Schema Directories:[/bold]")
        for dir_path in summary['directories']:
            console.print(f"  📁 {dir_path}")


@schema_catalog.command()
@click.argument('output_file', type=click.Path(path_type=Path))
@click.argument('catalog_item_id')
@click.option('--project-id', required=True, help='vRA project ID')
def export_inputs_template(output_file: Path, catalog_item_id: str, project_id: str):
    """Export input template for a catalog item."""
    ensure_schemas_loaded()
    schema = registry.get_schema(catalog_item_id)
    
    if not schema:
        console.print(f"[red]Schema not found for catalog item: {catalog_item_id}[/red]")
        return
    
    # Generate template with default values and comments
    template = {
        "_metadata": {
            "catalog_item_id": catalog_item_id,
            "catalog_item_name": schema.catalog_item_info.name,
            "project_id": project_id,
            "generated_by": "vmware-vra-cli"
        }
    }
    
    # Add field templates
    for field_name, prop in schema.schema.properties.items():
        value = prop.default if prop.default is not None else None
        
        # Add type hint as comment-like key
        template[f"_{field_name}_type"] = prop.type
        if prop.description:
            template[f"_{field_name}_description"] = prop.description
        if field_name in schema.schema.required:
            template[f"_{field_name}_required"] = True
        
        template[field_name] = value
    
    # Write template file
    try:
        with open(output_file, 'w') as f:
            json.dump(template, f, indent=2)
        console.print(f"[green]✅ Input template exported to: {output_file}[/green]")
    except Exception as e:
        console.print(f"[red]Error writing template file: {e}[/red]")


@schema_catalog.command()
def clear_cache():
    """Clear the schema registry cache."""
    registry.clear_cache()
    console.print("[green]✅ Schema cache cleared[/green]")

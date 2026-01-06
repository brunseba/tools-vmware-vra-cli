"""Interactive form builder for schema-driven input collection."""

import click
from typing import Dict, Any, List, Optional, Union
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from ..models.catalog_schema import FormField, CatalogItemSchema
from .schema_engine import SchemaEngine

console = Console()


class FormBuilder:
    """Interactive form builder for collecting catalog item inputs."""
    
    def __init__(self, schema_engine: Optional[SchemaEngine] = None):
        """Initialize form builder.
        
        Args:
            schema_engine: Schema engine for processing schemas
        """
        self.schema_engine = schema_engine or SchemaEngine()
    
    def collect_inputs(self, schema: CatalogItemSchema, 
                      initial_values: Optional[Dict[str, Any]] = None,
                      skip_optional: bool = False) -> Dict[str, Any]:
        """Collect inputs interactively based on schema.
        
        Args:
            schema: Catalog item schema
            initial_values: Pre-filled values
            skip_optional: Skip optional fields
            
        Returns:
            Dictionary of collected input values
        """
        inputs = initial_values.copy() if initial_values else {}
        fields = self.schema_engine.extract_form_fields(schema)
        
        console.print(Panel(
            f"[bold blue]{schema.catalog_item_info.name}[/bold blue]\\n"
            f"Type: [cyan]{schema.catalog_item_info.type}[/cyan]\\n"
            f"Required fields: [yellow]{len([f for f in fields if f.required])}[/yellow] | "
            f"Optional fields: [dim]{len([f for f in fields if not f.required])}[/dim]",
            title="📋 Service Catalog Item",
            border_style="blue"
        ))
        
        for field in fields:
            # Skip if we already have a value and it's not required
            if field.name in inputs and not field.required:
                continue
            
            # Skip optional fields if requested
            if skip_optional and not field.required:
                continue
            
            try:
                value = self._collect_field_value(field, inputs.get(field.name))
                if value is not None:
                    inputs[field.name] = value
            except KeyboardInterrupt:
                console.print("\\n[yellow]⚠️ Input collection cancelled[/yellow]")
                raise click.Abort()
        
        return inputs
    
    def _collect_field_value(self, field: FormField, current_value: Any = None) -> Any:
        """Collect value for a single field.
        
        Args:
            field: Form field configuration
            current_value: Current field value
            
        Returns:
            Collected field value
        """
        # Prepare prompt
        prompt_text = self._format_field_prompt(field)
        
        # Show field info
        self._display_field_info(field, current_value)
        
        # Handle different field types
        if field.type == 'boolean':
            return self._collect_boolean_field(field, current_value)
        elif field.choices:
            return self._collect_choice_field(field, current_value)
        elif field.type == 'number':
            return self._collect_number_field(field, current_value)
        elif field.type == 'array':
            return self._collect_array_field(field, current_value)
        else:
            return self._collect_string_field(field, current_value)
    
    def _format_field_prompt(self, field: FormField) -> str:
        """Format the prompt text for a field.
        
        Args:
            field: Form field configuration
            
        Returns:
            Formatted prompt text
        """
        prompt = field.title
        
        if field.required:
            prompt += " [red]*[/red]"
        
        if field.validation:
            constraints = []
            if 'minimum' in field.validation:
                constraints.append(f"min: {field.validation['minimum']}")
            if 'maximum' in field.validation:
                constraints.append(f"max: {field.validation['maximum']}")
            if 'min_length' in field.validation:
                constraints.append(f"min chars: {field.validation['min_length']}")
            if 'max_length' in field.validation:
                constraints.append(f"max chars: {field.validation['max_length']}")
            
            if constraints:
                prompt += f" [dim]({', '.join(constraints)})[/dim]"
        
        return prompt
    
    def _display_field_info(self, field: FormField, current_value: Any = None) -> None:
        """Display field information.
        
        Args:
            field: Form field configuration
            current_value: Current field value
        """
        info_parts = []
        
        # Type and requirement
        type_str = f"[cyan]{field.type}[/cyan]"
        if field.required:
            type_str += " [red](required)[/red]"
        info_parts.append(type_str)
        
        # Current value
        if current_value is not None:
            info_parts.append(f"current: [green]{current_value}[/green]")
        
        # Default value
        if field.default is not None:
            info_parts.append(f"default: [yellow]{field.default}[/yellow]")
        
        # Dynamic source
        if field.dynamic_source:
            info_parts.append("[dim]dynamic[/dim]")
        
        console.print(f"  {' | '.join(info_parts)}")
        
        # Description
        if field.description:
            console.print(f"  [dim]{field.description}[/dim]")
    
    def _collect_boolean_field(self, field: FormField, current_value: Any = None) -> bool:
        """Collect boolean field value.
        
        Args:
            field: Form field configuration
            current_value: Current field value
            
        Returns:
            Boolean value
        """
        default = current_value
        if default is None:
            default = field.default if field.default is not None else None
        
        return Confirm.ask(field.title, default=default)
    
    def _collect_choice_field(self, field: FormField, current_value: Any = None) -> str:
        """Collect choice field value.
        
        Args:
            field: Form field configuration  
            current_value: Current field value
            
        Returns:
            Selected choice value
        """
        if not field.choices:
            return self._collect_string_field(field, current_value)
        
        # Display choices
        console.print("  Available choices:")
        for i, choice in enumerate(field.choices, 1):
            marker = "→" if choice == current_value else " "
            console.print(f"  {marker} {i}. {choice}")
        
        # Get selection
        while True:
            try:
                response = Prompt.ask(
                    f"{field.title} (1-{len(field.choices)} or enter choice)",
                    default=current_value
                )
                
                # Try to parse as number
                if response.isdigit():
                    idx = int(response) - 1
                    if 0 <= idx < len(field.choices):
                        return field.choices[idx]
                
                # Check if it's a valid choice
                if response in field.choices:
                    return response
                
                console.print(f"[red]Invalid choice. Please enter 1-{len(field.choices)} or a valid option.[/red]")
                
            except KeyboardInterrupt:
                raise
    
    def _collect_number_field(self, field: FormField, current_value: Any = None) -> Union[int, float]:
        """Collect numeric field value.
        
        Args:
            field: Form field configuration
            current_value: Current field value
            
        Returns:
            Numeric value
        """
        default = current_value if current_value is not None else field.default
        
        while True:
            try:
                response = Prompt.ask(field.title, default=str(default) if default is not None else None)
                
                if not response and not field.required:
                    return None
                
                # Try to convert to number
                try:
                    value = float(response) if '.' in response else int(response)
                    
                    # Validate range
                    if field.validation:
                        if 'minimum' in field.validation and value < field.validation['minimum']:
                            console.print(f"[red]Value must be at least {field.validation['minimum']}[/red]")
                            continue
                        if 'maximum' in field.validation and value > field.validation['maximum']:
                            console.print(f"[red]Value must be no more than {field.validation['maximum']}[/red]")
                            continue
                    
                    return value
                    
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")
                    
            except KeyboardInterrupt:
                raise
    
    def _collect_string_field(self, field: FormField, current_value: Any = None) -> str:
        """Collect string field value.
        
        Args:
            field: Form field configuration
            current_value: Current field value
            
        Returns:
            String value
        """
        default = current_value if current_value is not None else field.default
        
        while True:
            try:
                response = Prompt.ask(field.title, default=str(default) if default is not None else None)
                
                if not response and not field.required:
                    return None
                
                if not response and field.required:
                    console.print("[red]This field is required[/red]")
                    continue
                
                # Validate string
                if field.validation:
                    if 'min_length' in field.validation and len(response) < field.validation['min_length']:
                        console.print(f"[red]Must be at least {field.validation['min_length']} characters[/red]")
                        continue
                    if 'max_length' in field.validation and len(response) > field.validation['max_length']:
                        console.print(f"[red]Must be no more than {field.validation['max_length']} characters[/red]")
                        continue
                    if 'pattern' in field.validation:
                        import re
                        if not re.match(field.validation['pattern'], response):
                            console.print("[red]Input doesn't match required pattern[/red]")
                            continue
                
                return response
                
            except KeyboardInterrupt:
                raise
    
    def _collect_array_field(self, field: FormField, current_value: Any = None) -> List[str]:
        """Collect array field value.
        
        Args:
            field: Form field configuration
            current_value: Current field value
            
        Returns:
            List of values
        """
        if current_value and isinstance(current_value, list):
            console.print(f"  Current values: {', '.join(map(str, current_value))}")
        
        console.print("  Enter values one per line (empty line to finish):")
        
        values = []
        while True:
            try:
                value = Prompt.ask(f"  Item {len(values) + 1}", default="")
                if not value:
                    break
                values.append(value)
            except KeyboardInterrupt:
                raise
        
        return values if values else (current_value if current_value else [])
    
    def display_inputs_summary(self, inputs: Dict[str, Any]) -> None:
        """Display summary of collected inputs.
        
        Args:
            inputs: Dictionary of input values
        """
        if not inputs:
            console.print("[dim]No inputs collected[/dim]")
            return
        
        table = Table(title="📝 Input Summary", border_style="blue")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Type", style="yellow", justify="center")
        
        for field_name, value in inputs.items():
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            
            value_type = type(value).__name__
            table.add_row(field_name, value_str, value_type)
        
        console.print(table)
    
    def confirm_execution(self, schema: CatalogItemSchema, 
                         inputs: Dict[str, Any],
                         deployment_name: str,
                         project_id: str) -> bool:
        """Confirm execution with user.
        
        Args:
            schema: Catalog item schema
            inputs: Input values
            deployment_name: Deployment name
            project_id: Project ID
            
        Returns:
            True if user confirms execution
        """
        console.print(Panel(
            f"[bold]Catalog Item:[/bold] {schema.catalog_item_info.name}\\n"
            f"[bold]Type:[/bold] {schema.catalog_item_info.type}\\n"
            f"[bold]Deployment Name:[/bold] {deployment_name}\\n"
            f"[bold]Project ID:[/bold] {project_id}\\n"
            f"[bold]Input Fields:[/bold] {len(inputs)}",
            title="🚀 Execution Summary",
            border_style="yellow"
        ))
        
        self.display_inputs_summary(inputs)
        
        return Confirm.ask("\\n[bold]Proceed with execution?[/bold]", default=False)
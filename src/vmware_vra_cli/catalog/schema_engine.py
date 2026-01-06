"""Core schema interpretation engine for dynamic catalog operations."""

import re
from typing import Dict, Any, List, Optional, Tuple
from rich.console import Console

from ..models.catalog_schema import (
    CatalogItemSchema, SchemaProperty, FormField, 
    ValidationResult, ExecutionContext
)

console = Console()


class SchemaEngine:
    """Engine for interpreting and processing catalog item schemas."""
    
    def __init__(self):
        """Initialize schema engine."""
        self.variable_pattern = re.compile(r'\{\{(\w+)\}\}')
    
    def extract_form_fields(self, schema: CatalogItemSchema) -> List[FormField]:
        """Extract form fields from schema for interactive input.
        
        Args:
            schema: Catalog item schema
            
        Returns:
            List of form fields ordered by dependencies
        """
        fields = []
        dependencies = {}
        
        for prop_name, prop_def in schema.schema_definition.properties.items():
            field = self._create_form_field(prop_name, prop_def, schema.schema_definition.required)
            fields.append(field)
            
            # Extract dependencies from dynamic sources
            if field.dynamic_source:
                deps = self._extract_dependencies(field.dynamic_source)
                if deps:
                    dependencies[prop_name] = deps
                    field.depends_on = deps
        
        # Sort fields by dependencies (fields without deps first)
        return self._sort_fields_by_dependencies(fields, dependencies)
    
    def _create_form_field(self, name: str, prop: SchemaProperty, required_fields: List[str]) -> FormField:
        """Create form field from schema property.
        
        Args:
            name: Property name
            prop: Schema property definition
            required_fields: List of required field names
            
        Returns:
            Form field configuration
        """
        # Build validation rules
        validation = {}
        if prop.minimum is not None:
            validation['minimum'] = prop.minimum
        if prop.maximum is not None:
            validation['maximum'] = prop.maximum
        if prop.minLength is not None:
            validation['min_length'] = prop.minLength
        if prop.maxLength is not None:
            validation['max_length'] = prop.maxLength
        if prop.pattern:
            validation['pattern'] = prop.pattern
        
        return FormField(
            name=name,
            title=prop.title or name.replace('_', ' ').title(),
            description=prop.description,
            type=prop.type,
            required=name in required_fields,
            default=prop.default,
            choices=prop.enum,
            validation=validation if validation else None,
            dynamic_source=prop.data or prop.dynamic_default
        )
    
    def _extract_dependencies(self, dynamic_source: str) -> List[str]:
        """Extract variable dependencies from dynamic source strings.
        
        Args:
            dynamic_source: Dynamic source string with variables
            
        Returns:
            List of dependent field names
        """
        matches = self.variable_pattern.findall(dynamic_source)
        return list(set(matches))  # Remove duplicates
    
    def _sort_fields_by_dependencies(self, fields: List[FormField], 
                                   dependencies: Dict[str, List[str]]) -> List[FormField]:
        """Sort fields by dependency order.
        
        Args:
            fields: List of form fields
            dependencies: Field dependency mapping
            
        Returns:
            Fields sorted by dependency order
        """
        sorted_fields = []
        field_map = {f.name: f for f in fields}
        processed = set()
        
        def add_field_and_deps(field_name: str):
            """Recursively add field and its dependencies."""
            if field_name in processed or field_name not in field_map:
                return
                
            # Add dependencies first
            if field_name in dependencies:
                for dep in dependencies[field_name]:
                    add_field_and_deps(dep)
            
            # Add the field itself
            if field_name not in processed:
                sorted_fields.append(field_map[field_name])
                processed.add(field_name)
        
        # Process all fields
        for field in fields:
            add_field_and_deps(field.name)
        
        return sorted_fields
    
    def validate_inputs(self, schema: CatalogItemSchema, 
                       inputs: Dict[str, Any]) -> ValidationResult:
        """Validate inputs against schema.
        
        Args:
            schema: Catalog item schema
            inputs: User input values
            
        Returns:
            Validation result with errors and processed inputs
        """
        errors = []
        warnings = []
        processed_inputs = {}
        
        # Check required fields
        for required_field in schema.schema_definition.required:
            if required_field not in inputs or inputs[required_field] is None:
                errors.append(f"Required field '{required_field}' is missing")
        
        # Validate each input
        for field_name, value in inputs.items():
            if field_name not in schema.schema_definition.properties:
                warnings.append(f"Unknown field '{field_name}' will be ignored")
                continue
                
            prop = schema.schema_definition.properties[field_name]
            field_errors = self._validate_field_value(field_name, value, prop)
            errors.extend(field_errors)
            
            # Convert and store processed value
            processed_value = self._convert_field_value(value, prop)
            if processed_value is not None:
                processed_inputs[field_name] = processed_value
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            processed_inputs=processed_inputs
        )
    
    def _validate_field_value(self, field_name: str, value: Any, 
                            prop: SchemaProperty) -> List[str]:
        """Validate a single field value.
        
        Args:
            field_name: Field name
            value: Field value
            prop: Schema property definition
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if value is None:
            return errors
        
        # Type validation
        expected_type = prop.type
        if expected_type == 'string' and not isinstance(value, str):
            errors.append(f"Field '{field_name}' must be a string")
        elif expected_type == 'number' and not isinstance(value, (int, float)):
            errors.append(f"Field '{field_name}' must be a number")
        elif expected_type == 'boolean' and not isinstance(value, bool):
            errors.append(f"Field '{field_name}' must be a boolean")
        elif expected_type == 'array' and not isinstance(value, list):
            errors.append(f"Field '{field_name}' must be an array")
        
        # String validations
        if expected_type == 'string' and isinstance(value, str):
            if prop.minLength and len(value) < prop.minLength:
                errors.append(f"Field '{field_name}' must be at least {prop.minLength} characters")
            if prop.maxLength and len(value) > prop.maxLength:
                errors.append(f"Field '{field_name}' must be no more than {prop.maxLength} characters")
            if prop.pattern and not re.match(prop.pattern, value):
                errors.append(f"Field '{field_name}' does not match required pattern")
            if prop.enum and value not in prop.enum:
                errors.append(f"Field '{field_name}' must be one of: {', '.join(prop.enum)}")
        
        # Number validations
        if expected_type == 'number' and isinstance(value, (int, float)):
            if prop.minimum is not None and value < prop.minimum:
                errors.append(f"Field '{field_name}' must be at least {prop.minimum}")
            if prop.maximum is not None and value > prop.maximum:
                errors.append(f"Field '{field_name}' must be no more than {prop.maximum}")
        
        return errors
    
    def _convert_field_value(self, value: Any, prop: SchemaProperty) -> Any:
        """Convert field value to appropriate type.
        
        Args:
            value: Raw input value
            prop: Schema property definition
            
        Returns:
            Converted value
        """
        if value is None:
            return None
        
        try:
            if prop.type == 'number':
                return float(value) if '.' in str(value) else int(value)
            elif prop.type == 'boolean':
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ('true', '1', 'yes', 'on')
            elif prop.type == 'string':
                return str(value)
            elif prop.type == 'array':
                if isinstance(value, list):
                    return value
                # Try to parse comma-separated string
                return [item.strip() for item in str(value).split(',')]
        except (ValueError, TypeError):
            return value
        
        return value
    
    def generate_request_payload(self, context: ExecutionContext) -> Dict[str, Any]:
        """Generate request payload for catalog item execution.
        
        Args:
            context: Execution context
            
        Returns:
            Request payload dictionary
        """
        payload = {
            "deploymentName": context.deployment_name or f"deployment-{context.catalog_schema.catalog_item_info.name.lower().replace(' ', '-')}",
            "projectId": context.project_id,
            "catalogItemId": context.catalog_schema.catalog_item_info.id,
            "inputs": context.inputs
        }
        
        # Add version if available
        if context.catalog_schema.catalog_item_info.version:
            payload["catalogItemVersion"] = context.catalog_schema.catalog_item_info.version
        
        return payload
    
    def resolve_dynamic_values(self, schema: CatalogItemSchema, 
                             current_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve dynamic default values and data sources.
        
        Args:
            schema: Catalog item schema
            current_inputs: Current input values for variable substitution
            
        Returns:
            Dictionary of resolved dynamic values
        """
        resolved = {}
        
        for prop_name, prop in schema.schema_definition.properties.items():
            # Skip if we already have a value
            if prop_name in current_inputs:
                continue
                
            # Handle dynamic defaults
            if prop.dynamic_default:
                resolved_source = self._substitute_variables(
                    prop.dynamic_default, current_inputs
                )
                # Note: In a real implementation, you'd make API calls here
                # For now, we'll return the resolved template as a placeholder
                resolved[prop_name] = f"[DYNAMIC: {resolved_source}]"
                
        return resolved
    
    def _substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in template string.
        
        Args:
            template: Template string with {{variable}} placeholders
            variables: Variable values
            
        Returns:
            String with variables substituted
        """
        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, f"{{{{ {var_name} }}}}"))
        
        return self.variable_pattern.sub(replace_var, template)
    
    def get_execution_summary(self, context: ExecutionContext) -> Dict[str, Any]:
        """Get execution summary for display.
        
        Args:
            context: Execution context
            
        Returns:
            Summary dictionary
        """
        schema = context.catalog_schema
        return {
            "catalog_item": {
                "name": schema.catalog_item_info.name,
                "type": schema.catalog_item_info.type,
                "id": schema.catalog_item_info.id
            },
            "deployment": {
                "name": context.deployment_name,
                "project_id": context.project_id
            },
            "inputs": context.inputs,
            "dry_run": context.dry_run
        }
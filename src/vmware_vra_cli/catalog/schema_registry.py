"""Schema registry for loading and managing catalog item schemas."""

import json
import glob
from pathlib import Path
from typing import Dict, List, Optional, Iterator
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..models.catalog_schema import CatalogItemSchema, CatalogItemInfo

console = Console()


class SchemaRegistry:
    """Registry for managing catalog item schemas."""
    
    def __init__(self, schema_dirs: Optional[List[Path]] = None):
        """Initialize schema registry.
        
        Args:
            schema_dirs: List of directories to search for schema files
        """
        self.schema_dirs = schema_dirs or []
        self._schemas: Dict[str, CatalogItemSchema] = {}
        self._loaded = False
        
    def add_schema_directory(self, path: Path) -> None:
        """Add a directory to search for schema files.
        
        Args:
            path: Directory path containing schema JSON files
        """
        if path.exists() and path.is_dir():
            self.schema_dirs.append(path)
        else:
            console.print(f"[yellow]Warning: Schema directory not found: {path}[/yellow]")
    
    def load_schemas(self, pattern: str = "*_schema.json", force_reload: bool = False) -> int:
        """Load all schemas from configured directories.
        
        Args:
            pattern: File pattern to match schema files
            force_reload: Force reload even if already loaded
            
        Returns:
            Number of schemas loaded
        """
        if self._loaded and not force_reload:
            return len(self._schemas)
            
        self._schemas.clear()
        loaded_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading schemas...", total=None)
            
            for schema_dir in self.schema_dirs:
                schema_files = list(schema_dir.glob(pattern))
                progress.update(task, description=f"Loading from {schema_dir.name}...")
                
                for schema_file in schema_files:
                    try:
                        schema = self._load_schema_file(schema_file)
                        if schema:
                            self._schemas[schema.catalog_item_info.id] = schema
                            loaded_count += 1
                    except Exception as e:
                        console.print(f"[red]Error loading {schema_file.name}: {e}[/red]")
                        
        self._loaded = True
        console.print(f"[green]✅ Loaded {loaded_count} catalog schemas[/green]")
        return loaded_count
    
    def _load_schema_file(self, file_path: Path) -> Optional[CatalogItemSchema]:
        """Load a single schema file.
        
        Args:
            file_path: Path to schema JSON file
            
        Returns:
            Loaded schema or None if failed
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return CatalogItemSchema(**data)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to parse {file_path.name}: {e}[/yellow]")
            return None
    
    def get_schema(self, catalog_item_id: str) -> Optional[CatalogItemSchema]:
        """Get schema by catalog item ID.
        
        Args:
            catalog_item_id: Catalog item ID
            
        Returns:
            Schema if found, None otherwise
        """
        if not self._loaded:
            self.load_schemas()
        return self._schemas.get(catalog_item_id)
    
    def list_schemas(self, 
                    item_type: Optional[str] = None,
                    name_filter: Optional[str] = None) -> List[CatalogItemInfo]:
        """List available schemas with optional filtering.
        
        Args:
            item_type: Filter by catalog item type
            name_filter: Filter by name (case-insensitive substring match)
            
        Returns:
            List of catalog item info objects
        """
        if not self._loaded:
            self.load_schemas()
            
        schemas = []
        for schema in self._schemas.values():
            # Type filter
            if item_type and schema.catalog_item_info.type != item_type:
                continue
                
            # Name filter
            if name_filter and name_filter.lower() not in schema.catalog_item_info.name.lower():
                continue
                
            schemas.append(schema.catalog_item_info)
        
        return sorted(schemas, key=lambda x: x.name)
    
    def search_schemas(self, query: str) -> List[CatalogItemInfo]:
        """Search schemas by name or description.
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching catalog item info objects
        """
        if not self._loaded:
            self.load_schemas()
            
        query_lower = query.lower()
        matches = []
        
        for schema in self._schemas.values():
            info = schema.catalog_item_info
            # Search in name and description
            if (query_lower in info.name.lower() or 
                (info.description and query_lower in info.description.lower())):
                matches.append(info)
        
        return sorted(matches, key=lambda x: x.name)
    
    def get_schemas_by_type(self, item_type: str) -> Dict[str, CatalogItemSchema]:
        """Get all schemas of a specific type.
        
        Args:
            item_type: Catalog item type
            
        Returns:
            Dictionary mapping item ID to schema
        """
        if not self._loaded:
            self.load_schemas()
            
        return {
            item_id: schema for item_id, schema in self._schemas.items()
            if schema.catalog_item_info.type == item_type
        }
    
    def validate_schema_directory(self, path: Path) -> Dict[str, any]:
        """Validate a schema directory and return statistics.
        
        Args:
            path: Directory path to validate
            
        Returns:
            Dictionary with validation statistics
        """
        if not path.exists() or not path.is_dir():
            return {"error": f"Directory not found: {path}"}
            
        schema_files = list(path.glob("*_schema.json"))
        valid_schemas = 0
        invalid_schemas = 0
        errors = []
        
        for schema_file in schema_files:
            try:
                schema = self._load_schema_file(schema_file)
                if schema:
                    valid_schemas += 1
                else:
                    invalid_schemas += 1
            except Exception as e:
                invalid_schemas += 1
                errors.append(f"{schema_file.name}: {str(e)}")
        
        return {
            "directory": str(path),
            "total_files": len(schema_files),
            "valid_schemas": valid_schemas,
            "invalid_schemas": invalid_schemas,
            "errors": errors
        }
    
    def export_schema_summary(self) -> Dict[str, any]:
        """Export summary of loaded schemas.
        
        Returns:
            Dictionary with schema statistics
        """
        if not self._loaded:
            self.load_schemas()
        
        type_counts = {}
        total_schemas = len(self._schemas)
        
        for schema in self._schemas.values():
            item_type = schema.catalog_item_info.type
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        return {
            "total_schemas": total_schemas,
            "types": type_counts,
            "schema_ids": list(self._schemas.keys()),
            "directories": [str(d) for d in self.schema_dirs]
        }
    
    def reload(self) -> int:
        """Reload all schemas from disk.
        
        Returns:
            Number of schemas loaded
        """
        return self.load_schemas(force_reload=True)
    
    def __len__(self) -> int:
        """Get number of loaded schemas."""
        if not self._loaded:
            self.load_schemas()
        return len(self._schemas)
    
    def __contains__(self, catalog_item_id: str) -> bool:
        """Check if schema exists for given catalog item ID."""
        if not self._loaded:
            self.load_schemas()
        return catalog_item_id in self._schemas
    
    def __iter__(self) -> Iterator[CatalogItemSchema]:
        """Iterate over all loaded schemas."""
        if not self._loaded:
            self.load_schemas()
        return iter(self._schemas.values())


# Global schema registry instance
registry = SchemaRegistry()
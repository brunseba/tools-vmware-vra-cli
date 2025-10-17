#!/usr/bin/env python3
"""Test script for the generic catalog implementation."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from vmware_vra_cli.catalog.schema_registry import registry
    from vmware_vra_cli.catalog.schema_engine import SchemaEngine
    from vmware_vra_cli.catalog.form_builder import FormBuilder
    
    print("✅ All imports successful!")
    
    # Test schema loading
    schema_dir = Path("./inputs/schema_exports")
    if schema_dir.exists():
        registry.add_schema_directory(schema_dir)
        count = registry.load_schemas()
        print(f"✅ Loaded {count} schemas from {schema_dir}")
        
        # Test schema listing
        schemas = registry.list_schemas()
        print(f"✅ Found {len(schemas)} catalog items:")
        
        for i, schema in enumerate(schemas[:5]):  # Show first 5
            print(f"  {i+1}. {schema.name} ({schema.type})")
        
        if len(schemas) > 5:
            print(f"  ... and {len(schemas) - 5} more")
        
        # Test schema engine with first schema
        if schemas:
            test_schema = registry.get_schema(schemas[0].id)
            if test_schema:
                engine = SchemaEngine()
                fields = engine.extract_form_fields(test_schema)
                print(f"✅ Extracted {len(fields)} form fields from '{test_schema.catalog_item_info.name}'")
                
                # Show field details
                for field in fields[:3]:  # Show first 3 fields
                    print(f"  - {field.name}: {field.type} {'(required)' if field.required else '(optional)'}")
        
        print("\n🎉 Implementation verification complete!")
        print("\nYou can now use the generic catalog system with:")
        print("1. Load schemas: registry.load_schemas()")
        print("2. List items: registry.list_schemas()")
        print("3. Execute items: Use the CLI commands once dependencies are installed")
        
    else:
        print(f"❌ Schema directory not found: {schema_dir}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This is expected if dependencies aren't installed yet.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
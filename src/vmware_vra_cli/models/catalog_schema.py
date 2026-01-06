"""Pydantic models for VMware vRA catalog item schemas."""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class CatalogItemType(str, Enum):
    """Catalog item types."""
    AUTOMATION_TEMPLATE = "VMware Aria Automation Templates"
    ORCHESTRATOR_WORKFLOW = "Automation Orchestrator Workflow"


class CatalogItemInfo(BaseModel):
    """Catalog item metadata."""
    id: str
    name: str
    type: CatalogItemType
    status: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None


class SchemaProperty(BaseModel):
    """JSON Schema property definition."""
    type: str
    title: Optional[str] = None
    description: Optional[str] = None
    default: Optional[Any] = None
    enum: Optional[List[str]] = None
    pattern: Optional[str] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    encrypted: Optional[bool] = None
    
    # Dynamic features
    data: Optional[str] = Field(None, alias="$data")
    dynamic_default: Optional[str] = Field(None, alias="$dynamicDefault")
    
    # Array properties
    items: Optional[Dict[str, Any]] = None


class JsonSchema(BaseModel):
    """JSON Schema definition."""
    type: str = "object"
    properties: Dict[str, SchemaProperty]
    required: Optional[List[str]] = []
    encrypted: Optional[bool] = None


class CatalogItemSchema(BaseModel):
    """Complete catalog item schema export."""
    catalog_item_info: CatalogItemInfo
    export_timestamp: datetime
    schema_definition: JsonSchema = Field(alias="schema")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FormField(BaseModel):
    """Form field for interactive input."""
    name: str
    title: str
    description: Optional[str] = None
    type: str
    required: bool = False
    default: Optional[Any] = None
    choices: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None
    depends_on: Optional[List[str]] = None
    dynamic_source: Optional[str] = None


class CatalogRequest(BaseModel):
    """Request payload for catalog item execution."""
    catalog_item_id: str
    project_id: str
    deployment_name: Optional[str] = None
    inputs: Dict[str, Any] = {}
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class ValidationResult(BaseModel):
    """Schema validation result."""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    processed_inputs: Optional[Dict[str, Any]] = None


class ExecutionContext(BaseModel):
    """Context for schema-based execution."""
    catalog_schema: CatalogItemSchema
    inputs: Dict[str, Any]
    project_id: str
    deployment_name: Optional[str] = None
    dry_run: bool = False
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
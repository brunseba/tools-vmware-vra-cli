"""Catalog endpoints for MCP server."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from vmware_vra_cli.rest_server.models import (
    CatalogItemsRequest,
    CatalogItemsResponse,
    CatalogItemResponse,
    CatalogSchemaResponse,
    CatalogRequestRequest,
    CatalogRequestResponse,
)
from vmware_vra_cli.rest_server.utils import get_catalog_client, handle_client_error

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/items", response_model=CatalogItemsResponse)
async def list_catalog_items(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    page_size: int = Query(100, ge=1, le=2000, description="Number of items per page"),
    first_page_only: bool = Query(False, description="Fetch only the first page"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """List available catalog items."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Catalog items request - project_id: {project_id}, page_size: {page_size}")
        client = get_catalog_client(verbose=verbose)
        logger.info(f"Client obtained: {type(client).__name__}")
        
        items = client.list_catalog_items(project_id=project_id)
        logger.info(f"Catalog items retrieved: {len(items)} items")
        
        # Convert Pydantic objects to dictionaries
        items_data = []
        for item in items:
            if hasattr(item, 'dict'):
                # It's a Pydantic object, convert to dict
                items_data.append(item.dict())
            elif isinstance(item, dict):
                # It's already a dict (from mock data)
                items_data.append(item)
            else:
                # Unknown type, try to convert
                logger.warning(f"Unknown item type: {type(item)}")
                items_data.append(item if isinstance(item, dict) else {})
        
        logger.info(f"Catalog items converted to {len(items_data)} dictionaries")
        
        return CatalogItemsResponse(
            success=True,
            message=f"Retrieved {len(items)} catalog items",
            items=items_data,
            total_count=len(items),
            page_info={
                "page_size": page_size,
                "first_page_only": first_page_only,
                "project_filter": project_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing catalog items: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise handle_client_error("list catalog items", e)


@router.get("/items/{item_id}", response_model=CatalogItemResponse)
async def get_catalog_item(
    item_id: str,
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Get details of a specific catalog item."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        item = client.get_catalog_item(item_id)
        
        return CatalogItemResponse(
            success=True,
            message=f"Retrieved catalog item {item_id}",
            item=item.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"get catalog item {item_id}", e)


@router.get("/items/{item_id}/schema", response_model=CatalogSchemaResponse)
async def get_catalog_item_schema(
    item_id: str,
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Get the request schema for a catalog item."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        schema = client.get_catalog_item_schema(item_id)
        
        return CatalogSchemaResponse(
            success=True,
            message=f"Retrieved schema for catalog item {item_id}",
            item_schema=schema
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"get catalog item schema {item_id}", e)


@router.post("/items/{item_id}/request", response_model=CatalogRequestResponse)
async def request_catalog_item(
    item_id: str,
    request_data: CatalogRequestRequest,
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Request a catalog item."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        # Prepare inputs dictionary
        inputs_dict = request_data.inputs or {}
        if request_data.name:
            inputs_dict['deploymentName'] = request_data.name
        
        result = client.request_catalog_item(
            item_id,
            inputs_dict,
            request_data.project_id,
            request_data.reason
        )
        
        return CatalogRequestResponse(
            success=True,
            message="Catalog item request submitted successfully",
            deployment_id=result.get('deploymentId'),
            request_id=result.get('requestId')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"request catalog item {item_id}", e)

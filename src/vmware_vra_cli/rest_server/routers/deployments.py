"""Deployments endpoints for MCP server."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from vmware_vra_cli.rest_server.models import (
    DeploymentsResponse,
    DeploymentResponse,
    DeploymentResourcesResponse,
    BaseResponse,
)
from vmware_vra_cli.rest_server.utils import get_catalog_client, handle_client_error

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.get("", response_model=DeploymentsResponse)
async def list_deployments(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page_size: int = Query(100, ge=1, le=2000, description="Number of items per page"),
    first_page_only: bool = Query(False, description="Fetch only the first page"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """List deployments."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        deployments = client.list_deployments(
            project_id=project_id,
            status=status,
            page_size=page_size,
            fetch_all=not first_page_only
        )
        
        return DeploymentsResponse(
            success=True,
            message=f"Retrieved {len(deployments)} deployments",
            deployments=deployments,
            total_count=len(deployments),
            page_info={
                "page_size": page_size,
                "first_page_only": first_page_only,
                "project_filter": project_id,
                "status_filter": status
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("list deployments", e)


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: str,
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Get deployment details."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        deployment = client.get_deployment(deployment_id)
        
        return DeploymentResponse(
            success=True,
            message=f"Retrieved deployment {deployment_id}",
            deployment=deployment
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"get deployment {deployment_id}", e)


@router.delete("/{deployment_id}", response_model=BaseResponse)
async def delete_deployment(
    deployment_id: str,
    confirm: bool = Query(False, description="Skip confirmation"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Delete a deployment."""
    try:
        if not confirm:
            raise HTTPException(
                status_code=400,
                detail="Deployment deletion requires confirmation. Set confirm=true to proceed."
            )
            
        client = get_catalog_client(verbose=verbose)
        
        result = client.delete_deployment(deployment_id)
        
        return BaseResponse(
            success=True,
            message=f"Deployment {deployment_id} deletion initiated"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"delete deployment {deployment_id}", e)


@router.get("/{deployment_id}/resources", response_model=DeploymentResourcesResponse)
async def get_deployment_resources(
    deployment_id: str,
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Get deployment resources."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        resources = client.get_deployment_resources(deployment_id)
        
        return DeploymentResourcesResponse(
            success=True,
            message=f"Retrieved resources for deployment {deployment_id}",
            resources=resources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"get deployment resources {deployment_id}", e)

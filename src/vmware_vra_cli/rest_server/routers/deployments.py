"""Deployments endpoints for MCP server."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from vmware_vra_cli.rest_server.models import (
    DeploymentsResponse,
    DeploymentResponse,
    DeploymentResourcesResponse,
    BaseResponse,
)
from vmware_vra_cli.rest_server.utils import get_catalog_client, handle_client_error
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.get("", response_model=DeploymentsResponse)
async def list_deployments(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    deleted: Optional[bool] = Query(None, description="Filter deleted deployments (true=only deleted, false=only active)"),
    page_size: int = Query(100, ge=1, le=2000, description="Number of items per page"),
    first_page_only: bool = Query(False, description="Fetch only the first page"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """List deployments."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        # Build params for API call
        list_params = {
            'project_id': project_id,
            'status': status,
            'page_size': page_size,
            'fetch_all': not first_page_only
        }
        
        # Add deleted filter if specified
        if deleted is not None:
            list_params['deleted'] = deleted
            if verbose:
                print(f"[DEBUG] Requesting deployments with deleted={deleted}")
        
        deployments = client.list_deployments(**list_params)
        
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


@router.get("/resources/all", response_model=Dict[str, Any])
async def get_all_deployment_resources(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type (e.g., Cloud.vSphere.Machine)"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Get all resources across all deployments (optimized bulk endpoint)."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        # Get all deployments
        deployments = client.list_deployments(
            project_id=project_id,
            page_size=1000,
            fetch_all=True
        )
        
        if not deployments:
            return {
                "success": True,
                "message": "No deployments found",
                "resources": [],
                "total_count": 0,
            }
        
        # Fetch resources in parallel batches
        all_resources = []
        batch_size = 10
        
        def fetch_resources(deployment):
            try:
                resources = client.get_deployment_resources(deployment['id'])
                # Add deployment context to each resource
                for resource in resources:
                    resource['deploymentId'] = deployment['id']
                    resource['deploymentName'] = deployment.get('name', 'Unknown')
                return resources
            except Exception as e:
                print(f"Failed to fetch resources for deployment {deployment['id']}: {e}")
                return []
        
        # Process deployments in batches
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            loop = asyncio.get_event_loop()
            for i in range(0, len(deployments), batch_size):
                batch = deployments[i:i + batch_size]
                batch_results = await loop.run_in_executor(
                    None,
                    lambda: list(executor.map(fetch_resources, batch))
                )
                for resources in batch_results:
                    all_resources.extend(resources)
        
        # Filter by resource type if specified
        if resource_type:
            all_resources = [
                r for r in all_resources
                if r.get('type') == resource_type
            ]
        
        return {
            "success": True,
            "message": f"Retrieved {len(all_resources)} resources from {len(deployments)} deployments",
            "resources": all_resources,
            "total_count": len(all_resources),
            "deployments_scanned": len(deployments),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("get all deployment resources", e)


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

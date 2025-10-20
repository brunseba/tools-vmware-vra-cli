"""Workflows endpoints for MCP server."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from vmware_vra_cli.rest_server.models import (
    WorkflowsRequest,
    WorkflowsResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowSchemaResponse,
    BaseResponse,
)
from vmware_vra_cli.rest_server.utils import get_catalog_client, handle_client_error

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("", response_model=WorkflowsResponse)
async def list_workflows(
    page_size: int = Query(100, ge=1, le=2000, description="Number of items per page"),
    first_page_only: bool = Query(False, description="Fetch only the first page"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """List available workflows.
    
    By default, this command fetches all workflows across all pages.
    Use first_page_only=true to limit to just the first page for faster results.
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        workflows = client.list_workflows(
            page_size=page_size,
            fetch_all=not first_page_only
        )
        
        return WorkflowsResponse(
            success=True,
            message=f"Retrieved {len(workflows)} workflows",
            workflows=workflows,
            total_count=len(workflows),
            page_info={
                "page_size": page_size,
                "first_page_only": first_page_only
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("list workflows", e)


@router.get("/{workflow_id}", response_model=WorkflowSchemaResponse)
async def get_workflow_schema(
    workflow_id: str,
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Get workflow input/output schema."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        schema = client.get_workflow_schema(workflow_id)
        
        return WorkflowSchemaResponse(
            success=True,
            message=f"Workflow schema retrieved for {workflow_id}",
            workflow_schema=schema
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"get workflow schema {workflow_id}", e)


@router.post("/{workflow_id}/run", response_model=WorkflowRunResponse)
async def run_workflow(
    workflow_id: str,
    request_data: WorkflowRunRequest,
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Execute a workflow.
    
    Submit inputs to run a workflow and receive the execution details.
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        workflow_run = client.run_workflow(
            workflow_id,
            request_data.inputs or {}
        )
        
        return WorkflowRunResponse(
            success=True,
            message=f"Workflow {workflow_id} execution started",
            execution_id=workflow_run.id,
            state=workflow_run.state
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"run workflow {workflow_id}", e)


@router.get("/{workflow_id}/executions/{execution_id}", response_model=WorkflowRunResponse)
async def get_workflow_run(
    workflow_id: str,
    execution_id: str,
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Get workflow execution details."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        workflow_run = client.get_workflow_run(workflow_id, execution_id)
        
        return WorkflowRunResponse(
            success=True,
            message=f"Workflow execution {execution_id} details retrieved",
            execution_id=workflow_run.id,
            state=workflow_run.state
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"get workflow run {workflow_id}/{execution_id}", e)


@router.put("/{workflow_id}/executions/{execution_id}/cancel", response_model=BaseResponse)
async def cancel_workflow_run(
    workflow_id: str,
    execution_id: str,
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Cancel a running workflow execution."""
    try:
        client = get_catalog_client(verbose=verbose)
        
        result = client.cancel_workflow_run(workflow_id, execution_id)
        
        if result:
            return BaseResponse(
                success=True,
                message=f"Workflow execution {execution_id} cancellation requested"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to cancel workflow execution"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"cancel workflow run {workflow_id}/{execution_id}", e)
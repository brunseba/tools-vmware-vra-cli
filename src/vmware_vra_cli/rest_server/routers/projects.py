"""Projects router for VMware vRA project management."""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends

from ..models import BaseResponse, ProjectInfo, ProjectsResponse
from ..utils import get_catalog_client, handle_client_error


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectsResponse)
async def list_projects(
    verbose: bool = Query(False, description="Include detailed project information"),
):
    """List all available projects."""
    try:
        # Get projects from vRA (use existing list_deployments to get project info)
        client = get_catalog_client(verbose=verbose)
        deployments = client.list_deployments(fetch_all=True)
        
        # Extract unique projects from deployments
        projects_dict = {}
        for deployment in deployments:
            project_id = deployment.get("projectId", "")
            if project_id and project_id not in projects_dict:
                # Create project info from deployment data
                projects_dict[project_id] = ProjectInfo(
                    id=project_id,
                    name=deployment.get("projectName", project_id),
                    description=f"Project containing {deployment.get('name', 'deployments')}",
                    organizationId=deployment.get("organizationId")
                )

        projects = list(projects_dict.values())

        return ProjectsResponse(
            success=True,
            message="Projects retrieved successfully",
            timestamp=datetime.utcnow(),
            projects=projects,
            total_count=len(projects)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("list projects", e)


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    verbose: bool = Query(False, description="Include detailed project information"),
):
    """Get details of a specific project."""
    try:
        # Get deployments for this specific project
        client = get_catalog_client(verbose=verbose)
        deployments = client.list_deployments(
            project_id=project_id,
            fetch_all=True
        )
        
        if not deployments:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Get project info from first deployment
        first_deployment = deployments[0]
        project = ProjectInfo(
            id=project_id,
            name=first_deployment.get("projectName", project_id),
            description=f"Project with {len(deployments)} deployment(s)",
            organizationId=first_deployment.get("organizationId")
        )

        return {
            "success": True,
            "message": "Project retrieved successfully",
            "timestamp": datetime.utcnow(),
            "project": project
        }

    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error(f"get project {project_id}", e)

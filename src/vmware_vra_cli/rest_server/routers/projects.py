"""Projects router for VMware vRA project management."""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends

from ...api.client import VRAClient
from ..models import BaseResponse, ProjectInfo, ProjectsResponse
from ..utils import get_vra_client


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectsResponse)
async def list_projects(
    verbose: bool = Query(False, description="Include detailed project information"),
    vra_client: VRAClient = Depends(get_vra_client),
):
    """List all available projects."""
    try:
        # Get projects from vRA (use existing list_deployments to get project info)
        deployments_response = await vra_client.list_deployments(verbose=verbose)
        
        if not deployments_response.get("success", False):
            # If no deployments, return empty projects list
            return ProjectsResponse(
                success=True,
                message="No projects found",
                timestamp=datetime.utcnow(),
                projects=[],
                total_count=0
            )

        deployments = deployments_response.get("deployments", [])
        
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve projects: {str(e)}")


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    verbose: bool = Query(False, description="Include detailed project information"),
    vra_client: VRAClient = Depends(get_vra_client),
):
    """Get details of a specific project."""
    try:
        # Get deployments for this specific project
        deployments_response = await vra_client.list_deployments(
            project_id=project_id,
            verbose=verbose
        )
        
        if not deployments_response.get("success", False):
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        deployments = deployments_response.get("deployments", [])
        
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
        raise HTTPException(status_code=500, detail=f"Failed to retrieve project: {str(e)}")
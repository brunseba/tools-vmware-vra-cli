"""Projects API endpoints for VMware vRA project management."""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends

from ..api.client import VRAClient
from ..rest_server.models import BaseResponse, ProjectInfo, ProjectsResponse
from ..rest_server.utils import get_vra_client


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectsResponse)
async def list_projects(
    verbose: bool = Query(False, description="Include detailed project information"),
    vra_client: VRAClient = Depends(get_vra_client),
):
    """List all available projects."""
    try:
        # Get projects from vRA
        projects_response = await vra_client.get_projects(verbose=verbose)
        
        if not projects_response.success:
            raise HTTPException(status_code=500, detail=projects_response.message)

        projects_data = projects_response.data.get("projects", [])
        
        # Convert to ProjectInfo models
        projects = []
        for project_data in projects_data:
            project = ProjectInfo(
                id=project_data.get("id", ""),
                name=project_data.get("name", "Unknown Project"),
                description=project_data.get("description"),
                organizationId=project_data.get("organizationId")
            )
            projects.append(project)

        return ProjectsResponse(
            success=True,
            message="Projects retrieved successfully",
            timestamp=datetime.utcnow(),
            projects=projects,
            total_count=len(projects)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve projects: {str(e)}")


@router.get("/{project_id}", response_model=BaseResponse)
async def get_project(
    project_id: str,
    verbose: bool = Query(False, description="Include detailed project information"),
    vra_client: VRAClient = Depends(get_vra_client),
):
    """Get details of a specific project."""
    try:
        # Get specific project from vRA
        project_response = await vra_client.get_project(project_id, verbose=verbose)
        
        if not project_response.success:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        project_data = project_response.data.get("project", {})
        
        project = ProjectInfo(
            id=project_data.get("id", ""),
            name=project_data.get("name", "Unknown Project"),
            description=project_data.get("description"),
            organizationId=project_data.get("organizationId")
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
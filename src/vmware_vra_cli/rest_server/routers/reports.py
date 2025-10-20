"""Reports endpoints for MCP server."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from vmware_vra_cli.rest_server.models import (
    ActivityTimelineRequest,
    ActivityTimelineResponse,
    CatalogUsageRequest,
    CatalogUsageResponse,
    UnsyncReportRequest,
    UnsyncReportResponse,
    ResourcesUsageResponse,
    BaseResponse,
)
from vmware_vra_cli.rest_server.utils import get_catalog_client, handle_client_error

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/activity-timeline", response_model=ActivityTimelineResponse)
async def get_activity_timeline_report(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    days_back: int = Query(30, ge=1, le=365, description="Days back for activity timeline"),
    group_by: str = Query("day", pattern="^(day|week|month|year)$", description="Group results by time period"),
    statuses: str = Query(
        "CREATE_SUCCESSFUL,UPDATE_SUCCESSFUL,SUCCESSFUL,CREATE_FAILED,UPDATE_FAILED,FAILED,CREATE_INPROGRESS,UPDATE_INPROGRESS,INPROGRESS",
        description="Comma-separated list of statuses to include"
    ),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Generate an activity timeline for service catalog items.
    
    This timeline provides a historical view of deployment activities over a specified period,
    allowing you to see patterns, peak activity periods, and trends.
    
    Group options:
    - day: Daily activity (default)
    - week: Weekly activity (shows week number and year)
    - month: Monthly activity (shows month and year)
    - year: Yearly activity (shows annual totals)
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        # Convert status string to list
        include_statuses = [status.strip().upper() for status in statuses.split(',')]
        
        timeline_data = client.get_activity_timeline(
            project_id=project_id,
            days_back=days_back,
            include_statuses=include_statuses,
            group_by=group_by
        )
        
        return ActivityTimelineResponse(
            success=True,
            message=f"Activity timeline generated for {days_back} days",
            timeline_data=timeline_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("generate activity timeline", e)


@router.get("/catalog-usage", response_model=CatalogUsageResponse)
async def get_catalog_usage_report(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    include_zero: bool = Query(False, description="Include catalog items with zero deployments"),
    sort_by: str = Query("deployments", pattern="^(deployments|resources|name)$", description="Sort results by field"),
    detailed_resources: bool = Query(False, description="Fetch exact resource counts (slower but more accurate)"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Generate a usage report for service catalog items.
    
    This report shows:
    - All catalog items in the specified project (or all projects)
    - Number of deployments created from each catalog item
    - Total number of resources created from each catalog item
    - Success rate and other deployment statistics
    
    By default, only catalog items with at least one deployment are shown.
    Use include_zero=true to show all catalog items.
    Use detailed_resources=true to fetch exact resource counts (slower).
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        usage_stats = client.get_catalog_usage_stats(
            project_id=project_id,
            fetch_resource_counts=detailed_resources
        )
        
        # Filter out zero deployments unless requested
        if not include_zero:
            usage_stats = [stats for stats in usage_stats if stats['deployment_count'] > 0]
        
        # Sort results
        if sort_by == 'deployments':
            usage_stats.sort(key=lambda x: x['deployment_count'], reverse=True)
        elif sort_by == 'resources':
            usage_stats.sort(key=lambda x: x['resource_count'], reverse=True)
        elif sort_by == 'name':
            usage_stats.sort(key=lambda x: x['catalog_item'].name.lower())
        
        # Get all deployments for summary statistics
        all_deployments = client.list_deployments(project_id=project_id)
        
        # Convert to JSON-serializable format
        catalog_items_data = []
        for stat in usage_stats:
            catalog_items_data.append({
                'id': stat['catalog_item'].id,
                'name': stat['catalog_item'].name,
                'type': stat['catalog_item'].type.name,
                'deployment_count': stat['deployment_count'],
                'resource_count': stat['resource_count'],
                'success_count': stat['success_count'],
                'failed_count': stat['failed_count'],
                'in_progress_count': stat['in_progress_count'],
                'success_rate': stat['success_rate'],
                'status_breakdown': stat['status_counts']
            })
        
        # Calculate summary statistics
        total_catalog_deployments = sum(stat['deployment_count'] for stat in usage_stats)
        total_catalog_resources = sum(stat['resource_count'] for stat in usage_stats)
        active_items = len([s for s in usage_stats if s['deployment_count'] > 0])
        
        summary = {
            'total_catalog_items': len(usage_stats),
            'active_items': active_items,
            'total_deployments_system_wide': len(all_deployments),
            'catalog_linked_deployments': total_catalog_deployments,
            'unlinked_deployments': len(all_deployments) - total_catalog_deployments,
            'total_resources': total_catalog_resources,
            'average_deployments_per_active_item': (
                total_catalog_deployments / active_items if active_items > 0 else 0
            )
        }
        
        return CatalogUsageResponse(
            success=True,
            message=f"Catalog usage report generated for {len(usage_stats)} items",
            usage_stats=catalog_items_data,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("generate catalog usage report", e)


@router.get("/resources-usage", response_model=ResourcesUsageResponse)
async def get_resources_usage_report(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    detailed_resources: bool = Query(True, description="Fetch detailed resource information"),
    sort_by: str = Query("catalog-item", pattern="^(deployment-name|catalog-item|resource-count|status)$", description="Sort deployments by field"),
    group_by: str = Query("catalog-item", pattern="^(catalog-item|resource-type|deployment-status)$", description="Group results by field"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Generate a consolidated resources usage report across all deployments.
    
    This report provides a comprehensive view of all resources existing in each deployment,
    showing resource types, counts, states, and their relationship to catalog items.
    
    The report includes:
    - Total resource counts by type and status
    - Resource breakdown per deployment
    - Catalog item resource utilization
    - Unlinked deployments and their resources
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        report_data = client.get_resources_usage_report(
            project_id=project_id,
            include_detailed_resources=detailed_resources
        )
        
        return ResourcesUsageResponse(
            success=True,
            message=f"Resources usage report generated for {report_data['summary']['total_deployments']} deployments",
            report_data=report_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("generate resources usage report", e)


@router.get("/unsync", response_model=UnsyncReportResponse)
async def get_unsync_report(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    detailed_resources: bool = Query(False, description="Fetch exact resource counts (slower but more accurate)"),
    reason_filter: Optional[str] = Query(None, description="Filter by specific reason (e.g., missing_catalog_references, catalog_item_deleted)"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Generate a report of deployments that don't match to catalog items.
    
    This report identifies "unsynced" deployments that cannot be linked back to any
    catalog item in the system. These deployments may indicate:
    - Deployments created outside the service catalog
    - Catalog items that were deleted after deployment
    - Issues with deployment tracking or naming
    - Failed deployments that lost their catalog associations
    
    The report provides detailed analysis of why each deployment is unsynced
    and suggests potential remediation actions.
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        unsync_data = client.get_unsynced_deployments(
            project_id=project_id,
            fetch_resource_counts=detailed_resources
        )
        
        # Apply reason filter if specified
        if reason_filter:
            filtered_deployments = []
            for unsync in unsync_data['unsynced_deployments']:
                if unsync['analysis']['primary_reason'] == reason_filter:
                    filtered_deployments.append(unsync)
            
            unsync_data['unsynced_deployments'] = filtered_deployments
            # Recalculate summary for filtered data
            unsync_data['summary']['unsynced_deployments'] = len(filtered_deployments)
            unsync_data['summary']['unsynced_percentage'] = (
                len(filtered_deployments) / max(unsync_data['summary']['total_deployments'], 1) * 100
            )
        
        return UnsyncReportResponse(
            success=True,
            message=f"Unsync report generated - found {unsync_data['summary']['unsynced_deployments']} unsynced deployments",
            unsync_data=unsync_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("generate unsync report", e)
"""Analytics API endpoints for VMware vRA statistics and metrics."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from ..api.client import VRAClient
from ..rest_server.models import BaseResponse, AnalyticsStats, ActivityItem, ChartData, ResourceUsage
from ..rest_server.utils import get_vra_client


router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsStatsResponse(BaseResponse):
    """Analytics statistics response."""
    stats: AnalyticsStats


class ActivityTimelineResponse(BaseResponse):
    """Activity timeline response."""
    activities: List[ActivityItem]
    total_count: int


class ChartDataResponse(BaseResponse):
    """Chart data response."""
    chart_data: ChartData


class ResourceUsageResponse(BaseResponse):
    """Resource usage response."""
    usage: ResourceUsage


@router.get("/stats", response_model=AnalyticsStatsResponse)
async def get_analytics_stats(
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    vra_client: VRAClient = Depends(get_vra_client),
):
    """Get overall analytics statistics."""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        if time_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_range == "90d":
            start_date = end_date - timedelta(days=90)
        elif time_range == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)

        # Get deployments with date filtering
        deployments_response = await vra_client.list_deployments(
            project_id=project_id,
            verbose=True
        )
        
        if not deployments_response.success:
            raise HTTPException(status_code=500, detail=deployments_response.message)

        deployments = deployments_response.data.get("deployments", [])
        
        # Filter deployments by date range
        filtered_deployments = []
        for deployment in deployments:
            created_at = datetime.fromisoformat(deployment.get("createdAt", "").replace("Z", "+00:00"))
            if start_date <= created_at <= end_date:
                filtered_deployments.append(deployment)

        # Calculate statistics
        total_deployments = len(filtered_deployments)
        active_deployments = len([d for d in filtered_deployments 
                                 if d.get("status") == "CREATE_SUCCESSFUL"])
        failed_deployments = len([d for d in filtered_deployments 
                                 if "FAILED" in d.get("status", "")])
        
        # Get unique users (owners)
        users = set()
        for deployment in filtered_deployments:
            owner = deployment.get("ownedBy", deployment.get("createdBy", ""))
            if owner:
                users.add(owner)
        
        total_users = len(users)

        stats = AnalyticsStats(
            totalDeployments=total_deployments,
            activeDeployments=active_deployments,
            failedDeployments=failed_deployments,
            totalUsers=total_users,
            successRate=((total_deployments - failed_deployments) / total_deployments * 100) 
                       if total_deployments > 0 else 0.0
        )

        return AnalyticsStatsResponse(
            success=True,
            message="Analytics statistics retrieved successfully",
            timestamp=datetime.utcnow(),
            stats=stats
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")


@router.get("/timeline", response_model=ActivityTimelineResponse)
async def get_activity_timeline(
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    limit: int = Query(50, description="Maximum number of activities"),
    vra_client: VRAClient = Depends(get_vra_client),
):
    """Get activity timeline for recent deployments and operations."""
    try:
        # Get deployments
        deployments_response = await vra_client.list_deployments(
            project_id=project_id,
            verbose=True
        )
        
        if not deployments_response.success:
            raise HTTPException(status_code=500, detail=deployments_response.message)

        deployments = deployments_response.data.get("deployments", [])
        
        # Convert deployments to activity items
        activities = []
        for deployment in deployments[:limit]:
            status = deployment.get("status", "")
            
            # Determine activity type and action based on status
            if "CREATE" in status:
                activity_type = "deployment"
                if "SUCCESSFUL" in status:
                    action = "Created"
                elif "IN_PROGRESS" in status:
                    action = "Creating"
                elif "FAILED" in status:
                    action = "Failed"
                    activity_type = "failure"
                else:
                    action = "Unknown"
            elif "DELETE" in status:
                activity_type = "deletion"
                if "IN_PROGRESS" in status:
                    action = "Deleting"
                elif "FAILED" in status:
                    action = "Delete Failed"
                    activity_type = "failure"
                else:
                    action = "Deleted"
            else:
                activity_type = "deployment"
                action = "Updated"

            created_at = deployment.get("createdAt", "")
            if created_at:
                try:
                    created_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    time_ago = _format_time_ago(created_time)
                except:
                    time_ago = "Unknown time"
            else:
                time_ago = "Unknown time"

            activity = ActivityItem(
                id=deployment.get("id", ""),
                type=activity_type,
                action=action,
                resource=deployment.get("name", "Unknown Resource"),
                user=deployment.get("ownedBy", deployment.get("createdBy", "Unknown User")),
                time=time_ago,
                timestamp=created_at
            )
            activities.append(activity)

        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x.timestamp or "", reverse=True)

        return ActivityTimelineResponse(
            success=True,
            message="Activity timeline retrieved successfully",
            timestamp=datetime.utcnow(),
            activities=activities,
            total_count=len(activities)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve timeline: {str(e)}")


@router.get("/charts", response_model=ChartDataResponse)
async def get_chart_data(
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    vra_client: VRAClient = Depends(get_vra_client),
):
    """Get chart data for deployment trends and metrics."""
    try:
        # Get deployments
        deployments_response = await vra_client.list_deployments(
            project_id=project_id,
            verbose=True
        )
        
        if not deployments_response.success:
            raise HTTPException(status_code=500, detail=deployments_response.message)

        deployments = deployments_response.data.get("deployments", [])
        
        # Process deployments by time periods
        end_date = datetime.utcnow()
        if time_range == "7d":
            periods = 7
            delta = timedelta(days=1)
        elif time_range == "30d":
            periods = 30
            delta = timedelta(days=1)
        elif time_range == "90d":
            periods = 12  # 12 weeks
            delta = timedelta(days=7)
        else:  # 1y
            periods = 12  # 12 months
            delta = timedelta(days=30)

        # Initialize data arrays
        labels = []
        deployment_counts = [0] * periods
        success_counts = [0] * periods
        failure_counts = [0] * periods

        # Generate labels and count deployments
        for i in range(periods):
            period_end = end_date - (delta * i)
            period_start = period_end - delta
            
            if time_range == "7d" or time_range == "30d":
                labels.insert(0, period_end.strftime("%m/%d"))
            elif time_range == "90d":
                labels.insert(0, f"Week {periods-i}")
            else:
                labels.insert(0, period_end.strftime("%b %Y"))

            # Count deployments in this period
            for deployment in deployments:
                created_at_str = deployment.get("createdAt", "")
                if not created_at_str:
                    continue
                    
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    if period_start <= created_at < period_end:
                        deployment_counts[periods - 1 - i] += 1
                        
                        status = deployment.get("status", "")
                        if "SUCCESSFUL" in status:
                            success_counts[periods - 1 - i] += 1
                        elif "FAILED" in status:
                            failure_counts[periods - 1 - i] += 1
                except:
                    continue

        chart_data = ChartData(
            labels=labels,
            deployments=deployment_counts,
            successes=success_counts,
            failures=failure_counts
        )

        return ChartDataResponse(
            success=True,
            message="Chart data retrieved successfully",
            timestamp=datetime.utcnow(),
            chart_data=chart_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chart data: {str(e)}")


@router.get("/usage", response_model=ResourceUsageResponse)
async def get_resource_usage(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    vra_client: VRAClient = Depends(get_vra_client),
):
    """Get resource usage statistics."""
    try:
        # Get deployments with resources
        deployments_response = await vra_client.list_deployments(
            project_id=project_id,
            verbose=True
        )
        
        if not deployments_response.success:
            raise HTTPException(status_code=500, detail=deployments_response.message)

        deployments = deployments_response.data.get("deployments", [])
        
        # Aggregate resource usage (this is a simplified calculation)
        total_cpu = 0
        total_memory = 0
        total_storage = 0
        vm_count = 0

        for deployment in deployments:
            if deployment.get("status") == "CREATE_SUCCESSFUL":
                # Try to extract resource info from deployment
                # This is simplified - real implementation would query vRA resource details
                vm_count += 1
                total_cpu += 2  # Assume 2 vCPU per VM (would come from actual resource data)
                total_memory += 4096  # Assume 4GB per VM (would come from actual resource data)  
                total_storage += 40  # Assume 40GB per VM (would come from actual resource data)

        usage = ResourceUsage(
            totalCpu=total_cpu,
            totalMemory=total_memory,  # In MB
            totalStorage=total_storage,  # In GB
            vmCount=vm_count,
            cpuUtilization=68.5,  # Would come from monitoring system
            memoryUtilization=73.2,  # Would come from monitoring system
            storageUtilization=82.1   # Would come from monitoring system
        )

        return ResourceUsageResponse(
            success=True,
            message="Resource usage retrieved successfully",
            timestamp=datetime.utcnow(),
            usage=usage
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve resource usage: {str(e)}")


def _format_time_ago(timestamp: datetime) -> str:
    """Format timestamp as 'time ago' string."""
    now = datetime.utcnow().replace(tzinfo=timestamp.tzinfo)
    delta = now - timestamp
    
    if delta.days > 0:
        if delta.days == 1:
            return "1 day ago"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"
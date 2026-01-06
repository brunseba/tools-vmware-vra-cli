"""Pydantic models for MCP server API requests and responses."""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseResponse):
    """Error response model."""
    success: bool = False
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


class AuthRequest(BaseModel):
    """Authentication request model."""
    username: str
    password: str
    url: str
    tenant: Optional[str] = None
    domain: Optional[str] = None


class AuthResponse(BaseResponse):
    """Authentication response model."""
    token_stored: bool = False
    config_saved: bool = False


class ConfigRequest(BaseModel):
    """Configuration update request model."""
    key: str
    value: Union[str, int, bool]


class ConfigResponse(BaseResponse):
    """Configuration response model."""
    config: Dict[str, Any]


class CatalogItemsRequest(BaseModel):
    """Request model for listing catalog items."""
    project_id: Optional[str] = None
    page_size: int = Field(default=100, ge=1, le=2000)
    first_page_only: bool = False


class CatalogItemsResponse(BaseResponse):
    """Response model for catalog items list."""
    items: List[Dict[str, Any]]
    total_count: int
    page_info: Optional[Dict[str, Any]] = None


class CatalogItemRequest(BaseModel):
    """Request model for single catalog item."""
    item_id: str


class CatalogItemResponse(BaseResponse):
    """Response model for single catalog item."""
    item: Dict[str, Any]


class CatalogSchemaRequest(BaseModel):
    """Request model for catalog item schema."""
    item_id: str


class CatalogSchemaResponse(BaseResponse):
    """Response model for catalog item schema."""
    item_schema: Dict[str, Any]


class CatalogRequestRequest(BaseModel):
    """Request model for requesting a catalog item."""
    item_id: str
    project_id: str
    inputs: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    name: Optional[str] = None


class CatalogRequestResponse(BaseResponse):
    """Response model for catalog item request."""
    deployment_id: Optional[str] = None
    request_id: Optional[str] = None


class DeploymentsRequest(BaseModel):
    """Request model for listing deployments."""
    project_id: Optional[str] = None
    status: Optional[str] = None
    page_size: int = Field(default=100, ge=1, le=2000)
    first_page_only: bool = False


class DeploymentsResponse(BaseResponse):
    """Response model for deployments list."""
    deployments: List[Dict[str, Any]]
    total_count: int
    page_info: Optional[Dict[str, Any]] = None


class DeploymentRequest(BaseModel):
    """Request model for single deployment."""
    deployment_id: str


class DeploymentResponse(BaseResponse):
    """Response model for single deployment."""
    deployment: Dict[str, Any]


class DeploymentDeleteRequest(BaseModel):
    """Request model for deleting a deployment."""
    deployment_id: str
    confirm: bool = False


class DeploymentResourcesRequest(BaseModel):
    """Request model for deployment resources."""
    deployment_id: str


class DeploymentResourcesResponse(BaseResponse):
    """Response model for deployment resources."""
    resources: List[Dict[str, Any]]


class TagsRequest(BaseModel):
    """Request model for listing tags."""
    search: Optional[str] = None
    page_size: int = Field(default=100, ge=1, le=2000)
    first_page_only: bool = False


class TagsResponse(BaseResponse):
    """Response model for tags list."""
    tags: List[Dict[str, Any]]
    total_count: int
    page_info: Optional[Dict[str, Any]] = None


class TagRequest(BaseModel):
    """Request model for single tag."""
    tag_id: str


class TagResponse(BaseResponse):
    """Response model for single tag."""
    tag: Dict[str, Any]


class TagCreateRequest(BaseModel):
    """Request model for creating a tag."""
    key: str
    value: Optional[str] = None
    description: Optional[str] = None


class TagCreateResponse(BaseResponse):
    """Response model for tag creation."""
    tag: Dict[str, Any]


class TagUpdateRequest(BaseModel):
    """Request model for updating a tag."""
    tag_id: str
    key: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None


class TagDeleteRequest(BaseModel):
    """Request model for deleting a tag."""
    tag_id: str
    confirm: bool = False


class TagAssignRequest(BaseModel):
    """Request model for assigning a tag to a resource."""
    resource_id: str
    tag_id: str
    resource_type: str = Field(default="deployment", pattern="^(deployment|catalog-item)$")


class TagRemoveRequest(BaseModel):
    """Request model for removing a tag from a resource."""
    resource_id: str
    tag_id: str
    resource_type: str = Field(default="deployment", pattern="^(deployment|catalog-item)$")
    confirm: bool = False


# Analytics Models
class AnalyticsStats(BaseModel):
    """Analytics statistics model."""
    totalDeployments: int
    activeDeployments: int
    failedDeployments: int
    totalUsers: int
    successRate: float = 0.0


class ActivityItem(BaseModel):
    """Activity timeline item model."""
    id: str
    type: str  # deployment, success, failure, deletion
    action: str  # Created, Failed, Deleted, etc.
    resource: str
    user: str
    time: str  # Human readable time ago
    timestamp: Optional[str] = None  # ISO timestamp


class ChartData(BaseModel):
    """Chart data model for trends."""
    labels: List[str]
    deployments: List[int]
    successes: List[int]
    failures: List[int]


class ResourceUsage(BaseModel):
    """Resource usage statistics model."""
    totalCpu: int  # Total vCPUs
    totalMemory: int  # Total memory in MB
    totalStorage: int  # Total storage in GB
    vmCount: int  # Number of VMs
    cpuUtilization: float  # CPU utilization percentage
    memoryUtilization: float  # Memory utilization percentage
    storageUtilization: float  # Storage utilization percentage


class AnalyticsRequest(BaseModel):
    """Request model for analytics data."""
    time_range: str = Field(default="30d", pattern="^(7d|30d|90d|1y)$")
    project_id: Optional[str] = None


class ActivityTimelineRequest(BaseModel):
    """Request model for activity timeline."""
    time_range: str = Field(default="30d", pattern="^(7d|30d|90d|1y)$")
    project_id: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=1000)


class ProjectInfo(BaseModel):
    """Project information model."""
    id: str
    name: str
    description: Optional[str] = None
    organizationId: Optional[str] = None
    

class ProjectsResponse(BaseResponse):
    """Response model for projects list."""
    projects: List[ProjectInfo]
    total_count: int


class ResourceTagsRequest(BaseModel):
    """Request model for getting resource tags."""
    resource_id: str
    resource_type: str = Field(default="deployment", pattern="^(deployment|catalog-item)$")


class WorkflowsRequest(BaseModel):
    """Request model for listing workflows."""
    page_size: int = Field(default=100, ge=1, le=2000)
    first_page_only: bool = False


class WorkflowsResponse(BaseResponse):
    """Response model for workflows list."""
    workflows: List[Dict[str, Any]]
    total_count: int
    page_info: Optional[Dict[str, Any]] = None


class WorkflowRunRequest(BaseModel):
    """Request model for running a workflow."""
    workflow_id: str
    inputs: Optional[Dict[str, Any]] = None


class WorkflowRunResponse(BaseResponse):
    """Response model for workflow execution."""
    execution_id: str
    state: str


class WorkflowSchemaResponse(BaseResponse):
    """Response model for workflow schema."""
    workflow_schema: Dict[str, Any]


class ActivityTimelineRequest(BaseModel):
    """Request model for activity timeline report."""
    project_id: Optional[str] = None
    days_back: int = Field(default=30, ge=1, le=365)
    group_by: str = Field(default="day", pattern="^(day|week|month|year)$")
    statuses: Optional[str] = None


class ActivityTimelineResponse(BaseResponse):
    """Response model for activity timeline report."""
    timeline_data: Dict[str, Any]


class CatalogUsageRequest(BaseModel):
    """Request model for catalog usage report."""
    project_id: Optional[str] = None
    include_zero: bool = False
    sort_by: str = Field(default="deployments", pattern="^(deployments|resources|name)$")
    detailed_resources: bool = False


class CatalogUsageResponse(BaseResponse):
    """Response model for catalog usage report."""
    usage_stats: List[Dict[str, Any]]
    summary: Dict[str, Any]


class UnsyncReportRequest(BaseModel):
    """Request model for unsync report."""
    project_id: Optional[str] = None
    detailed_resources: bool = False
    reason_filter: Optional[str] = None


class UnsyncReportResponse(BaseResponse):
    """Response model for unsync report."""
    unsync_data: Dict[str, Any]


class ResourcesUsageResponse(BaseResponse):
    """Response model for resources usage report."""
    report_data: Dict[str, Any]


class DependenciesReportRequest(BaseModel):
    """Request model for dependencies report."""
    project_id: Optional[str] = None
    deployment_id: Optional[str] = None


class DependenciesReportResponse(BaseResponse):
    """Response model for dependencies report."""
    dependencies_data: Dict[str, Any]


class HealthResponse(BaseResponse):
    """Health check response model."""
    status: str = "healthy"
    version: str
    uptime: str
    vra_connection: Optional[str] = None

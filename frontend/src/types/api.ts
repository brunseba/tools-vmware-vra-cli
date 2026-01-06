export interface BaseResponse {
  success: boolean;
  message?: string;
  timestamp: string;
}

export interface ErrorResponse extends BaseResponse {
  success: false;
  error_code?: string;
  error_details?: Record<string, any>;
}

// Authentication types
export interface AuthRequest {
  username: string;
  password: string;
  url: string;
  tenant?: string;
  domain?: string;
}

export interface AuthResponse extends BaseResponse {
  token_stored: boolean;
  config_saved: boolean;
}

// Catalog types
export interface CatalogItemType {
  name: string;
}

export interface CatalogItem {
  id: string;
  name: string;
  type: CatalogItemType;
  status?: string;
  version?: string;
  description?: string;
}

export interface CatalogItemsResponse extends BaseResponse {
  items: CatalogItem[];
  total_count: number;
  page_info?: {
    page_size: number;
    first_page_only: boolean;
    project_filter?: string;
  };
}

export interface CatalogItemResponse extends BaseResponse {
  item: CatalogItem;
}

export interface CatalogSchema {
  type: string;
  properties: Record<string, any>;
  required?: string[];
}

export interface CatalogSchemaResponse extends BaseResponse {
  item_schema: CatalogSchema;
}

export interface CatalogRequestRequest {
  item_id: string;
  project_id: string;
  inputs?: Record<string, any>;
  reason?: string;
  name?: string;
}

export interface CatalogRequestResponse extends BaseResponse {
  deployment_id?: string;
  request_id?: string;
}

// Deployment types
export interface Deployment {
  id: string;
  name: string;
  status: string;
  projectId: string;
  catalogItemId?: string;
  catalogItemName?: string;
  createdAt: string;
  completedAt?: string;
  inputs?: Record<string, any>;
  resources?: DeploymentResource[];
}

export interface DeploymentsResponse extends BaseResponse {
  deployments: Deployment[];
  total_count: number;
  page_info?: {
    page_size: number;
    first_page_only: boolean;
    project_filter?: string;
    status_filter?: string;
  };
}

export interface DeploymentResponse extends BaseResponse {
  deployment: Deployment;
}

export interface DeploymentResource {
  id: string;
  name: string;
  type: string;
  status: string;
  properties?: Record<string, any>;
}

export interface DeploymentResourcesResponse extends BaseResponse {
  resources: DeploymentResource[];
}

// Report types
export interface ActivityTimelineRequest {
  project_id?: string;
  days_back?: number;
  group_by?: 'day' | 'week' | 'month' | 'year';
  statuses?: string;
}

export interface ActivityTimelineResponse extends BaseResponse {
  timeline_data: {
    summary: Record<string, any>;
    period_activity: Record<string, any>;
  };
}

export interface CatalogUsageRequest {
  project_id?: string;
  include_zero?: boolean;
  sort_by?: 'deployments' | 'resources' | 'name';
  detailed_resources?: boolean;
}

export interface CatalogUsageResponse extends BaseResponse {
  usage_stats: Array<{
    catalog_item: CatalogItem;
    deployment_count: number;
    resource_count: number;
    success_count: number;
    failed_count: number;
    in_progress_count: number;
    success_rate: number;
    status_counts: Record<string, number>;
  }>;
  summary: Record<string, any>;
}

// Health check
export interface HealthResponse extends BaseResponse {
  status: string;
  version: string;
  uptime: string;
  vra_connection?: string;
}
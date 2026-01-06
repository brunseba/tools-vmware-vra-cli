import { apiClient, handleApiResponse, handleApiError } from './api';
import { AxiosError } from 'axios';

// Types for Activity Timeline Report
export interface ActivityTimelineParams {
  projectId?: string;
  daysBack?: number;
  groupBy?: 'day' | 'week' | 'month' | 'year';
  statuses?: string;
}

export interface PeriodActivity {
  total_deployments: number;
  successful_deployments: number;
  failed_deployments: number;
  in_progress_deployments: number;
  unique_catalog_items: number;
  unique_projects: number;
}

export interface ActivityTimelineData {
  summary: {
    total_deployments: number;
    successful_deployments: number;
    failed_deployments: number;
    in_progress_deployments: number;
    date_range_start: string;
    date_range_end: string;
    unique_catalog_items: number;
    unique_projects: number;
  };
  period_activity: Record<string, PeriodActivity>;
}

export interface ActivityTimelineResponse {
  success: boolean;
  message: string;
  timeline_data: ActivityTimelineData;
}

// Types for Catalog Usage Report
export interface CatalogUsageParams {
  projectId?: string;
  includeZero?: boolean;
  sortBy?: 'deployments' | 'resources' | 'name';
  detailedResources?: boolean;
}

export interface CatalogUsageItem {
  id: string;
  name: string;
  type: string;
  deployment_count: number;
  resource_count: number;
  success_count: number;
  failed_count: number;
  in_progress_count: number;
  success_rate: number;
  status_breakdown: Record<string, number>;
}

export interface CatalogUsageData {
  usage_stats: CatalogUsageItem[];
  summary: {
    total_catalog_items: number;
    active_items: number;
    total_deployments_system_wide: number;
    catalog_linked_deployments: number;
    unlinked_deployments: number;
    total_resources: number;
    average_deployments_per_active_item: number;
  };
}

export interface CatalogUsageResponse {
  success: boolean;
  message: string;
  usage_stats: CatalogUsageItem[];
  summary: CatalogUsageData['summary'];
}

// Types for Resources Usage Report
export interface ResourcesUsageParams {
  projectId?: string;
  detailedResources?: boolean;
  sortBy?: 'deployment-name' | 'catalog-item' | 'resource-count' | 'status';
  groupBy?: 'catalog-item' | 'resource-type' | 'deployment-status';
}

export interface DeploymentResourceInfo {
  id: string;
  name: string;
  status: string;
  resource_count: number;
  catalog_item_id?: string;
  catalog_item_info?: {
    id: string;
    name: string;
    type: string;
  };
  resource_breakdown?: Record<string, number>;
  created_at?: string;
}

export interface CatalogItemSummary {
  catalog_item_info?: {
    id: string;
    name: string;
    type: string;
  };
  deployment_count: number;
  total_resources: number;
  resource_types: Record<string, number>;
}

export interface ResourcesUsageData {
  summary: {
    total_deployments: number;
    linked_deployments: number;
    unlinked_deployments: number;
    total_resources: number;
    unique_resource_types: number;
    unique_catalog_items: number;
    resource_types: Record<string, number>;
    resource_states: Record<string, number>;
  };
  deployments: DeploymentResourceInfo[];
  catalog_item_summary: Record<string, CatalogItemSummary>;
  unlinked_deployments: DeploymentResourceInfo[];
}

export interface ResourcesUsageResponse {
  success: boolean;
  message: string;
  report_data: ResourcesUsageData;
}

// Types for Unsync Report
export interface UnsyncReportParams {
  projectId?: string;
  detailedResources?: boolean;
  reasonFilter?: string;
}

export interface UnsyncAnalysis {
  primary_reason: string;
  details: string[];
  suggestions: string[];
  potential_matches?: Array<{
    id: string;
    name: string;
    similarity_reason: string;
  }>;
}

export interface UnsyncedDeployment {
  deployment: {
    id?: string;
    name?: string;
    status?: string;
    createdAt?: string;
    projectId?: string;
    catalogItemId?: string;
    catalogItemName?: string;
    blueprintId?: string;
  };
  resource_count: number;
  analysis: UnsyncAnalysis;
}

export interface UnsyncReportData {
  summary: {
    total_deployments: number;
    linked_deployments: number;
    unsynced_deployments: number;
    unsynced_percentage: number;
    total_unsynced_resources: number;
    catalog_items_count: number;
  };
  reason_groups: Record<string, number>;
  status_breakdown: Record<string, number>;
  age_breakdown: Record<string, number>;
  unsynced_deployments: UnsyncedDeployment[];
}

export interface UnsyncReportResponse {
  success: boolean;
  message: string;
  unsync_data: UnsyncReportData;
}

// Types for Dependencies Report
export interface DependenciesReportParams {
  projectId?: string;
  deploymentId?: string;
}

export interface ResourceDependency {
  type: string;
  description: string;
  target_id?: string;
  target_name?: string;
  target_type?: string;
  details?: Record<string, any>;
}

export interface InputDependency {
  source_type: string;
  source_name: string;
  input_name: string;
  depends_on: ResourceDependency[];
}

export interface ResourceWithDependencies {
  id: string;
  name: string;
  type: string;
  deployment_id: string;
  deployment_name: string;
  dependencies?: ResourceDependency[];
}

export interface DeploymentDependencyInfo {
  deployment_id: string;
  deployment_name: string;
  resource_count: number;
  resources: ResourceWithDependencies[];
  dependency_count: number;
  dependencies: Array<{
    resource_id: string;
    resource_name: string;
    resource_type: string;
    depends_on: ResourceDependency[];
  }>;
  input_dependencies: InputDependency[];
}

export interface CrossResourceLink {
  source_id: string;
  source_name: string;
  source_type: string;
  source_deployment_id: string;
  source_deployment_name: string;
  target_id: string;
  target_name: string;
  target_type: string;
  target_deployment_id: string;
  target_deployment_name: string;
  is_cross_deployment: boolean;
}

export interface DependenciesReportData {
  summary: {
    total_deployments: number;
    total_resources: number;
    resources_with_dependencies: number;
    standalone_resources: number;
    unique_resource_types: number;
    dependency_types: Record<string, number>;
    resource_types: Record<string, number>;
    cross_resource_links_count: number;
    cross_deployment_links_count: number;
    same_deployment_links_count: number;
    deployments_with_input_dependencies: number;
    total_input_dependencies: number;
  };
  deployments: DeploymentDependencyInfo[];
  all_resources: ResourceWithDependencies[];
  cross_resource_links: CrossResourceLink[];
  cross_deployment_links: CrossResourceLink[];
  same_deployment_links: CrossResourceLink[];
}

export interface DependenciesReportResponse {
  success: boolean;
  message: string;
  dependencies_data: DependenciesReportData;
}

class ReportService {
  /**
   * Get activity timeline report
   */
  async getActivityTimeline(params: ActivityTimelineParams = {}): Promise<ActivityTimelineData> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params.projectId) queryParams.append('project_id', params.projectId);
      if (params.daysBack) queryParams.append('days_back', params.daysBack.toString());
      if (params.groupBy) queryParams.append('group_by', params.groupBy);
      if (params.statuses) queryParams.append('statuses', params.statuses);
      
      const response = await apiClient.get<ActivityTimelineResponse>(
        `/reports/activity-timeline?${queryParams.toString()}`
      );
      
      return handleApiResponse(response).timeline_data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }

  /**
   * Get catalog usage report
   */
  async getCatalogUsage(params: CatalogUsageParams = {}): Promise<CatalogUsageData> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params.projectId) queryParams.append('project_id', params.projectId);
      if (params.includeZero !== undefined) queryParams.append('include_zero', params.includeZero.toString());
      if (params.sortBy) queryParams.append('sort_by', params.sortBy);
      if (params.detailedResources !== undefined) queryParams.append('detailed_resources', params.detailedResources.toString());
      
      const response = await apiClient.get<CatalogUsageResponse>(
        `/reports/catalog-usage?${queryParams.toString()}`
      );
      
      const result = handleApiResponse(response);
      return {
        usage_stats: result.usage_stats,
        summary: result.summary
      };
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }

  /**
   * Get resources usage report
   */
  async getResourcesUsage(params: ResourcesUsageParams = {}): Promise<ResourcesUsageData> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params.projectId) queryParams.append('project_id', params.projectId);
      if (params.detailedResources !== undefined) queryParams.append('detailed_resources', params.detailedResources.toString());
      if (params.sortBy) queryParams.append('sort_by', params.sortBy);
      if (params.groupBy) queryParams.append('group_by', params.groupBy);
      
      const response = await apiClient.get<ResourcesUsageResponse>(
        `/reports/resources-usage?${queryParams.toString()}`
      );
      
      return handleApiResponse(response).report_data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }

  /**
   * Get unsync report
   */
  async getUnsyncReport(params: UnsyncReportParams = {}): Promise<UnsyncReportData> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params.projectId) queryParams.append('project_id', params.projectId);
      if (params.detailedResources !== undefined) queryParams.append('detailed_resources', params.detailedResources.toString());
      if (params.reasonFilter) queryParams.append('reason_filter', params.reasonFilter);
      
      const response = await apiClient.get<UnsyncReportResponse>(
        `/reports/unsync?${queryParams.toString()}`
      );
      
      return handleApiResponse(response).unsync_data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }

  /**
   * Get dependencies report
   */
  async getDependencies(params: DependenciesReportParams = {}): Promise<DependenciesReportData> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params.projectId) queryParams.append('project_id', params.projectId);
      if (params.deploymentId) queryParams.append('deployment_id', params.deploymentId);
      
      const response = await apiClient.get<DependenciesReportResponse>(
        `/reports/dependencies?${queryParams.toString()}`
      );
      
      return handleApiResponse(response).dependencies_data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }
}

export const reportService = new ReportService();

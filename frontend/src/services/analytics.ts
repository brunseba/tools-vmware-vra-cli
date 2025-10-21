import { apiClient, handleApiResponse, handleApiError } from './api';

export interface AnalyticsStats {
  totalDeployments: number;
  activeDeployments: number;
  failedDeployments: number;
  totalUsers: number;
  successRate: number;
}

export interface ActivityItem {
  id: string;
  type: string;
  action: string;
  resource: string;
  user: string;
  time: string;
  timestamp?: string;
}

export interface ChartData {
  labels: string[];
  deployments: number[];
  successes: number[];
  failures: number[];
}

export interface ResourceUsage {
  totalCpu: number;
  totalMemory: number;
  totalStorage: number;
  vmCount: number;
  cpuUtilization: number;
  memoryUtilization: number;
  storageUtilization: number;
}

export interface AnalyticsParams {
  timeRange?: string;
  projectId?: string;
}

export interface ActivityTimelineParams extends AnalyticsParams {
  limit?: number;
}

interface AnalyticsStatsResponse {
  success: boolean;
  message?: string;
  timestamp: string;
  stats: AnalyticsStats;
}

interface ActivityTimelineResponse {
  success: boolean;
  message?: string;
  timestamp: string;
  activities: ActivityItem[];
  total_count: number;
}

interface ChartDataResponse {
  success: boolean;
  message?: string;
  timestamp: string;
  chart_data: ChartData;
}

interface ResourceUsageResponse {
  success: boolean;
  message?: string;
  timestamp: string;
  usage: ResourceUsage;
}

export const analyticsService = {
  /**
   * Get analytics statistics
   */
  async getStats(params: AnalyticsParams = {}): Promise<AnalyticsStats> {
    try {
      const response = await apiClient.get<AnalyticsStatsResponse>('/analytics/stats', {
        params: {
          time_range: params.timeRange || '30d',
          project_id: params.projectId,
        }
      });
      
      const data = handleApiResponse(response);
      return data.stats;
    } catch (error: any) {
      return handleApiError(error);
    }
  },

  /**
   * Get activity timeline
   */
  async getTimeline(params: ActivityTimelineParams = {}): Promise<ActivityItem[]> {
    try {
      const response = await apiClient.get<ActivityTimelineResponse>('/analytics/timeline', {
        params: {
          time_range: params.timeRange || '30d',
          project_id: params.projectId,
          limit: params.limit || 50,
        }
      });
      
      const data = handleApiResponse(response);
      return data.activities;
    } catch (error: any) {
      return handleApiError(error);
    }
  },

  /**
   * Get chart data for trends
   */
  async getChartData(params: AnalyticsParams = {}): Promise<ChartData> {
    try {
      const response = await apiClient.get<ChartDataResponse>('/analytics/charts', {
        params: {
          time_range: params.timeRange || '30d',
          project_id: params.projectId,
        }
      });
      
      const data = handleApiResponse(response);
      return data.chart_data;
    } catch (error: any) {
      return handleApiError(error);
    }
  },

  /**
   * Get resource usage statistics
   */
  async getResourceUsage(params: Pick<AnalyticsParams, 'projectId'> = {}): Promise<ResourceUsage> {
    try {
      const response = await apiClient.get<ResourceUsageResponse>('/analytics/usage', {
        params: {
          project_id: params.projectId,
        }
      });
      
      const data = handleApiResponse(response);
      return data.usage;
    } catch (error: any) {
      return handleApiError(error);
    }
  },
};
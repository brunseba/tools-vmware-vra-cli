import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { 
  analyticsService, 
  AnalyticsStats, 
  ActivityItem, 
  ChartData, 
  ResourceUsage,
  AnalyticsParams,
  ActivityTimelineParams 
} from '../services/analytics';

/**
 * Hook to fetch analytics statistics
 */
export const useAnalyticsStats = (
  params: AnalyticsParams = {},
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
): UseQueryResult<AnalyticsStats, Error> => {
  return useQuery({
    queryKey: ['analytics', 'stats', params.timeRange, params.projectId],
    queryFn: () => analyticsService.getStats(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: options?.enabled ?? true,
    refetchInterval: options?.refetchInterval ?? 30000, // 30 seconds
  });
};

/**
 * Hook to fetch activity timeline
 */
export const useActivityTimeline = (
  params: ActivityTimelineParams = {},
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
): UseQueryResult<ActivityItem[], Error> => {
  return useQuery({
    queryKey: ['analytics', 'timeline', params.timeRange, params.projectId, params.limit],
    queryFn: () => analyticsService.getTimeline(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
    enabled: options?.enabled ?? true,
    refetchInterval: options?.refetchInterval ?? 30000, // 30 seconds
  });
};

/**
 * Hook to fetch chart data
 */
export const useChartData = (
  params: AnalyticsParams = {},
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
): UseQueryResult<ChartData, Error> => {
  return useQuery({
    queryKey: ['analytics', 'charts', params.timeRange, params.projectId],
    queryFn: () => analyticsService.getChartData(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: options?.enabled ?? true,
    refetchInterval: options?.refetchInterval ?? 60000, // 1 minute
  });
};

/**
 * Hook to fetch resource usage
 */
export const useResourceUsage = (
  params: Pick<AnalyticsParams, 'projectId'> = {},
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
): UseQueryResult<ResourceUsage, Error> => {
  return useQuery({
    queryKey: ['analytics', 'usage', params.projectId],
    queryFn: () => analyticsService.getResourceUsage(params),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: options?.enabled ?? true,
    refetchInterval: options?.refetchInterval ?? 60000, // 1 minute
  });
};
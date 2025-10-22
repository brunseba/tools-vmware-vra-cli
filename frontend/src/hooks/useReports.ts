import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { reportService } from '../services/reports';
import type {
  ActivityTimelineData,
  CatalogUsageData,
  ResourcesUsageData,
  UnsyncReportData,
  ActivityTimelineParams,
  CatalogUsageParams,
  ResourcesUsageParams,
  UnsyncReportParams,
} from '../services/reports';

/**
 * Hook to fetch activity timeline report
 */
export const useActivityTimelineReport = (
  params: ActivityTimelineParams = {},
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
): UseQueryResult<ActivityTimelineData, Error> => {
  return useQuery({
    queryKey: ['reports', 'activity-timeline', params.projectId, params.daysBack, params.groupBy, params.statuses],
    queryFn: () => reportService.getActivityTimeline(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: options?.enabled ?? true,
    refetchInterval: options?.refetchInterval,
  });
};

/**
 * Hook to fetch catalog usage report
 */
export const useCatalogUsageReport = (
  params: CatalogUsageParams = {},
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
): UseQueryResult<CatalogUsageData, Error> => {
  return useQuery({
    queryKey: ['reports', 'catalog-usage', params.projectId, params.includeZero, params.sortBy, params.detailedResources],
    queryFn: () => reportService.getCatalogUsage(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: options?.enabled ?? true,
    refetchInterval: options?.refetchInterval,
  });
};

/**
 * Hook to fetch resources usage report
 */
export const useResourcesUsageReport = (
  params: ResourcesUsageParams = {},
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
): UseQueryResult<ResourcesUsageData, Error> => {
  return useQuery({
    queryKey: ['reports', 'resources-usage', params.projectId, params.detailedResources, params.sortBy, params.groupBy],
    queryFn: () => reportService.getResourcesUsage(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: options?.enabled ?? true,
    refetchInterval: options?.refetchInterval,
  });
};

/**
 * Hook to fetch unsync report
 */
export const useUnsyncReport = (
  params: UnsyncReportParams = {},
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
): UseQueryResult<UnsyncReportData, Error> => {
  return useQuery({
    queryKey: ['reports', 'unsync', params.projectId, params.detailedResources, params.reasonFilter],
    queryFn: () => reportService.getUnsyncReport(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: options?.enabled ?? true,
    refetchInterval: options?.refetchInterval,
  });
};

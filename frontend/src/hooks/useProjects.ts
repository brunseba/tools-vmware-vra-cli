import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { projectsService, Project } from '../services/projects';

/**
 * Hook to fetch all projects
 */
export const useProjects = (
  verbose: boolean = false,
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
): UseQueryResult<Project[], Error> => {
  return useQuery({
    queryKey: ['projects', verbose],
    queryFn: () => projectsService.listProjects(verbose),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: options?.enabled ?? true,
    refetchInterval: options?.refetchInterval,
  });
};

/**
 * Hook to fetch a specific project
 */
export const useProject = (
  projectId: string,
  verbose: boolean = false,
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
): UseQueryResult<Project, Error> => {
  return useQuery({
    queryKey: ['projects', projectId, verbose],
    queryFn: () => projectsService.getProject(projectId, verbose),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: (options?.enabled ?? true) && !!projectId,
    refetchInterval: options?.refetchInterval,
  });
};
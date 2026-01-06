import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { deploymentsService, DeploymentListParams } from '@/services/deployments'
import { useSettingsStore } from '@/store/settingsStore'

export const useDeployments = (params: DeploymentListParams = {}) => {
  return useQuery({
    queryKey: ['deployments', params],
    queryFn: () => deploymentsService.listDeployments(params),
    staleTime: 1 * 60 * 1000, // 1 minute (deployments change frequently)
    retry: 2,
  })
}

export const useDeployment = (deploymentId: string, verbose = false) => {
  return useQuery({
    queryKey: ['deployment', deploymentId, verbose],
    queryFn: () => deploymentsService.getDeployment(deploymentId, verbose),
    enabled: !!deploymentId,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1,
  })
}

export const useDeploymentResources = (deploymentId: string, verbose = false) => {
  return useQuery({
    queryKey: ['deployment', 'resources', deploymentId, verbose],
    queryFn: () => deploymentsService.getDeploymentResources(deploymentId, verbose),
    enabled: !!deploymentId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  })
}

export const useDeleteDeployment = () => {
  const queryClient = useQueryClient()
  const { addNotification } = useSettingsStore()
  
  return useMutation({
    mutationFn: ({ deploymentId, confirm = true, verbose = false }: {
      deploymentId: string
      confirm?: boolean
      verbose?: boolean
    }) => deploymentsService.deleteDeployment(deploymentId, confirm, verbose),
    
    onSuccess: (_, { deploymentId }) => {
      // Invalidate deployment queries to refresh the list
      queryClient.invalidateQueries({ queryKey: ['deployments'] })
      queryClient.removeQueries({ queryKey: ['deployment', deploymentId] })
      queryClient.removeQueries({ queryKey: ['deployment', 'resources', deploymentId] })
      
      addNotification({
        type: 'success',
        title: 'Deployment Deleted',
        message: `Deployment ${deploymentId} has been successfully deleted`,
      })
    },
    
    onError: (error: Error, { deploymentId }) => {
      addNotification({
        type: 'error',
        title: 'Delete Failed',
        message: `Failed to delete deployment ${deploymentId}: ${error.message}`,
      })
    },
  })
}

// Hook to get deployment statistics
export const useDeploymentStats = (projectId?: string) => {
  return useQuery({
    queryKey: ['deployments', 'stats', projectId],
    queryFn: async () => {
      const response = await deploymentsService.listDeployments({
        project_id: projectId,
        page_size: 1000, // Get a reasonable sample for stats
      })
      
      const deployments = response.deployments
      
      // Calculate statistics
      const totalDeployments = response.total_count
      const activeDeployments = deployments.filter(d => 
        d.status.includes('INPROGRESS') || d.status.includes('RUNNING')
      ).length
      
      const successfulDeployments = deployments.filter(d => 
        d.status.includes('SUCCESSFUL') || d.status === 'SUCCESS'
      ).length
      
      const failedDeployments = deployments.filter(d => 
        d.status.includes('FAILED') || d.status === 'FAILED'
      ).length
      
      const successRate = totalDeployments > 0 
        ? (successfulDeployments / totalDeployments) * 100 
        : 0
      
      return {
        totalDeployments,
        activeDeployments,
        successfulDeployments,
        failedDeployments,
        successRate,
      }
    },
    staleTime: 2 * 60 * 1000,
    retry: 1,
  })
}

// Hook for auto-refreshing deployments
export const useDeploymentsAutoRefresh = (params: DeploymentListParams = {}, enabled = true) => {
  const { settings } = useSettingsStore()
  
  return useQuery({
    queryKey: ['deployments', 'auto-refresh', params],
    queryFn: () => deploymentsService.listDeployments(params),
    enabled: enabled && settings.autoRefresh,
    refetchInterval: settings.refreshInterval,
    staleTime: 30 * 1000, // 30 seconds for auto-refresh
    retry: 1,
  })
}
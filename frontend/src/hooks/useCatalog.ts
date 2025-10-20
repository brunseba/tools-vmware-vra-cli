import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { catalogService, CatalogListParams } from '@/services/catalog'
import { useSettingsStore } from '@/store/settingsStore'
import { CatalogRequestRequest } from '@/types/api'

export const useCatalogItems = (params: CatalogListParams = {}) => {
  return useQuery({
    queryKey: ['catalog', 'items', params],
    queryFn: () => catalogService.listItems(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  })
}

export const useCatalogItem = (itemId: string, verbose = false) => {
  return useQuery({
    queryKey: ['catalog', 'item', itemId, verbose],
    queryFn: () => catalogService.getItem(itemId, verbose),
    enabled: !!itemId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  })
}

export const useCatalogItemSchema = (itemId: string, verbose = false) => {
  return useQuery({
    queryKey: ['catalog', 'schema', itemId, verbose],
    queryFn: () => catalogService.getItemSchema(itemId, verbose),
    enabled: !!itemId,
    staleTime: 10 * 60 * 1000, // 10 minutes (schemas change rarely)
    retry: 1,
  })
}

export const useRequestCatalogItem = () => {
  const queryClient = useQueryClient()
  const { addNotification } = useSettingsStore()
  
  return useMutation({
    mutationFn: ({ itemId, requestData, verbose = false }: {
      itemId: string
      requestData: CatalogRequestRequest
      verbose?: boolean
    }) => catalogService.requestItem(itemId, requestData, verbose),
    
    onSuccess: (response, { requestData }) => {
      // Invalidate deployments to refresh the list
      queryClient.invalidateQueries({ queryKey: ['deployments'] })
      
      addNotification({
        type: 'success',
        title: 'Deployment Started',
        message: `Successfully requested "${requestData.name || 'catalog item'}" - Deployment ID: ${response.deployment_id}`,
        autoHide: false, // Keep visible for important success messages
      })
    },
    
    onError: (error: Error, { requestData }) => {
      addNotification({
        type: 'error',
        title: 'Deployment Failed',
        message: `Failed to deploy "${requestData.name || 'catalog item'}": ${error.message}`,
        autoHide: false,
      })
    },
  })
}

// Hook for prefetching catalog items in the background
export const usePrefetchCatalogItems = () => {
  const queryClient = useQueryClient()
  
  return (params: CatalogListParams = {}) => {
    queryClient.prefetchQuery({
      queryKey: ['catalog', 'items', params],
      queryFn: () => catalogService.listItems(params),
      staleTime: 2 * 60 * 1000,
    })
  }
}

// Hook for infinite scrolling of catalog items
export const useCatalogItemsInfinite = (baseParams: CatalogListParams = {}) => {
  const { settings } = useSettingsStore()
  
  return useQuery({
    queryKey: ['catalog', 'items', 'infinite', baseParams],
    queryFn: async () => {
      const params = {
        ...baseParams,
        page_size: settings.pageSize,
        first_page_only: false,
      }
      return catalogService.listItems(params)
    },
    staleTime: 2 * 60 * 1000,
    retry: 2,
  })
}

// Hook to get catalog item counts and statistics
export const useCatalogStats = (projectId?: string) => {
  return useQuery({
    queryKey: ['catalog', 'stats', projectId],
    queryFn: async () => {
      const response = await catalogService.listItems({
        project_id: projectId,
        page_size: 1, // We only need the count
      })
      
      return {
        totalItems: response.total_count,
        hasItems: response.total_count > 0,
      }
    },
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })
}
import { useQuery, useMutation, useQueryClient, UseQueryResult } from '@tanstack/react-query'
import { vmTemplateService, VMTemplate, VMTemplateCreate, VMTemplateUpdate } from '@/services/vmTemplates'
import { useSettingsStore } from '@/store/settingsStore'

/**
 * Hook to fetch all VM templates
 */
export const useVMTemplates = (search?: string): UseQueryResult<VMTemplate[], Error> => {
  return useQuery({
    queryKey: ['vm-templates', search],
    queryFn: () => vmTemplateService.listTemplates(search),
    staleTime: 1 * 60 * 1000, // 1 minute
    retry: 2,
  })
}

/**
 * Hook to fetch a single VM template
 */
export const useVMTemplate = (templateId: string): UseQueryResult<VMTemplate, Error> => {
  return useQuery({
    queryKey: ['vm-templates', templateId],
    queryFn: () => vmTemplateService.getTemplate(templateId),
    enabled: !!templateId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  })
}

/**
 * Hook to create a VM template
 */
export const useCreateVMTemplate = () => {
  const queryClient = useQueryClient()
  const { addNotification } = useSettingsStore()

  return useMutation({
    mutationFn: (template: VMTemplateCreate) => vmTemplateService.createTemplate(template),
    onSuccess: (data) => {
      // Invalidate templates list to refresh
      queryClient.invalidateQueries({ queryKey: ['vm-templates'] })
      
      addNotification({
        type: 'success',
        title: 'Template Created',
        message: `Successfully created template "${data.name}"`,
      })
    },
    onError: (error: Error) => {
      addNotification({
        type: 'error',
        title: 'Creation Failed',
        message: `Failed to create template: ${error.message}`,
      })
    },
  })
}

/**
 * Hook to update a VM template
 */
export const useUpdateVMTemplate = () => {
  const queryClient = useQueryClient()
  const { addNotification } = useSettingsStore()

  return useMutation({
    mutationFn: ({ id, template }: { id: string; template: VMTemplateUpdate }) =>
      vmTemplateService.updateTemplate(id, template),
    onSuccess: (data) => {
      // Invalidate templates list and specific template
      queryClient.invalidateQueries({ queryKey: ['vm-templates'] })
      queryClient.invalidateQueries({ queryKey: ['vm-templates', data.id] })
      
      addNotification({
        type: 'success',
        title: 'Template Updated',
        message: `Successfully updated template "${data.name}"`,
      })
    },
    onError: (error: Error) => {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: `Failed to update template: ${error.message}`,
      })
    },
  })
}

/**
 * Hook to delete a VM template
 */
export const useDeleteVMTemplate = () => {
  const queryClient = useQueryClient()
  const { addNotification } = useSettingsStore()

  return useMutation({
    mutationFn: (templateId: string) => vmTemplateService.deleteTemplate(templateId),
    onSuccess: (data) => {
      // Invalidate templates list
      queryClient.invalidateQueries({ queryKey: ['vm-templates'] })
      
      addNotification({
        type: 'success',
        title: 'Template Deleted',
        message: data.message,
      })
    },
    onError: (error: Error) => {
      addNotification({
        type: 'error',
        title: 'Deletion Failed',
        message: `Failed to delete template: ${error.message}`,
      })
    },
  })
}

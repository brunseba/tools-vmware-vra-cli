import { apiClient, handleApiResponse, handleApiError } from './api'
import { AxiosError } from 'axios'

export interface VMTemplate {
  id: string
  name: string
  description: string
  catalogItemId: string
  catalogItemName: string
  inputs: Record<string, any>
  createdAt: string
  updatedAt: string
}

export interface VMTemplateCreate {
  name: string
  description?: string
  catalogItemId?: string
  catalogItemName?: string
  inputs: Record<string, any>
}

export interface VMTemplateUpdate {
  name?: string
  description?: string
  catalogItemId?: string
  catalogItemName?: string
  inputs?: Record<string, any>
}

export interface VMTemplateListResponse {
  success: boolean
  message: string
  templates: VMTemplate[]
  total_count: number
}

class VMTemplateService {
  /**
   * List all VM templates
   */
  async listTemplates(search?: string): Promise<VMTemplate[]> {
    try {
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      
      const response = await apiClient.get<VMTemplateListResponse>(
        `/vm-templates${params.toString() ? `?${params.toString()}` : ''}`
      )
      
      return handleApiResponse(response).templates
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }

  /**
   * Get a specific template by ID
   */
  async getTemplate(templateId: string): Promise<VMTemplate> {
    try {
      const response = await apiClient.get<VMTemplate>(`/vm-templates/${templateId}`)
      return response.data
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }

  /**
   * Create a new template
   */
  async createTemplate(template: VMTemplateCreate): Promise<VMTemplate> {
    try {
      const response = await apiClient.post<VMTemplate>('/vm-templates', template)
      return response.data
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }

  /**
   * Update an existing template
   */
  async updateTemplate(templateId: string, template: VMTemplateUpdate): Promise<VMTemplate> {
    try {
      const response = await apiClient.put<VMTemplate>(`/vm-templates/${templateId}`, template)
      return response.data
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }

  /**
   * Delete a template
   */
  async deleteTemplate(templateId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.delete<{ success: boolean; message: string }>(
        `/vm-templates/${templateId}`
      )
      return handleApiResponse(response)
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }
}

export const vmTemplateService = new VMTemplateService()

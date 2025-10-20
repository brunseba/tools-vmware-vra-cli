import { apiClient, handleApiResponse, handleApiError } from './api'
import {
  DeploymentsResponse,
  DeploymentResponse,
  DeploymentResourcesResponse,
  BaseResponse,
} from '@/types/api'

export interface DeploymentListParams {
  project_id?: string
  status?: string
  page_size?: number
  first_page_only?: boolean
  verbose?: boolean
}

export const deploymentsService = {
  /**
   * List deployments with optional filtering
   */
  async listDeployments(params: DeploymentListParams = {}): Promise<DeploymentsResponse> {
    try {
      const response = await apiClient.get<DeploymentsResponse>('/deployments', {
        params
      })
      return handleApiResponse(response)
    } catch (error: any) {
      return handleApiError(error)
    }
  },

  /**
   * Get details of a specific deployment
   */
  async getDeployment(deploymentId: string, verbose = false): Promise<DeploymentResponse> {
    try {
      const response = await apiClient.get<DeploymentResponse>(`/deployments/${deploymentId}`, {
        params: { verbose }
      })
      return handleApiResponse(response)
    } catch (error: any) {
      return handleApiError(error)
    }
  },

  /**
   * Delete a deployment
   */
  async deleteDeployment(deploymentId: string, confirm = true, verbose = false): Promise<BaseResponse> {
    try {
      const response = await apiClient.delete<BaseResponse>(`/deployments/${deploymentId}`, {
        params: { confirm, verbose }
      })
      return handleApiResponse(response)
    } catch (error: any) {
      return handleApiError(error)
    }
  },

  /**
   * Get deployment resources
   */
  async getDeploymentResources(deploymentId: string, verbose = false): Promise<DeploymentResourcesResponse> {
    try {
      const response = await apiClient.get<DeploymentResourcesResponse>(`/deployments/${deploymentId}/resources`, {
        params: { verbose }
      })
      return handleApiResponse(response)
    } catch (error: any) {
      return handleApiError(error)
    }
  },
}
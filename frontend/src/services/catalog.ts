import { apiClient, handleApiResponse, handleApiError } from './api';
import {
  CatalogItemsResponse,
  CatalogItemResponse,
  CatalogSchemaResponse,
  CatalogRequestRequest,
  CatalogRequestResponse,
} from '@/types/api';

export interface CatalogListParams {
  project_id?: string;
  page_size?: number;
  first_page_only?: boolean;
  verbose?: boolean;
}

export const catalogService = {
  /**
   * List available catalog items
   */
  async listItems(params: CatalogListParams = {}): Promise<CatalogItemsResponse> {
    try {
      const response = await apiClient.get<CatalogItemsResponse>('/catalog/items', {
        params
      });
      return handleApiResponse(response);
    } catch (error: any) {
      return handleApiError(error);
    }
  },

  /**
   * Get details of a specific catalog item
   */
  async getItem(itemId: string, verbose = false): Promise<CatalogItemResponse> {
    try {
      const response = await apiClient.get<CatalogItemResponse>(`/catalog/items/${itemId}`, {
        params: { verbose }
      });
      return handleApiResponse(response);
    } catch (error: any) {
      return handleApiError(error);
    }
  },

  /**
   * Get schema for a catalog item
   */
  async getItemSchema(itemId: string, verbose = false): Promise<CatalogSchemaResponse> {
    try {
      const response = await apiClient.get<CatalogSchemaResponse>(`/catalog/items/${itemId}/schema`, {
        params: { verbose }
      });
      return handleApiResponse(response);
    } catch (error: any) {
      return handleApiError(error);
    }
  },

  /**
   * Request a catalog item deployment
   */
  async requestItem(itemId: string, requestData: CatalogRequestRequest, verbose = false): Promise<CatalogRequestResponse> {
    try {
      const response = await apiClient.post<CatalogRequestResponse>(
        `/catalog/items/${itemId}/request`,
        requestData,
        { params: { verbose } }
      );
      return handleApiResponse(response);
    } catch (error: any) {
      return handleApiError(error);
    }
  },
};
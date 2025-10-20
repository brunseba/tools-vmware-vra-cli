import { apiClient, handleApiResponse, handleApiError } from './api';
import {
  AuthRequest,
  AuthResponse,
  BaseResponse,
} from '@/types/api';

export const authService = {
  /**
   * Authenticate user with vRA credentials
   */
  async login(credentials: AuthRequest): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
      return handleApiResponse(response);
    } catch (error: any) {
      return handleApiError(error);
    }
  },

  /**
   * Logout and clear stored tokens
   */
  async logout(): Promise<BaseResponse> {
    try {
      const response = await apiClient.post<BaseResponse>('/auth/logout');
      return handleApiResponse(response);
    } catch (error: any) {
      return handleApiError(error);
    }
  },

  /**
   * Check current authentication status
   */
  async getStatus(): Promise<BaseResponse> {
    try {
      const response = await apiClient.get<BaseResponse>('/auth/status');
      return handleApiResponse(response);
    } catch (error: any) {
      return handleApiError(error);
    }
  },

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<BaseResponse> {
    try {
      const response = await apiClient.post<BaseResponse>('/auth/refresh');
      return handleApiResponse(response);
    } catch (error: any) {
      return handleApiError(error);
    }
  },
};
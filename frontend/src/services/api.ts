import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';
import { BaseResponse, ErrorResponse } from '@/types/api';

// Create base axios instance
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: '/api', // Proxy configured in vite.config.ts
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor
  client.interceptors.request.use(
    (config) => {
      // Add any common headers or auth tokens here if needed
      console.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error('API Request Error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      console.debug(`API Response: ${response.status} ${response.config.url}`);
      return response;
    },
    (error: AxiosError) => {
      console.error('API Response Error:', error);
      
      // Handle different error types
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const data = error.response.data as ErrorResponse;
        
        switch (status) {
          case 401:
            // Handle unauthorized - could trigger logout
            console.error('Unauthorized access');
            break;
          case 403:
            console.error('Forbidden access');
            break;
          case 404:
            console.error('Resource not found');
            break;
          case 500:
            console.error('Internal server error');
            break;
          default:
            console.error(`API Error ${status}:`, data.message || error.message);
        }
      } else if (error.request) {
        // Network error
        console.error('Network error:', error.message);
      } else {
        // Other error
        console.error('Error:', error.message);
      }
      
      return Promise.reject(error);
    }
  );

  return client;
};

// Create the API client instance
export const apiClient = createApiClient();

// Helper function to handle API responses
export const handleApiResponse = <T extends BaseResponse>(
  response: AxiosResponse<T>
): T => {
  const data = response.data;
  
  if (!data.success) {
    throw new Error((data as ErrorResponse).message || 'API request failed');
  }
  
  return data;
};

// Helper function to handle API errors
export const handleApiError = (error: AxiosError): never => {
  if (error.response?.data) {
    const errorData = error.response.data as ErrorResponse;
    throw new Error(errorData.message || 'API request failed');
  }
  
  throw new Error(error.message || 'Network error occurred');
};
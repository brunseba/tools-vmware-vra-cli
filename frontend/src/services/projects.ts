import { apiClient, handleApiResponse, handleApiError } from './api';

export interface Project {
  id: string;
  name: string;
  description?: string;
  organizationId?: string;
}

export interface ProjectsResponse {
  success: boolean;
  message?: string;
  timestamp: string;
  projects: Project[];
  total_count: number;
}

export interface ProjectResponse {
  success: boolean;
  message?: string;
  timestamp: string;
  project: Project;
}

export const projectsService = {
  /**
   * List all available projects
   */
  async listProjects(verbose: boolean = false): Promise<Project[]> {
    try {
      const response = await apiClient.get<ProjectsResponse>('/projects', {
        params: { verbose }
      });
      
      const data = handleApiResponse(response);
      return data.projects;
    } catch (error: any) {
      return handleApiError(error);
    }
  },

  /**
   * Get details of a specific project
   */
  async getProject(projectId: string, verbose: boolean = false): Promise<Project> {
    try {
      const response = await apiClient.get<ProjectResponse>(`/projects/${projectId}`, {
        params: { verbose }
      });
      
      const data = handleApiResponse(response);
      return data.project;
    } catch (error: any) {
      return handleApiError(error);
    }
  },
};
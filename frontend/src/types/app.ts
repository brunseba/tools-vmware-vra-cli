// UI state types
export interface User {
  username: string;
  tenant?: string;
  domain?: string;
  isAuthenticated: boolean;
}

export interface AppSettings {
  darkMode: boolean;
  apiBaseUrl: string;
  defaultProject?: string;
  pageSize: number;
  autoRefresh: boolean;
  refreshInterval: number;
}

export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  children?: NavigationItem[];
  badge?: string | number;
  disabled?: boolean;
}

// Filter and search types
export interface FilterState {
  search: string;
  status: string[];
  type: string[];
  project: string;
  dateRange: {
    start?: Date;
    end?: Date;
  };
}

// Table and grid types
export interface SortState {
  field: string;
  direction: 'asc' | 'desc';
}

export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}

// Notification types
export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: Date;
  autoHide?: boolean;
  duration?: number;
}

// Feature flags
export interface FeatureFlags {
  enableReports: boolean;
  enableWorkflows: boolean;
  enableBulkOperations: boolean;
  enableRealTimeUpdates: boolean;
  enableExport: boolean;
}

// Theme types
export interface ThemeConfig {
  mode: 'light' | 'dark';
  primaryColor: string;
  secondaryColor: string;
  fontSize: 'small' | 'medium' | 'large';
}

// Error handling
export interface AppError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: Date;
  stack?: string;
}
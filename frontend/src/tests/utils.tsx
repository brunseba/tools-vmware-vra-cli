import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { useSettingsStore } from '@/store/settingsStore'
import { useAuthStore } from '@/store/authStore'

// Mock stores for testing
const mockSettingsStore = {
  settings: {
    darkMode: false,
    apiBaseUrl: '/api',
    defaultProject: 'test-project',
    pageSize: 25,
    autoRefresh: false,
    refreshInterval: 30000,
  },
  theme: {
    mode: 'light' as const,
    primaryColor: '#1976d2',
    secondaryColor: '#dc004e',
    fontSize: 'medium' as const,
  },
  featureFlags: {
    enableReports: true,
    enableWorkflows: true,
    enableBulkOperations: true,
    enableRealTimeUpdates: false,
    enableExport: true,
  },
  notifications: [],
  updateSettings: jest.fn(),
  updateTheme: jest.fn(),
  toggleDarkMode: jest.fn(),
  updateFeatureFlags: jest.fn(),
  addNotification: jest.fn(),
  removeNotification: jest.fn(),
  clearNotifications: jest.fn(),
}

const mockAuthStore = {
  user: {
    username: 'testuser',
    tenant: 'test.local',
    domain: 'test',
    isAuthenticated: true,
  },
  isLoading: false,
  error: null,
  login: jest.fn(),
  logout: jest.fn(),
  checkAuthStatus: jest.fn(),
  refreshToken: jest.fn(),
  clearError: jest.fn(),
  setUser: jest.fn(),
}

// Mock the stores
jest.mock('@/store/settingsStore', () => ({
  useSettingsStore: () => mockSettingsStore,
}))

jest.mock('@/store/authStore', () => ({
  useAuthStore: () => mockAuthStore,
}))

// Test theme
const testTheme = createTheme({
  palette: {
    mode: 'light',
  },
})

// Custom render function with all providers
interface AllTheProvidersProps {
  children: React.ReactNode
}

const AllTheProviders: React.FC<AllTheProvidersProps> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: 0,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ThemeProvider theme={testTheme}>
          <CssBaseline />
          {children}
        </ThemeProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }

// Helper functions for testing
export const createMockCatalogItem = (overrides = {}) => ({
  id: 'test-catalog-item',
  name: 'Test Catalog Item',
  type: { name: 'com.vmw.blueprint' },
  status: 'PUBLISHED',
  version: '1.0',
  description: 'Test catalog item description',
  ...overrides,
})

export const createMockDeployment = (overrides = {}) => ({
  id: 'test-deployment',
  name: 'Test Deployment',
  status: 'CREATE_SUCCESSFUL',
  projectId: 'test-project',
  catalogItemId: 'test-catalog-item',
  createdAt: '2024-01-01T00:00:00Z',
  completedAt: '2024-01-01T00:05:00Z',
  inputs: { hostname: 'test-vm' },
  ...overrides,
})

export const createMockApiResponse = <T extends object>(data: T, overrides = {}) => ({
  success: true,
  message: 'Success',
  timestamp: new Date().toISOString(),
  ...data,
  ...overrides,
})

// Mock API responses
export const mockApiResponses = {
  catalogItems: createMockApiResponse({
    items: [createMockCatalogItem()],
    total_count: 1,
    page_info: { page_size: 25, first_page_only: false },
  }),
  
  deployments: createMockApiResponse({
    deployments: [createMockDeployment()],
    total_count: 1,
    page_info: { page_size: 25, first_page_only: false },
  }),
  
  catalogSchema: createMockApiResponse({
    item_schema: {
      type: 'object',
      properties: {
        hostname: {
          type: 'string',
          title: 'Hostname',
          description: 'Server hostname',
        },
        cpu: {
          type: 'integer',
          title: 'CPU Count',
          minimum: 1,
          maximum: 8,
          default: 2,
        },
      },
      required: ['hostname'],
    },
  }),
}

// Utility to wait for async operations
export const waitForLoadingToFinish = () => 
  new Promise(resolve => setTimeout(resolve, 0))

// Reset mocks helper
export const resetMocks = () => {
  Object.values(mockSettingsStore).forEach(fn => {
    if (typeof fn === 'function') fn.mockClear?.()
  })
  Object.values(mockAuthStore).forEach(fn => {
    if (typeof fn === 'function') fn.mockClear?.()
  })
}
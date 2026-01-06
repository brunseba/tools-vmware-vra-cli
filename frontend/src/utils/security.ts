import { User } from '@/types/app'

// Permission constants based on vRA RBAC
export const PERMISSIONS = {
  // Catalog permissions
  CATALOG_VIEW: 'catalog:view',
  CATALOG_REQUEST: 'catalog:request',
  CATALOG_MANAGE: 'catalog:manage',
  
  // Deployment permissions
  DEPLOYMENT_VIEW: 'deployment:view',
  DEPLOYMENT_MANAGE: 'deployment:manage',
  DEPLOYMENT_DELETE: 'deployment:delete',
  DEPLOYMENT_EXECUTE_ACTIONS: 'deployment:execute-actions',
  
  // Project permissions
  PROJECT_VIEW: 'project:view',
  PROJECT_MANAGE: 'project:manage',
  
  // Admin permissions
  ADMIN_USER_MANAGEMENT: 'admin:user-management',
  ADMIN_SYSTEM_CONFIG: 'admin:system-config',
  
  // Workflow permissions
  WORKFLOW_VIEW: 'workflow:view',
  WORKFLOW_EXECUTE: 'workflow:execute',
  
  // Report permissions
  REPORT_VIEW: 'report:view',
  REPORT_EXPORT: 'report:export',
} as const

export type Permission = typeof PERMISSIONS[keyof typeof PERMISSIONS]

// Role-based permission mapping
export const ROLE_PERMISSIONS: Record<string, Permission[]> = {
  'administrator': Object.values(PERMISSIONS),
  'service-architect': [
    PERMISSIONS.CATALOG_VIEW,
    PERMISSIONS.CATALOG_MANAGE,
    PERMISSIONS.DEPLOYMENT_VIEW,
    PERMISSIONS.DEPLOYMENT_MANAGE,
    PERMISSIONS.PROJECT_VIEW,
    PERMISSIONS.PROJECT_MANAGE,
    PERMISSIONS.WORKFLOW_VIEW,
    PERMISSIONS.WORKFLOW_EXECUTE,
    PERMISSIONS.REPORT_VIEW,
    PERMISSIONS.REPORT_EXPORT,
  ],
  'developer': [
    PERMISSIONS.CATALOG_VIEW,
    PERMISSIONS.CATALOG_REQUEST,
    PERMISSIONS.DEPLOYMENT_VIEW,
    PERMISSIONS.DEPLOYMENT_MANAGE,
    PERMISSIONS.PROJECT_VIEW,
    PERMISSIONS.WORKFLOW_VIEW,
    PERMISSIONS.WORKFLOW_EXECUTE,
    PERMISSIONS.REPORT_VIEW,
  ],
  'consumer': [
    PERMISSIONS.CATALOG_VIEW,
    PERMISSIONS.CATALOG_REQUEST,
    PERMISSIONS.DEPLOYMENT_VIEW,
    PERMISSIONS.PROJECT_VIEW,
    PERMISSIONS.REPORT_VIEW,
  ],
  'viewer': [
    PERMISSIONS.CATALOG_VIEW,
    PERMISSIONS.DEPLOYMENT_VIEW,
    PERMISSIONS.PROJECT_VIEW,
    PERMISSIONS.REPORT_VIEW,
  ],
}

// User role extraction from vRA authentication
export const getUserRoles = (user: User): string[] => {
  // In a real implementation, this would extract roles from JWT token
  // or from user profile API response
  // For now, we'll simulate based on domain/tenant info
  
  if (!user.isAuthenticated) return []
  
  // Extract roles from user context (this is a simulation)
  // In production, this would come from the authentication token or user profile
  const simulatedRoles: string[] = []
  
  // Admin detection (example logic)
  if (user.username.includes('admin') || user.domain === 'vsphere.local') {
    simulatedRoles.push('administrator')
  }
  
  // Service architect detection
  if (user.username.includes('architect') || user.username.includes('service')) {
    simulatedRoles.push('service-architect')
  }
  
  // Developer detection
  if (user.username.includes('dev') || user.username.includes('engineer')) {
    simulatedRoles.push('developer')
  }
  
  // Default consumer role for authenticated users
  if (simulatedRoles.length === 0) {
    simulatedRoles.push('consumer')
  }
  
  return simulatedRoles
}

// Permission checking functions
export const hasPermission = (user: User, permission: Permission): boolean => {
  if (!user.isAuthenticated) return false
  
  const userRoles = getUserRoles(user)
  
  return userRoles.some(role => 
    ROLE_PERMISSIONS[role]?.includes(permission) || false
  )
}

export const hasAnyPermission = (user: User, permissions: Permission[]): boolean => {
  return permissions.some(permission => hasPermission(user, permission))
}

export const hasAllPermissions = (user: User, permissions: Permission[]): boolean => {
  return permissions.every(permission => hasPermission(user, permission))
}

// Project-specific permission checking
export const hasProjectAccess = (user: User, projectId: string, permission: Permission): boolean => {
  if (!hasPermission(user, permission)) return false
  
  // In a real implementation, this would check project-specific permissions
  // For now, we'll allow access if user has the base permission
  return true
}

// Security utilities
export const sanitizeUserInput = (input: string): string => {
  return input
    .replace(/[<>]/g, '') // Remove potential HTML
    .replace(/['"]/g, '') // Remove quotes
    .trim()
}

export const validateDeploymentName = (name: string): { valid: boolean; error?: string } => {
  const sanitized = sanitizeUserInput(name)
  
  if (!sanitized) {
    return { valid: false, error: 'Deployment name is required' }
  }
  
  if (sanitized.length < 3) {
    return { valid: false, error: 'Deployment name must be at least 3 characters' }
  }
  
  if (sanitized.length > 64) {
    return { valid: false, error: 'Deployment name must be less than 64 characters' }
  }
  
  if (!/^[a-zA-Z0-9-_]+$/.test(sanitized)) {
    return { valid: false, error: 'Deployment name can only contain letters, numbers, hyphens, and underscores' }
  }
  
  return { valid: true }
}

// Content Security Policy helpers
export const isValidUrl = (url: string): boolean => {
  try {
    const parsed = new URL(url)
    return ['http:', 'https:'].includes(parsed.protocol)
  } catch {
    return false
  }
}

export const sanitizeApiUrl = (url: string): string => {
  try {
    const parsed = new URL(url)
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      throw new Error('Invalid protocol')
    }
    return parsed.toString()
  } catch {
    throw new Error('Invalid URL format')
  }
}

// Session management
export const isSessionValid = (user: User | null): boolean => {
  if (!user?.isAuthenticated) return false
  
  // In a real implementation, check token expiry
  return true
}

export const getSecurityHeaders = (): Record<string, string> => {
  return {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
  }
}

// Audit logging helpers
export const createAuditLog = (action: string, resource: string, user: User) => {
  // In production, this would send to audit logging system
  console.log('AUDIT:', {
    timestamp: new Date().toISOString(),
    user: user.username,
    tenant: user.tenant,
    action,
    resource,
  })
}

// Rate limiting (client-side)
const actionCounts = new Map<string, { count: number; resetTime: number }>()

export const isRateLimited = (action: string, limit = 10, windowMs = 60000): boolean => {
  const now = Date.now()
  const key = action
  const current = actionCounts.get(key)
  
  if (!current || now > current.resetTime) {
    actionCounts.set(key, { count: 1, resetTime: now + windowMs })
    return false
  }
  
  if (current.count >= limit) {
    return true
  }
  
  current.count++
  return false
}
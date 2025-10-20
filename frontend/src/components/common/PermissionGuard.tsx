import React from 'react'
import { Alert, Box, Typography } from '@mui/material'
import { Lock } from '@mui/icons-material'
import { useAuthStore } from '@/store/authStore'
import { Permission, hasPermission, hasAnyPermission, hasAllPermissions } from '@/utils/security'

interface PermissionGuardProps {
  children: React.ReactNode
  permission?: Permission
  permissions?: Permission[]
  requireAll?: boolean
  fallback?: React.ReactNode
  showFallback?: boolean
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  children,
  permission,
  permissions,
  requireAll = false,
  fallback,
  showFallback = true,
}) => {
  const { user } = useAuthStore()

  // Check permissions
  const hasRequiredPermission = React.useMemo(() => {
    if (!user?.isAuthenticated) return false

    if (permission) {
      return hasPermission(user, permission)
    }

    if (permissions) {
      return requireAll 
        ? hasAllPermissions(user, permissions)
        : hasAnyPermission(user, permissions)
    }

    // If no permissions specified, allow authenticated users
    return true
  }, [user, permission, permissions, requireAll])

  if (hasRequiredPermission) {
    return <>{children}</>
  }

  if (fallback) {
    return <>{fallback}</>
  }

  if (!showFallback) {
    return null
  }

  return (
    <Box sx={{ p: 3, textAlign: 'center' }}>
      <Alert 
        severity="warning" 
        icon={<Lock />}
        sx={{ mb: 2, display: 'inline-flex', textAlign: 'left' }}
      >
        <Typography variant="body2">
          <strong>Access Restricted</strong>
          <br />
          You don't have the required permissions to access this feature.
          {permission && (
            <><br />Required permission: <code>{permission}</code></>
          )}
          {permissions && (
            <>
              <br />Required permissions ({requireAll ? 'all' : 'any'}): 
              <br />
              {permissions.map(p => <code key={p}>{p}</code>).reduce((prev, curr, index) => 
                prev.concat(index < permissions.length - 1 ? ', ' : '', curr)
              )}
            </>
          )}
        </Typography>
      </Alert>
    </Box>
  )
}

// Convenience wrapper for single permission
export const RequirePermission: React.FC<{
  children: React.ReactNode
  permission: Permission
  fallback?: React.ReactNode
}> = ({ children, permission, fallback }) => (
  <PermissionGuard permission={permission} fallback={fallback}>
    {children}
  </PermissionGuard>
)

// Convenience wrapper for multiple permissions (any)
export const RequireAnyPermission: React.FC<{
  children: React.ReactNode
  permissions: Permission[]
  fallback?: React.ReactNode
}> = ({ children, permissions, fallback }) => (
  <PermissionGuard 
    permissions={permissions} 
    requireAll={false} 
    fallback={fallback}
  >
    {children}
  </PermissionGuard>
)

// Convenience wrapper for multiple permissions (all)
export const RequireAllPermissions: React.FC<{
  children: React.ReactNode
  permissions: Permission[]
  fallback?: React.ReactNode
}> = ({ children, permissions, fallback }) => (
  <PermissionGuard 
    permissions={permissions} 
    requireAll={true} 
    fallback={fallback}
  >
    {children}
  </PermissionGuard>
)
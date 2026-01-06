import React, { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { CircularProgress, Box } from '@mui/material'
import { useAuthStore } from '@/store/authStore'

interface AuthGuardProps {
  children: React.ReactNode
}

export const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const { user, isLoading, checkAuthStatus } = useAuthStore()

  useEffect(() => {
    // Check auth status on component mount
    if (!user) {
      checkAuthStatus()
    }
  }, [user, checkAuthStatus])

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    )
  }

  if (!user?.isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authService } from '@/services/auth'
import { useAuthStore } from '@/store/authStore'
import { useSettingsStore } from '@/store/settingsStore'
import { AuthRequest } from '@/types/api'

export const useLogin = () => {
  const navigate = useNavigate()
  const { setUser } = useAuthStore()
  const { addNotification } = useSettingsStore()
  
  return useMutation({
    mutationFn: async (credentials: AuthRequest) => {
      return authService.login(credentials)
    },
    onSuccess: (response, credentials) => {
      const user = {
        username: credentials.username,
        tenant: credentials.tenant,
        domain: credentials.domain,
        isAuthenticated: true,
      }
      
      setUser(user)
      addNotification({
        type: 'success',
        title: 'Login Successful',
        message: `Welcome, ${credentials.username}!`,
      })
      navigate('/dashboard')
    },
    onError: (error: Error) => {
      addNotification({
        type: 'error',
        title: 'Login Failed',
        message: error.message || 'Unable to authenticate with vRA server',
      })
    },
  })
}

export const useLogout = () => {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const { setUser } = useAuthStore()
  const { addNotification } = useSettingsStore()
  
  return useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      setUser(null)
      queryClient.clear() // Clear all cached data
      addNotification({
        type: 'info',
        title: 'Logged Out',
        message: 'You have been successfully logged out',
      })
      navigate('/login')
    },
    onError: (error: Error) => {
      // Even on error, clear local state
      setUser(null)
      queryClient.clear()
      navigate('/login')
    },
  })
}

export const useAuthStatus = () => {
  const { user } = useAuthStore()
  
  return useQuery({
    queryKey: ['auth', 'status'],
    queryFn: authService.getStatus,
    enabled: !!user?.isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  })
}

export const useRefreshToken = () => {
  const { addNotification } = useSettingsStore()
  
  return useMutation({
    mutationFn: authService.refreshToken,
    onSuccess: () => {
      addNotification({
        type: 'success',
        title: 'Session Refreshed',
        message: 'Your authentication session has been renewed',
      })
    },
    onError: (error: Error) => {
      addNotification({
        type: 'warning',
        title: 'Session Expired',
        message: 'Please log in again to continue',
      })
    },
  })
}
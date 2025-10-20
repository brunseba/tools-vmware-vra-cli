import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  FormControlLabel,
  Switch,
  Divider,
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
  Person,
  VpnKey,
  Language,
  Business,
  Cloud,
} from '@mui/icons-material'
import { useAuthStore } from '@/store/authStore'
import { useSettingsStore } from '@/store/settingsStore'
import { useLogin } from '@/hooks/useAuth'
import { AuthRequest } from '@/types/api'

export const LoginForm: React.FC = () => {
  const { error, clearError } = useAuthStore()
  const { toggleDarkMode, theme } = useSettingsStore()
  const loginMutation = useLogin()
  
  const [credentials, setCredentials] = useState<AuthRequest>({
    username: '',
    password: '',
    url: 'https://',
    tenant: '',
    domain: '',
  })
  
  const [showPassword, setShowPassword] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleChange = (field: keyof AuthRequest) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setCredentials(prev => ({
      ...prev,
      [field]: event.target.value
    }))
    
    // Clear error when user starts typing
    if (error) {
      clearError()
    }
    if (loginMutation.isError) {
      loginMutation.reset()
    }
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    
    try {
      await loginMutation.mutateAsync(credentials)
    } catch (err) {
      // Error handling is done in the mutation hook
      console.error('Login failed:', err)
    }
  }

  const isValidForm = credentials.username && credentials.password && credentials.url
  const isLoading = loginMutation.isPending
  const loginError = error || (loginMutation.isError ? loginMutation.error?.message : null)

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: theme.mode === 'dark' 
          ? 'linear-gradient(135deg, #1e1e1e 0%, #2d2d30 100%)'
          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 480, width: '100%', boxShadow: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Cloud sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            <Typography variant="h4" component="h1" gutterBottom>
              VMware vRA
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Sign in to access your vRealize Automation environment
            </Typography>
          </Box>

          {loginError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {loginError}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Username"
              value={credentials.username}
              onChange={handleChange('username')}
              margin="normal"
              required
              autoComplete="username"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Person />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Password"
              type={showPassword ? 'text' : 'password'}
              value={credentials.password}
              onChange={handleChange('password')}
              margin="normal"
              required
              autoComplete="current-password"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <VpnKey />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="vRA Server URL"
              value={credentials.url}
              onChange={handleChange('url')}
              margin="normal"
              required
              placeholder="https://vra.company.com"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Cloud />
                  </InputAdornment>
                ),
              }}
            />

            <Box sx={{ mt: 2, mb: 2 }}>
              <Button
                variant="text"
                size="small"
                onClick={() => setShowAdvanced(!showAdvanced)}
                sx={{ textTransform: 'none' }}
              >
                {showAdvanced ? 'Hide' : 'Show'} Advanced Options
              </Button>
            </Box>

            {showAdvanced && (
              <>
                <TextField
                  fullWidth
                  label="Tenant (Optional)"
                  value={credentials.tenant}
                  onChange={handleChange('tenant')}
                  margin="normal"
                  placeholder="company.local"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Business />
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  label="Domain (Optional)"
                  value={credentials.domain}
                  onChange={handleChange('domain')}
                  margin="normal"
                  placeholder="mydomain"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Language />
                      </InputAdornment>
                    ),
                  }}
                />
              </>
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={!isValidForm || isLoading}
              sx={{ mt: 3, mb: 2, py: 1.5 }}
            >
              {isLoading ? 'Signing In...' : 'Sign In'}
            </Button>
          </form>

          <Divider sx={{ my: 2 }} />
          
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={theme.mode === 'dark'}
                  onChange={toggleDarkMode}
                  size="small"
                />
              }
              label="Dark Mode"
              sx={{ fontSize: '0.875rem' }}
            />
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}
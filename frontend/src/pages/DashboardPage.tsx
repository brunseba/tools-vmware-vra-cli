import React from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Skeleton,
  Alert,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  CloudQueue,
  Assignment,
  Timeline,
  TrendingUp,
} from '@mui/icons-material'
import { useCatalogStats } from '@/hooks/useCatalog'
import { useDeploymentStats } from '@/hooks/useDeployments'
import { useSettingsStore } from '@/store/settingsStore'

export const DashboardPage: React.FC = () => {
  const { settings } = useSettingsStore()
  
  // Fetch real data
  const { 
    data: catalogStats, 
    isLoading: catalogLoading, 
    error: catalogError 
  } = useCatalogStats(settings.defaultProject)
  
  const { 
    data: deploymentStats, 
    isLoading: deploymentLoading, 
    error: deploymentError 
  } = useDeploymentStats(settings.defaultProject)

  const isLoading = catalogLoading || deploymentLoading
  const hasError = catalogError || deploymentError

  if (hasError) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <DashboardIcon sx={{ mr: 1, fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Dashboard
          </Typography>
        </Box>
        
        <Alert severity="error">
          Failed to load dashboard data. Please check your connection and authentication.
        </Alert>
      </Box>
    )
  }

  const renderMetricCard = (icon: React.ReactNode, title: string, value: number | string, subtitle: string, showProgress = false) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {icon}
          <Typography variant="h6" component="h2">
            {title}
          </Typography>
        </Box>
        {isLoading ? (
          <Skeleton variant="text" width="60%" height={48} />
        ) : (
          <Typography variant="h3" component="p" sx={{ fontWeight: 'bold' }}>
            {typeof value === 'number' && showProgress ? `${value.toFixed(1)}%` : value}
          </Typography>
        )}
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
        {showProgress && !isLoading && typeof value === 'number' && (
          <LinearProgress
            variant="determinate"
            value={value}
            sx={{ mt: 1, height: 6, borderRadius: 3 }}
          />
        )}
      </CardContent>
    </Card>
  )

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <DashboardIcon sx={{ mr: 1, fontSize: 32 }} />
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
      </Box>

      {!settings.defaultProject && (
        <Alert severity="info" sx={{ mb: 3 }}>
          No default project configured. Some metrics may be limited. Configure a default project in settings for better insights.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Metrics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            <CloudQueue sx={{ color: 'primary.main', mr: 1 }} />,
            'Catalog Items',
            catalogStats?.totalItems || 0,
            'Available for deployment'
          )}
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            <Assignment sx={{ color: 'success.main', mr: 1 }} />,
            'Deployments',
            deploymentStats?.totalDeployments || 0,
            'Total deployments'
          )}
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            <Timeline sx={{ color: 'warning.main', mr: 1 }} />,
            'Active',
            deploymentStats?.activeDeployments || 0,
            'Currently running'
          )}
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            <TrendingUp sx={{ color: 'success.main', mr: 1 }} />,
            'Success Rate',
            deploymentStats?.successRate || 0,
            'Recent deployments',
            true
          )}
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
              Recent Activity
            </Typography>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                Activity timeline will be displayed here
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Connect to your vRA environment to see deployment activity
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
              Quick Actions
            </Typography>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                Quick deployment actions will be available here
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Browse catalog items to get started
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
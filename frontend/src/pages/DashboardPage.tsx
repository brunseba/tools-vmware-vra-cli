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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Divider,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  CloudQueue,
  Assignment,
  Timeline,
  TrendingUp,
  CheckCircle,
  Error as ErrorIcon,
  HourglassEmpty,
  Refresh as RefreshIcon,
  OpenInNew,
  RocketLaunch,
  Star,
} from '@mui/icons-material'
import { useCatalogStats } from '@/hooks/useCatalog'
import { useDeploymentStats, useDeployments } from '@/hooks/useDeployments'
import { useCatalogUsageReport } from '@/hooks/useReports'
import { useSettingsStore } from '@/store/settingsStore'
import { useNavigate } from 'react-router-dom'

export const DashboardPage: React.FC = () => {
  const { settings } = useSettingsStore()
  const navigate = useNavigate()
  
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

  // Fetch recent deployments for activity
  const { 
    data: recentDeploymentsData, 
    isLoading: recentLoading, 
    error: recentError,
    refetch: refetchRecent
  } = useDeployments({
    project_id: settings.defaultProject,
    page_size: 10, // Get latest 10 deployments
  })

  // Fetch catalog usage for top items
  const { 
    data: catalogUsage, 
    isLoading: catalogUsageLoading,
    error: catalogUsageError 
  } = useCatalogUsageReport({
    projectId: settings.defaultProject,
    includeZero: false,
    sortBy: 'deployments',
    detailedResources: false,
  })

  const isLoading = catalogLoading || deploymentLoading
  const hasError = catalogError || deploymentError

  const getStatusIcon = (status: string) => {
    if (status.includes('SUCCESS')) {
      return <CheckCircle sx={{ color: 'success.main' }} />
    } else if (status.includes('FAILED')) {
      return <ErrorIcon sx={{ color: 'error.main' }} />
    } else if (status.includes('INPROGRESS')) {
      return <HourglassEmpty sx={{ color: 'warning.main' }} />
    }
    return <Timeline sx={{ color: 'info.main' }} />
  }

  const getStatusColor = (status: string): 'success' | 'error' | 'warning' | 'default' => {
    if (status.includes('SUCCESS')) return 'success'
    if (status.includes('FAILED')) return 'error'
    if (status.includes('INPROGRESS')) return 'warning'
    return 'default'
  }

  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

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
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" component="h2">
                Recent Activity
              </Typography>
              <IconButton size="small" onClick={() => refetchRecent()}>
                <RefreshIcon />
              </IconButton>
            </Box>
            
            {recentLoading ? (
              <Box>
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} variant="rectangular" height={60} sx={{ mb: 1 }} />
                ))}
              </Box>
            ) : recentError ? (
              <Alert severity="error">
                Failed to load recent activity. Please check your connection.
              </Alert>
            ) : recentDeploymentsData && recentDeploymentsData.deployments.length > 0 ? (
              <List sx={{ width: '100%' }}>
                {recentDeploymentsData.deployments.slice(0, 8).map((deployment, index) => (
                  <React.Fragment key={deployment.id}>
                    <ListItem
                      secondaryAction={
                        <IconButton 
                          edge="end" 
                          onClick={() => navigate(`/deployments/${deployment.id}`)}
                        >
                          <OpenInNew />
                        </IconButton>
                      }
                      sx={{ 
                        cursor: 'pointer',
                        '&:hover': { bgcolor: 'action.hover' }
                      }}
                      onClick={() => navigate(`/deployments/${deployment.id}`)}
                    >
                      <ListItemIcon>
                        {getStatusIcon(deployment.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1">
                              {deployment.name}
                            </Typography>
                            <Chip 
                              label={deployment.status} 
                              size="small"
                              color={getStatusColor(deployment.status)}
                            />
                          </Box>
                        }
                        secondary={
                          <Box sx={{ display: 'flex', gap: 2, mt: 0.5 }}>
                            <Typography variant="caption" color="text.secondary">
                              {formatTimeAgo(deployment.lastUpdatedAt || deployment.createdAt)}
                            </Typography>
                            {deployment.projectName && (
                              <Typography variant="caption" color="text.secondary">
                                • {deployment.projectName}
                              </Typography>
                            )}
                            {deployment.catalogItemName && (
                              <Typography variant="caption" color="text.secondary">
                                • {deployment.catalogItemName}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < Math.min(recentDeploymentsData.deployments.length - 1, 7) && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" color="text.secondary">
                  No recent activity
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Deploy from catalog to see activity here
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" component="h2">
                Popular Catalog Items
              </Typography>
              <Star sx={{ color: 'warning.main' }} />
            </Box>
            
            {catalogUsageLoading ? (
              <Box>
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} variant="rectangular" height={70} sx={{ mb: 1, borderRadius: 1 }} />
                ))}
              </Box>
            ) : catalogUsageError ? (
              <Alert severity="info" sx={{ mt: 2 }}>
                Unable to load popular items
              </Alert>
            ) : catalogUsage && catalogUsage.usage_stats.length > 0 ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {catalogUsage.usage_stats.slice(0, 5).map((item, index) => (
                  <Card 
                    key={item.id} 
                    variant="outlined"
                    sx={{ 
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': { 
                        boxShadow: 2,
                        transform: 'translateY(-2px)',
                        borderColor: 'primary.main'
                      }
                    }}
                    onClick={() => navigate(`/catalog/${item.id}`)}
                  >
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <Typography 
                              variant="body1" 
                              sx={{ 
                                fontWeight: 'medium',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}
                            >
                              {item.name.length > 25 ? item.name.substring(0, 25) + '...' : item.name}
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
                            <Chip 
                              label={`${item.deployment_count} deploys`} 
                              size="small" 
                              color="primary"
                              variant="outlined"
                            />
                            <Chip 
                              label={`${item.success_rate.toFixed(0)}% success`} 
                              size="small" 
                              color={item.success_rate >= 80 ? 'success' : 'warning'}
                              variant="outlined"
                            />
                          </Box>
                        </Box>
                        <IconButton 
                          size="small" 
                          color="primary"
                          onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/catalog/${item.id}`)
                          }}
                        >
                          <RocketLaunch fontSize="small" />
                        </IconButton>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" color="text.secondary">
                  No catalog items used yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Browse catalog to get started
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
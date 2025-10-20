import React from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  CloudQueue,
  Assignment,
  Timeline,
  TrendingUp,
} from '@mui/icons-material'

export const DashboardPage: React.FC = () => {
  // Mock data for now - will be replaced with real API calls
  const metrics = {
    totalCatalogItems: 156,
    totalDeployments: 89,
    activeDeployments: 23,
    successRate: 94.2,
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <DashboardIcon sx={{ mr: 1, fontSize: 32 }} />
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Metrics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CloudQueue sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6" component="h2">
                  Catalog Items
                </Typography>
              </Box>
              <Typography variant="h3" component="p" sx={{ fontWeight: 'bold' }}>
                {metrics.totalCatalogItems}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Available for deployment
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Assignment sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="h6" component="h2">
                  Deployments
                </Typography>
              </Box>
              <Typography variant="h3" component="p" sx={{ fontWeight: 'bold' }}>
                {metrics.totalDeployments}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total deployments
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Timeline sx={{ color: 'warning.main', mr: 1 }} />
                <Typography variant="h6" component="h2">
                  Active
                </Typography>
              </Box>
              <Typography variant="h3" component="p" sx={{ fontWeight: 'bold' }}>
                {metrics.activeDeployments}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Currently running
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="h6" component="h2">
                  Success Rate
                </Typography>
              </Box>
              <Typography variant="h3" component="p" sx={{ fontWeight: 'bold' }}>
                {metrics.successRate}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics.successRate}
                sx={{ mt: 1, height: 6, borderRadius: 3 }}
              />
            </CardContent>
          </Card>
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
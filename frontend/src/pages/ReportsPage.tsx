import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Paper,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  ButtonGroup,
  Menu,
  MenuItem as MenuOption,
  IconButton,
  Snackbar,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  CloudQueue as DeployIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Schedule as ScheduleIcon,
  People as PeopleIcon,
  Storage as StorageIcon,
  Download as DownloadIcon,
  DateRange as DateRangeIcon,
  FileDownload as FileDownloadIcon,
  GetApp as GetAppIcon,
  PictureAsPdf as PictureAsPdfIcon,
} from '@mui/icons-material';
import { useSettingsStore } from '@/store/settingsStore';
import { AnalyticsChart, ResourceUsageChart } from '@/components/charts/AnalyticsChart';
import { exportAnalyticsData } from '../utils/exportUtils';

// Mock data - replace with real data from API
const mockStats = {
  totalDeployments: 142,
  activeDeployments: 89,
  failedDeployments: 8,
  totalUsers: 23,
  recentActivity: [
    { id: '1', type: 'deployment', action: 'Created', resource: 'Web Server VM', user: 'John Doe', time: '2 minutes ago' },
    { id: '2', type: 'failure', action: 'Failed', resource: 'Database Cluster', user: 'Jane Smith', time: '15 minutes ago' },
    { id: '3', type: 'success', action: 'Completed', resource: 'Load Balancer', user: 'Bob Johnson', time: '1 hour ago' },
    { id: '4', type: 'deployment', action: 'Started', resource: 'Cache Server', user: 'Alice Brown', time: '2 hours ago' },
    { id: '5', type: 'success', action: 'Deployed', resource: 'Monitoring Stack', user: 'Charlie Wilson', time: '3 hours ago' },
  ],
  monthlyTrends: {
    deployments: [45, 52, 38, 61, 42, 58, 72, 68, 45, 52, 61, 89],
    successes: [42, 48, 35, 58, 39, 55, 69, 64, 43, 49, 58, 81],
    failures: [3, 4, 3, 3, 3, 3, 3, 4, 2, 3, 3, 8]
  },
};

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'deployment':
      return <DeployIcon fontSize="small" color="primary" />;
    case 'success':
      return <SuccessIcon fontSize="small" color="success" />;
    case 'failure':
      return <ErrorIcon fontSize="small" color="error" />;
    default:
      return <ScheduleIcon fontSize="small" />;
  }
};

export const ReportsPage: React.FC = () => {
  const { settings, featureFlags } = useSettingsStore();
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState('deployments');
  const [exportAnchorEl, setExportAnchorEl] = useState<null | HTMLElement>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const handleExportClick = (event: React.MouseEvent<HTMLElement>) => {
    setExportAnchorEl(event.currentTarget);
  };

  const handleExportClose = () => {
    setExportAnchorEl(null);
  };

  const handleExport = (format: 'csv' | 'json' | 'pdf') => {
    try {
      const stats = {
        totalDeployments: mockStats.totalDeployments,
        activeDeployments: mockStats.activeDeployments,
        failedDeployments: mockStats.failedDeployments,
        totalUsers: mockStats.totalUsers,
      };

      exportAnalyticsData(stats, timeRange, format);
      
      setSnackbarMessage(`Report exported successfully as ${format.toUpperCase()}`);
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Export failed:', error);
      setSnackbarMessage('Failed to export report. Please try again.');
      setSnackbarOpen(true);
    }
    handleExportClose();
  };

  if (!featureFlags.enableReports) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Alert severity="info">
          <Typography variant="h6" gutterBottom>
            Reports & Analytics Disabled
          </Typography>
          <Typography variant="body2">
            This feature is currently disabled. Enable it in Settings → Feature Flags.
          </Typography>
          <Button 
            size="small" 
            sx={{ mt: 1 }}
            onClick={() => window.location.href = '/settings'}
          >
            Go to Settings
          </Button>
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AnalyticsIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            Reports & Analytics
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="7d">Last 7 days</MenuItem>
              <MenuItem value="30d">Last 30 days</MenuItem>
              <MenuItem value="90d">Last 90 days</MenuItem>
              <MenuItem value="1y">Last year</MenuItem>
            </Select>
          </FormControl>
          
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            size="small"
            onClick={handleExportClick}
          >
            Export Report
          </Button>
          
          <Menu
            anchorEl={exportAnchorEl}
            open={Boolean(exportAnchorEl)}
            onClose={handleExportClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuOption onClick={() => handleExport('csv')}>
              <FileDownloadIcon sx={{ mr: 1 }} />
              Export as CSV
            </MenuOption>
            <MenuOption onClick={() => handleExport('json')}>
              <GetAppIcon sx={{ mr: 1 }} />
              Export as JSON
            </MenuOption>
            <MenuOption onClick={() => handleExport('pdf')}>
              <PictureAsPdfIcon sx={{ mr: 1 }} />
              Export as PDF
            </MenuOption>
          </Menu>
        </Box>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Total Deployments
                  </Typography>
                  <Typography variant="h4" component="div">
                    {mockStats.totalDeployments}
                  </Typography>
                </Box>
                <DeployIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
              <Box sx={{ mt: 1 }}>
                <Chip label="+12% vs last month" size="small" color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Active Deployments
                  </Typography>
                  <Typography variant="h4" component="div">
                    {mockStats.activeDeployments}
                  </Typography>
                </Box>
                <SuccessIcon sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
              <Box sx={{ mt: 1 }}>
                <Chip label="Healthy" size="small" color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Failed Deployments
                  </Typography>
                  <Typography variant="h4" component="div">
                    {mockStats.failedDeployments}
                  </Typography>
                </Box>
                <ErrorIcon sx={{ fontSize: 40, color: 'error.main' }} />
              </Box>
              <Box sx={{ mt: 1 }}>
                <Chip label="5.6% failure rate" size="small" color="warning" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Active Users
                  </Typography>
                  <Typography variant="h4" component="div">
                    {mockStats.totalUsers}
                  </Typography>
                </Box>
                <PeopleIcon sx={{ fontSize: 40, color: 'info.main' }} />
              </Box>
              <Box sx={{ mt: 1 }}>
                <Chip label="+3 this month" size="small" color="info" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Chart Placeholder */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardHeader 
              title="Deployment Trends" 
              subheader={`${timeRange === '7d' ? '7 days' : timeRange === '30d' ? '30 days' : timeRange === '90d' ? '90 days' : '1 year'} overview`}
              action={
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <Select
                    value={selectedMetric}
                    onChange={(e) => setSelectedMetric(e.target.value)}
                  >
                    <MenuItem value="deployments">Deployments</MenuItem>
                    <MenuItem value="successes">Success Rate</MenuItem>
                    <MenuItem value="resources">Resource Usage</MenuItem>
                  </Select>
                </FormControl>
              }
            />
            <CardContent>
              {selectedMetric === 'resources' ? (
                <ResourceUsageChart timeRange={timeRange} />
              ) : (
                <AnalyticsChart 
                  type={selectedMetric === 'successes' ? 'doughnut' : 'line'}
                  data={null}
                  timeRange={timeRange}
                  height={300}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Recent Activity */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardHeader title="Recent Activity" />
            <CardContent sx={{ pt: 0 }}>
              <List dense>
                {mockStats.recentActivity.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon>
                        {getActivityIcon(activity.type)}
                      </ListItemIcon>
                      <ListItemText
                        primary={`${activity.action} ${activity.resource}`}
                        secondary={`${activity.user} • ${activity.time}`}
                      />
                    </ListItem>
                    {index < mockStats.recentActivity.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
              <Button fullWidth size="small" sx={{ mt: 2 }}>
                View All Activity
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Resource Usage Summary */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="Resource Usage Summary" 
              subheader="Current resource utilization across all deployments"
            />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <StorageIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                    <Typography variant="h6">1.2 TB</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Storage Used
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip label="73% utilized" size="small" color="warning" />
                    </Box>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Box sx={{ 
                      width: 48, 
                      height: 48, 
                      bgcolor: 'info.main', 
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 1
                    }}>
                      <Typography variant="body2" color="white" fontWeight="bold">
                        CPU
                      </Typography>
                    </Box>
                    <Typography variant="h6">342 vCPUs</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total CPU Allocated
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip label="68% average usage" size="small" color="success" />
                    </Box>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Box sx={{ 
                      width: 48, 
                      height: 48, 
                      bgcolor: 'secondary.main', 
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 1
                    }}>
                      <Typography variant="body2" color="white" fontWeight="bold">
                        RAM
                      </Typography>
                    </Box>
                    <Typography variant="h6">896 GB</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Memory Allocated
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip label="82% average usage" size="small" color="warning" />
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
};

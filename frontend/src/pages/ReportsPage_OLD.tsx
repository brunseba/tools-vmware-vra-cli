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
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Divider,
  Switch,
  FormControlLabel,
  Menu,
  MenuItem as MenuOption,
  Snackbar,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Storage as StorageIcon,
  SyncProblem as SyncProblemIcon,
  Download as DownloadIcon,
  FileDownload as FileDownloadIcon,
  GetApp as GetAppIcon,
  PictureAsPdf as PictureAsPdfIcon,
} from '@mui/icons-material';
import { useSettingsStore } from '@/store/settingsStore';
import { 
  useActivityTimelineReport,
  useCatalogUsageReport,
  useResourcesUsageReport,
  useUnsyncReport,
} from '../hooks/useReports';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`report-tabpanel-${index}`}
      aria-labelledby={`report-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

export const ReportsPage: React.FC = () => {
  const { settings, featureFlags } = useSettingsStore();
  const [activeTab, setActiveTab] = useState(0);
  const [exportAnchorEl, setExportAnchorEl] = useState<null | HTMLElement>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // Activity Timeline state
  const [daysBack, setDaysBack] = useState(30);
  const [groupBy, setGroupBy] = useState<'day' | 'week' | 'month' | 'year'>('day');

  // Catalog Usage state
  const [includeZero, setIncludeZero] = useState(false);
  const [catalogSortBy, setCatalogSortBy] = useState<'deployments' | 'resources' | 'name'>('deployments');
  const [detailedResources, setDetailedResources] = useState(false);

  // Resources Usage state
  const [resourcesSortBy, setResourcesSortBy] = useState<'deployment-name' | 'catalog-item' | 'resource-count' | 'status'>('catalog-item');
  const [resourcesGroupBy, setResourcesGroupBy] = useState<'catalog-item' | 'resource-type' | 'deployment-status'>('catalog-item');
  const [resourcesDetailed, setResourcesDetailed] = useState(true);

  // Unsync Report state
  const [reasonFilter, setReasonFilter] = useState<string>('');

  // Data hooks
  const { data: activityTimeline, isLoading: activityLoading, error: activityError } = useActivityTimelineReport({
    projectId: settings.defaultProject,
    daysBack,
    groupBy,
  }, { enabled: activeTab === 0 });

  const { data: catalogUsage, isLoading: catalogLoading, error: catalogError } = useCatalogUsageReport({
    projectId: settings.defaultProject,
    includeZero,
    sortBy: catalogSortBy,
    detailedResources,
  }, { enabled: activeTab === 1 });

  const { data: resourcesUsage, isLoading: resourcesLoading, error: resourcesError } = useResourcesUsageReport({
    projectId: settings.defaultProject,
    detailedResources: resourcesDetailed,
    sortBy: resourcesSortBy,
    groupBy: resourcesGroupBy,
  }, { enabled: activeTab === 2 });

  const { data: unsyncReport, isLoading: unsyncLoading, error: unsyncError } = useUnsyncReport({
    projectId: settings.defaultProject,
    detailedResources: false,
    reasonFilter: reasonFilter || undefined,
  }, { enabled: activeTab === 3 });

  const handleExportClick = (event: React.MouseEvent<HTMLElement>) => {
    setExportAnchorEl(event.currentTarget);
  };

  const handleExportClose = () => {
    setExportAnchorEl(null);
  };

  const handleExport = (format: 'csv' | 'json' | 'pdf') => {
    try {
      if (!analyticsStats) {
        setSnackbarMessage('No data available for export');
        setSnackbarOpen(true);
        handleExportClose();
        return;
      }

      const stats = {
        totalDeployments: analyticsStats.totalDeployments,
        activeDeployments: analyticsStats.activeDeployments,
        failedDeployments: analyticsStats.failedDeployments,
        totalUsers: analyticsStats.totalUsers,
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

  // Error state
  if (statsError) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Alert severity="error">
          <Typography variant="h6" gutterBottom>
            Failed to Load Analytics
          </Typography>
          <Typography variant="body2">
            Unable to fetch analytics data. Please check your connection and try again.
          </Typography>
          <Typography variant="body2" sx={{ mt: 1, fontFamily: 'monospace', fontSize: '0.8rem' }}>
            Error: {statsError.message}
          </Typography>
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
                    {statsLoading ? '...' : (analyticsStats?.totalDeployments || 0)}
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
                    {statsLoading ? '...' : (analyticsStats?.activeDeployments || 0)}
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
                    {statsLoading ? '...' : (analyticsStats?.failedDeployments || 0)}
                  </Typography>
                </Box>
                <ErrorIcon sx={{ fontSize: 40, color: 'error.main' }} />
              </Box>
              <Box sx={{ mt: 1 }}>
                <Chip 
                  label={`${analyticsStats?.successRate?.toFixed(1) || 0}% success rate`} 
                  size="small" 
                  color={!analyticsStats || analyticsStats.successRate > 80 ? "success" : "warning"} 
                />
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
                    {statsLoading ? '...' : (analyticsStats?.totalUsers || 0)}
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
                {activityLoading ? (
                  Array.from({ length: 5 }).map((_, index) => (
                    <React.Fragment key={index}>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemIcon>
                          <ScheduleIcon fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Loading..."
                          secondary="Please wait"
                        />
                      </ListItem>
                      {index < 4 && <Divider />}
                    </React.Fragment>
                  ))
                ) : activityData && activityData.length > 0 ? (
                  activityData.map((activity, index) => (
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
                      {index < activityData.length - 1 && <Divider />}
                    </React.Fragment>
                  ))
                ) : (
                  <ListItem sx={{ px: 0 }}>
                    <ListItemText
                      primary="No recent activity"
                      secondary="No deployments found"
                    />
                  </ListItem>
                )}
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
                    <Typography variant="h6">
                      {resourceLoading ? '...' : `${resourceUsage?.totalStorage || 0} GB`}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Storage Allocated
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip 
                        label={resourceLoading ? 'Loading...' : `${resourceUsage?.storageUtilization?.toFixed(1) || 0}% utilized`} 
                        size="small" 
                        color={!resourceUsage || resourceUsage.storageUtilization < 80 ? "success" : "warning"} 
                      />
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
                    <Typography variant="h6">
                      {resourceLoading ? '...' : `${resourceUsage?.totalCpu || 0} vCPUs`}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total CPU Allocated
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip 
                        label={resourceLoading ? 'Loading...' : `${resourceUsage?.cpuUtilization?.toFixed(1) || 0}% usage`} 
                        size="small" 
                        color={!resourceUsage || resourceUsage.cpuUtilization < 80 ? "success" : "warning"} 
                      />
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
                    <Typography variant="h6">
                      {resourceLoading ? '...' : `${Math.round((resourceUsage?.totalMemory || 0) / 1024)} GB`}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Memory Allocated
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip 
                        label={resourceLoading ? 'Loading...' : `${resourceUsage?.memoryUtilization?.toFixed(1) || 0}% usage`} 
                        size="small" 
                        color={!resourceUsage || resourceUsage.memoryUtilization < 80 ? "success" : "warning"} 
                      />
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

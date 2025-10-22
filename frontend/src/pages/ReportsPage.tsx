import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
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
  Paper,
  Collapse,
  IconButton,
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
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  OpenInNew as OpenInNewIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
  KeyboardArrowUp as KeyboardArrowUpIcon,
} from '@mui/icons-material';
import { useSettingsStore } from '@/store/settingsStore';
import { useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();
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
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  // Resources Usage state
  const [resourcesSortBy, setResourcesSortBy] = useState<'deployment-name' | 'catalog-item' | 'resource-count' | 'status'>('catalog-item');
  const [resourcesGroupBy, setResourcesGroupBy] = useState<'catalog-item' | 'resource-type' | 'deployment-status'>('catalog-item');
  const [resourcesDetailed, setResourcesDetailed] = useState(true);

  // Unsync Report state
  const [reasonFilter, setReasonFilter] = useState<string>('');

  // Data hooks
  const { data: activityTimeline, isLoading: activityLoading, error: activityError, refetch: refetchActivity } = useActivityTimelineReport({
    projectId: settings.defaultProject,
    daysBack,
    groupBy,
  }, { enabled: activeTab === 0 });

  const { data: catalogUsage, isLoading: catalogLoading, error: catalogError, refetch: refetchCatalog } = useCatalogUsageReport({
    projectId: settings.defaultProject,
    includeZero,
    sortBy: catalogSortBy,
    detailedResources,
  }, { enabled: activeTab === 1 });

  const { data: resourcesUsage, isLoading: resourcesLoading, error: resourcesError, refetch: refetchResources } = useResourcesUsageReport({
    projectId: settings.defaultProject,
    detailedResources: resourcesDetailed,
    sortBy: resourcesSortBy,
    groupBy: resourcesGroupBy,
  }, { enabled: activeTab === 2 });

  const { data: unsyncReport, isLoading: unsyncLoading, error: unsyncError, refetch: refetchUnsync } = useUnsyncReport({
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
      let data: any = null;
      let reportName = '';

      switch (activeTab) {
        case 0:
          data = activityTimeline;
          reportName = 'activity-timeline';
          break;
        case 1:
          data = catalogUsage;
          reportName = 'catalog-usage';
          break;
        case 2:
          data = resourcesUsage;
          reportName = 'resources-usage';
          break;
        case 3:
          data = unsyncReport;
          reportName = 'unsync-report';
          break;
      }

      if (!data) {
        setSnackbarMessage('No data available for export');
        setSnackbarOpen(true);
        handleExportClose();
        return;
      }

      // Export based on format
      if (format === 'json') {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${reportName}-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
      } else if (format === 'csv') {
        // Simple CSV export - would need more sophisticated handling for nested data
        setSnackbarMessage('CSV export coming soon');
        setSnackbarOpen(true);
        handleExportClose();
        return;
      } else if (format === 'pdf') {
        setSnackbarMessage('PDF export coming soon');
        setSnackbarOpen(true);
        handleExportClose();
        return;
      }

      setSnackbarMessage(`Report exported successfully as ${format.toUpperCase()}`);
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Export failed:', error);
      setSnackbarMessage('Failed to export report. Please try again.');
      setSnackbarOpen(true);
    }
    handleExportClose();
  };

  const handleRefresh = () => {
    switch (activeTab) {
      case 0:
        refetchActivity();
        break;
      case 1:
        refetchCatalog();
        break;
      case 2:
        refetchResources();
        break;
      case 3:
        refetchUnsync();
        break;
    }
  };

  const toggleRowExpansion = (itemId: string) => {
    setExpandedRows((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
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

  const currentError = [activityError, catalogError, resourcesError, unsyncError][activeTab];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AnalyticsIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            Reports & Analytics
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            size="small"
            onClick={handleRefresh}
          >
            Refresh
          </Button>
          
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

      {/* Error Alert */}
      {currentError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="body2">
            Failed to load report data: {currentError.message}
          </Typography>
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab icon={<TimelineIcon />} label="Activity Timeline" />
          <Tab icon={<AssessmentIcon />} label="Catalog Usage" />
          <Tab icon={<StorageIcon />} label="Resources Usage" />
          <Tab icon={<SyncProblemIcon />} label="Unsync Report" />
        </Tabs>
      </Box>

      {/* Activity Timeline Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardHeader
                title="Activity Timeline Filters"
                action={
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                      <InputLabel>Days Back</InputLabel>
                      <Select
                        value={daysBack}
                        label="Days Back"
                        onChange={(e) => setDaysBack(Number(e.target.value))}
                      >
                        <MenuItem value={7}>7 days</MenuItem>
                        <MenuItem value={30}>30 days</MenuItem>
                        <MenuItem value={60}>60 days</MenuItem>
                        <MenuItem value={90}>90 days</MenuItem>
                        <MenuItem value={180}>180 days</MenuItem>
                        <MenuItem value={365}>1 year</MenuItem>
                      </Select>
                    </FormControl>
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                      <InputLabel>Group By</InputLabel>
                      <Select
                        value={groupBy}
                        label="Group By"
                        onChange={(e) => setGroupBy(e.target.value as typeof groupBy)}
                      >
                        <MenuItem value="day">Day</MenuItem>
                        <MenuItem value="week">Week</MenuItem>
                        <MenuItem value="month">Month</MenuItem>
                        <MenuItem value="year">Year</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>
                }
              />
              <CardContent>
                {activityLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : activityTimeline ? (
                  <>
                    {/* Summary Stats */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4">{activityTimeline.summary.total_deployments}</Typography>
                          <Typography variant="body2" color="text.secondary">Total Deployments</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4" color="success.main">
                            {activityTimeline.summary.successful_deployments}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">Successful</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4" color="error.main">
                            {activityTimeline.summary.failed_deployments}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">Failed</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4" color="warning.main">
                            {activityTimeline.summary.in_progress_deployments}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">In Progress</Typography>
                        </Paper>
                      </Grid>
                    </Grid>

                    {/* Activity Table */}
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Period</TableCell>
                            <TableCell align="right">Total</TableCell>
                            <TableCell align="right">Success</TableCell>
                            <TableCell align="right">Failed</TableCell>
                            <TableCell align="right">In Progress</TableCell>
                            <TableCell align="right">Unique Items</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {Object.entries(activityTimeline.period_activity).map(([period, data]) => (
                            <TableRow key={period}>
                              <TableCell>{period}</TableCell>
                              <TableCell align="right">{data.total_deployments}</TableCell>
                              <TableCell align="right">
                                <Chip label={data.successful_deployments} color="success" size="small" />
                              </TableCell>
                              <TableCell align="right">
                                <Chip label={data.failed_deployments} color="error" size="small" />
                              </TableCell>
                              <TableCell align="right">
                                <Chip label={data.in_progress_deployments} color="warning" size="small" />
                              </TableCell>
                              <TableCell align="right">{data.unique_catalog_items}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                ) : (
                  <Typography>No data available</Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Catalog Usage Tab */}
      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardHeader
                title="Catalog Usage Filters"
                action={
                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={includeZero}
                          onChange={(e) => setIncludeZero(e.target.checked)}
                        />
                      }
                      label="Include Zero"
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={detailedResources}
                          onChange={(e) => setDetailedResources(e.target.checked)}
                        />
                      }
                      label="Detailed"
                    />
                    <FormControl size="small" sx={{ minWidth: 150 }}>
                      <InputLabel>Sort By</InputLabel>
                      <Select
                        value={catalogSortBy}
                        label="Sort By"
                        onChange={(e) => setCatalogSortBy(e.target.value as typeof catalogSortBy)}
                      >
                        <MenuItem value="deployments">Deployments</MenuItem>
                        <MenuItem value="resources">Resources</MenuItem>
                        <MenuItem value="name">Name</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>
                }
              />
              <CardContent>
                {catalogLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : catalogUsage ? (
                  <>
                    {/* Summary */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                      <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 2 }}>
                          <Typography variant="body2" color="text.secondary">Total Items</Typography>
                          <Typography variant="h5">{catalogUsage.summary.total_catalog_items}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {catalogUsage.summary.active_items} active
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 2 }}>
                          <Typography variant="body2" color="text.secondary">Total Deployments</Typography>
                          <Typography variant="h5">{catalogUsage.summary.total_deployments_system_wide}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {catalogUsage.summary.catalog_linked_deployments} linked
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 2 }}>
                          <Typography variant="body2" color="text.secondary">Total Resources</Typography>
                          <Typography variant="h5">{catalogUsage.summary.total_resources}</Typography>
                        </Paper>
                      </Grid>
                    </Grid>

                    {/* Usage Table */}
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            {detailedResources && <TableCell />}
                            <TableCell>Catalog Item</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell align="right">Deployments</TableCell>
                            <TableCell align="right">Resources</TableCell>
                            <TableCell align="right">Success</TableCell>
                            <TableCell align="right">Failed</TableCell>
                            <TableCell align="right">Success Rate</TableCell>
                            <TableCell align="center">Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {catalogUsage.usage_stats.map((item) => (
                            <React.Fragment key={item.id}>
                              <TableRow hover>
                                {detailedResources && (
                                  <TableCell>
                                    <IconButton
                                      size="small"
                                      onClick={() => toggleRowExpansion(item.id)}
                                    >
                                      {expandedRows.has(item.id) ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                                    </IconButton>
                                  </TableCell>
                                )}
                                <TableCell>{item.name}</TableCell>
                                <TableCell>
                                  <Chip label={item.type.replace('com.vmw.', '')} size="small" />
                                </TableCell>
                                <TableCell align="right">{item.deployment_count}</TableCell>
                                <TableCell align="right">{item.resource_count}</TableCell>
                                <TableCell align="right">
                                  <Chip label={item.success_count} color="success" size="small" />
                                </TableCell>
                                <TableCell align="right">
                                  <Chip label={item.failed_count} color="error" size="small" />
                                </TableCell>
                                <TableCell align="right">{item.success_rate.toFixed(1)}%</TableCell>
                                <TableCell align="center">
                                  <Button
                                    size="small"
                                    startIcon={<VisibilityIcon />}
                                    onClick={() => navigate(`/catalog/${item.id}`)}
                                    variant="outlined"
                                  >
                                    View
                                  </Button>
                                </TableCell>
                              </TableRow>
                              {detailedResources && (
                                <TableRow>
                                  <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={9}>
                                    <Collapse in={expandedRows.has(item.id)} timeout="auto" unmountOnExit>
                                      <Box sx={{ margin: 2 }}>
                                        <Typography variant="h6" gutterBottom component="div">
                                          Status Breakdown
                                        </Typography>
                                        <Table size="small">
                                          <TableHead>
                                            <TableRow>
                                              <TableCell>Status</TableCell>
                                              <TableCell align="right">Count</TableCell>
                                            </TableRow>
                                          </TableHead>
                                          <TableBody>
                                            {Object.entries(item.status_breakdown || {}).map(([status, count]) => (
                                              <TableRow key={status}>
                                                <TableCell>
                                                  <Chip
                                                    label={status}
                                                    size="small"
                                                    color={
                                                      status.includes('SUCCESS') ? 'success' :
                                                      status.includes('FAILED') ? 'error' :
                                                      status.includes('INPROGRESS') ? 'warning' : 'default'
                                                    }
                                                  />
                                                </TableCell>
                                                <TableCell align="right">{count}</TableCell>
                                              </TableRow>
                                            ))}
                                          </TableBody>
                                        </Table>
                                        <Box sx={{ mt: 2 }}>
                                          <Typography variant="body2" color="text.secondary">
                                            <strong>Total Deployments:</strong> {item.deployment_count}
                                          </Typography>
                                          <Typography variant="body2" color="text.secondary">
                                            <strong>In Progress:</strong> {item.in_progress_count}
                                          </Typography>
                                        </Box>
                                      </Box>
                                    </Collapse>
                                  </TableCell>
                                </TableRow>
                              )}
                            </React.Fragment>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                ) : (
                  <Typography>No data available</Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Resources Usage Tab */}
      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardHeader
                title="Resources Usage Filters"
                action={
                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={resourcesDetailed}
                          onChange={(e) => setResourcesDetailed(e.target.checked)}
                        />
                      }
                      label="Detailed"
                    />
                    <FormControl size="small" sx={{ minWidth: 150 }}>
                      <InputLabel>Sort By</InputLabel>
                      <Select
                        value={resourcesSortBy}
                        label="Sort By"
                        onChange={(e) => setResourcesSortBy(e.target.value as typeof resourcesSortBy)}
                      >
                        <MenuItem value="deployment-name">Deployment</MenuItem>
                        <MenuItem value="catalog-item">Catalog Item</MenuItem>
                        <MenuItem value="resource-count">Resources</MenuItem>
                        <MenuItem value="status">Status</MenuItem>
                      </Select>
                    </FormControl>
                    <FormControl size="small" sx={{ minWidth: 150 }}>
                      <InputLabel>Group By</InputLabel>
                      <Select
                        value={resourcesGroupBy}
                        label="Group By"
                        onChange={(e) => setResourcesGroupBy(e.target.value as typeof resourcesGroupBy)}
                      >
                        <MenuItem value="catalog-item">Catalog Item</MenuItem>
                        <MenuItem value="resource-type">Resource Type</MenuItem>
                        <MenuItem value="deployment-status">Status</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>
                }
              />
              <CardContent>
                {resourcesLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : resourcesUsage ? (
                  <>
                    {/* Summary */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4">{resourcesUsage.summary.total_deployments}</Typography>
                          <Typography variant="body2" color="text.secondary">Total Deployments</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4">{resourcesUsage.summary.total_resources}</Typography>
                          <Typography variant="body2" color="text.secondary">Total Resources</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4">{resourcesUsage.summary.unique_resource_types}</Typography>
                          <Typography variant="body2" color="text.secondary">Resource Types</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4">{resourcesUsage.summary.unique_catalog_items}</Typography>
                          <Typography variant="body2" color="text.secondary">Catalog Items</Typography>
                        </Paper>
                      </Grid>
                    </Grid>

                    {/* Resource Types */}
                    {resourcesUsage.summary.resource_types && (
                      <Card sx={{ mb: 3 }}>
                        <CardHeader title="Resource Types" />
                        <CardContent>
                          <Grid container spacing={2}>
                            {Object.entries(resourcesUsage.summary.resource_types)
                              .sort(([, a], [, b]) => b - a)
                              .slice(0, 6)
                              .map(([type, count]) => (
                                <Grid item xs={6} sm={4} md={2} key={type}>
                                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                                    <Typography variant="h6">{count}</Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      {type}
                                    </Typography>
                                  </Paper>
                                </Grid>
                              ))}
                          </Grid>
                        </CardContent>
                      </Card>
                    )}
                  </>
                ) : (
                  <Typography>No data available</Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Unsync Report Tab */}
      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardHeader
                title="Unsync Report Filters"
                action={
                  <FormControl size="small" sx={{ minWidth: 200 }}>
                    <InputLabel>Reason Filter</InputLabel>
                    <Select
                      value={reasonFilter}
                      label="Reason Filter"
                      onChange={(e) => setReasonFilter(e.target.value)}
                    >
                      <MenuItem value="">All Reasons</MenuItem>
                      <MenuItem value="missing_catalog_references">Missing References</MenuItem>
                      <MenuItem value="catalog_item_deleted">Item Deleted</MenuItem>
                      <MenuItem value="catalog_name_mismatch">Name Mismatch</MenuItem>
                      <MenuItem value="external_creation">External Creation</MenuItem>
                    </Select>
                  </FormControl>
                }
              />
              <CardContent>
                {unsyncLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : unsyncReport ? (
                  <>
                    {/* Summary */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4">{unsyncReport.summary.total_deployments}</Typography>
                          <Typography variant="body2" color="text.secondary">Total Deployments</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4" color="error.main">
                            {unsyncReport.summary.unsynced_deployments}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">Unsynced</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4">{unsyncReport.summary.unsynced_percentage.toFixed(1)}%</Typography>
                          <Typography variant="body2" color="text.secondary">Unsync Rate</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4">{unsyncReport.summary.total_unsynced_resources}</Typography>
                          <Typography variant="body2" color="text.secondary">Unsynced Resources</Typography>
                        </Paper>
                      </Grid>
                    </Grid>

                    {/* Reason Breakdown */}
                    {unsyncReport.reason_groups && Object.keys(unsyncReport.reason_groups).length > 0 && (
                      <Card sx={{ mb: 3 }}>
                        <CardHeader title="Reasons" />
                        <CardContent>
                          <Grid container spacing={2}>
                            {Object.entries(unsyncReport.reason_groups)
                              .sort(([, a], [, b]) => b - a)
                              .map(([reason, count]) => (
                                <Grid item xs={12} sm={6} md={4} key={reason}>
                                  <Paper sx={{ p: 2 }}>
                                    <Typography variant="h6">{count}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                      {reason.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                    </Typography>
                                  </Paper>
                                </Grid>
                              ))}
                          </Grid>
                        </CardContent>
                      </Card>
                    )}

                    {/* Unsynced Deployments Table */}
                    {unsyncReport.unsynced_deployments.length > 0 && (
                      <TableContainer>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Deployment</TableCell>
                              <TableCell>Status</TableCell>
                              <TableCell align="right">Resources</TableCell>
                              <TableCell>Reason</TableCell>
                              <TableCell align="center">Actions</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {unsyncReport.unsynced_deployments.slice(0, 20).map((item, index) => (
                              <TableRow key={item.deployment.id || index} hover>
                                <TableCell>{item.deployment.name || 'Unknown'}</TableCell>
                                <TableCell>
                                  <Chip 
                                    label={item.deployment.status || 'Unknown'} 
                                    size="small"
                                    color={
                                      item.deployment.status?.includes('SUCCESS') ? 'success' :
                                      item.deployment.status?.includes('FAILED') ? 'error' : 'default'
                                    }
                                  />
                                </TableCell>
                                <TableCell align="right">{item.resource_count}</TableCell>
                                <TableCell>
                                  {item.analysis.primary_reason.replace(/_/g, ' ')}
                                </TableCell>
                                <TableCell align="center">
                                  {item.deployment.id && (
                                    <Button
                                      size="small"
                                      startIcon={<OpenInNewIcon />}
                                      onClick={() => navigate(`/deployments/${item.deployment.id}`)}
                                      variant="outlined"
                                    >
                                      Details
                                    </Button>
                                  )}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </>
                ) : (
                  <Typography>No data available</Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
};

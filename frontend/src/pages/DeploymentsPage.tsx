import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Menu,
  ListItemIcon,
  ListItemText,
  Alert,
  LinearProgress,
  Tooltip,
  MenuItem as MenuOption,
  Snackbar,
} from '@mui/material';
import {
  Inventory as InventoryIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  MoreVert as MoreVertIcon,
  CloudQueue as DeployIcon,
  Delete as DeleteIcon,
  Stop as StopIcon,
  PlayArrow as StartIcon,
  Visibility as ViewIcon,
  Warning as WarningIcon,
  Download as DownloadIcon,
  FileDownload as FileDownloadIcon,
  GetApp as GetAppIcon,
  PictureAsPdf as PictureAsPdfIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { deploymentsService } from '@/services/deployments';
import { useSettingsStore } from '@/store/settingsStore';
import { exportDeploymentData } from '../utils/exportUtils';
import { useProjects } from '../hooks/useProjects';

interface Deployment {
  id: string;
  name: string;
  status: string;
  projectId: string;
  catalogItemId?: string;
  createdAt: string;
  completedAt?: string;
  inputs?: Record<string, any>;
}

const getStatusColor = (status: string) => {
  const statusMap: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
    'CREATE_SUCCESSFUL': 'success',
    'CREATE_IN_PROGRESS': 'info',
    'CREATE_FAILED': 'error',
    'DELETE_IN_PROGRESS': 'warning',
    'DELETE_FAILED': 'error',
    'RUNNING': 'success',
    'STOPPED': 'default',
  };
  return statusMap[status] || 'default';
};

const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    'CREATE_SUCCESSFUL': 'Running',
    'CREATE_IN_PROGRESS': 'Creating',
    'CREATE_FAILED': 'Failed',
    'DELETE_IN_PROGRESS': 'Deleting',
    'DELETE_FAILED': 'Delete Failed',
    'RUNNING': 'Running',
    'STOPPED': 'Stopped',
  };
  return labelMap[status] || status;
};

export const DeploymentsPage: React.FC = () => {
  const { settings, addNotification } = useSettingsStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [projectFilter, setProjectFilter] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedDeployment, setSelectedDeployment] = useState<string | null>(null);
  const [exportAnchorEl, setExportAnchorEl] = useState<null | HTMLElement>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // Get projects for filtering
  const { data: projects } = useProjects();

  const {
    data: deploymentsResponse,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['deployments', settings.defaultProject, searchQuery, statusFilter],
    queryFn: () => deploymentsService.listDeployments({
      project_id: settings.defaultProject,
      page_size: settings.pageSize,
      // Note: searchQuery filtering will be handled client-side
      status: statusFilter || undefined,
    }),
    refetchInterval: settings.autoRefresh ? settings.refreshInterval : false,
  });

  const deployments = deploymentsResponse?.deployments || [];

  const handleActionClick = (event: React.MouseEvent<HTMLElement>, deploymentId: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedDeployment(deploymentId);
  };

  const handleActionClose = () => {
    setAnchorEl(null);
    setSelectedDeployment(null);
  };

  const handleDeploymentAction = async (action: string) => {
    if (!selectedDeployment) return;
    
    try {
      switch (action) {
        case 'delete':
          await deploymentsService.deleteDeployment(selectedDeployment);
          addNotification({
            type: 'success',
            title: 'Deployment Deleted',
            message: 'Deployment deletion initiated successfully.',
          });
          break;
        case 'stop':
          // Implement stop logic
          addNotification({
            type: 'info',
            title: 'Stop Requested',
            message: 'Stop operation initiated.',
          });
          break;
        case 'start':
          // Implement start logic
          addNotification({
            type: 'info',
            title: 'Start Requested',
            message: 'Start operation initiated.',
          });
          break;
        default:
          break;
      }
      refetch();
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Action Failed',
        message: `Failed to ${action} deployment: ${error}`,
      });
    }
    
    handleActionClose();
  };

  const handleExportClick = (event: React.MouseEvent<HTMLElement>) => {
    setExportAnchorEl(event.currentTarget);
  };

  const handleExportClose = () => {
    setExportAnchorEl(null);
  };

  const handleExport = (format: 'csv' | 'json' | 'pdf') => {
    try {
      exportDeploymentData(filteredDeployments, format);
      setSnackbarMessage(`Deployments exported successfully as ${format.toUpperCase()}`);
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Export failed:', error);
      setSnackbarMessage('Failed to export deployments. Please try again.');
      setSnackbarOpen(true);
    }
    handleExportClose();
  };

  const filteredDeployments = deployments.filter((deployment: Deployment) => {
    const matchesSearch = !searchQuery || 
      deployment.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      deployment.id.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesProject = !projectFilter || deployment.projectId === projectFilter;
    
    return matchesSearch && matchesProject;
  });

  if (isError) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Failed to Load Deployments
          </Typography>
          <Typography variant="body2">
            {error instanceof Error ? error.message : 'An unexpected error occurred'}
          </Typography>
          <Button onClick={() => refetch()} sx={{ mt: 1 }}>
            Retry
          </Button>
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <InventoryIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            My Deployments
          </Typography>
          {deployments.length > 0 && (
            <Chip 
              label={`${filteredDeployments.length} of ${deployments.length}`} 
              size="small" 
              color="primary" 
              variant="outlined"
            />
          )}
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Export deployments">
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              size="small"
              onClick={handleExportClick}
              disabled={filteredDeployments.length === 0}
            >
              Export
            </Button>
          </Tooltip>
          
          <Tooltip title="Refresh deployments">
            <IconButton onClick={() => refetch()} disabled={isLoading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* No Default Project Warning */}
      {!settings.defaultProject && (
        <Alert severity="warning" sx={{ mb: 3 }} icon={<WarningIcon />}>
          <Typography variant="body2">
            No default project configured. Please set a default project in{' '}
            <Button size="small" onClick={() => window.location.href = '/settings'}>
              Settings
            </Button>
            {' '}to view your deployments.
          </Typography>
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search deployments"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                placeholder="Search by name or ID..."
              />
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status Filter</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status Filter"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="CREATE_SUCCESSFUL">Running</MenuItem>
                  <MenuItem value="CREATE_IN_PROGRESS">Creating</MenuItem>
                  <MenuItem value="CREATE_FAILED">Failed</MenuItem>
                  <MenuItem value="DELETE_IN_PROGRESS">Deleting</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Project Filter</InputLabel>
                <Select
                  value={projectFilter}
                  label="Project Filter"
                  onChange={(e) => setProjectFilter(e.target.value)}
                >
                  <MenuItem value="">All Projects</MenuItem>
                  {projects?.map((project) => (
                    <MenuItem key={project.id} value={project.id}>
                      {project.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Loading */}
      {isLoading && <LinearProgress sx={{ mb: 3 }} />}

      {/* Deployments List */}
      {filteredDeployments.length === 0 && !isLoading ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <InventoryIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {deployments.length === 0 ? 'No Deployments Found' : 'No Matching Deployments'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {deployments.length === 0 
                ? 'Start by deploying a catalog item to see your deployments here.'
                : 'Try adjusting your search or filter criteria.'}
            </Typography>
            {deployments.length === 0 && (
              <Button 
                variant="contained" 
                sx={{ mt: 2 }}
                onClick={() => window.location.href = '/catalog'}
              >
                Browse Catalog
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {filteredDeployments.map((deployment: Deployment) => (
            <Grid item xs={12} md={6} lg={4} key={deployment.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="h3" noWrap sx={{ flexGrow: 1, mr: 1 }}>
                      {deployment.name}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Chip 
                        label={getStatusLabel(deployment.status)}
                        color={getStatusColor(deployment.status)}
                        size="small"
                      />
                      <IconButton 
                        size="small"
                        onClick={(e) => handleActionClick(e, deployment.id)}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    ID: {deployment.id}
                  </Typography>
                  
                  {deployment.inputs?.owner && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Owner: {deployment.inputs.owner}
                    </Typography>
                  )}
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Created: {new Date(deployment.createdAt).toLocaleDateString()}
                  </Typography>
                  
                  {deployment.completedAt && deployment.completedAt !== deployment.createdAt && (
                    <Typography variant="body2" color="text.secondary">
                      Completed: {new Date(deployment.completedAt).toLocaleDateString()}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleActionClose}
      >
        <MenuItem onClick={() => handleDeploymentAction('view')}>
          <ListItemIcon>
            <ViewIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={() => handleDeploymentAction('stop')}>
          <ListItemIcon>
            <StopIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Stop</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={() => handleDeploymentAction('start')}>
          <ListItemIcon>
            <StartIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Start</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={() => handleDeploymentAction('delete')} sx={{ color: 'error.main' }}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>
      
      {/* Export Menu */}
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
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
};

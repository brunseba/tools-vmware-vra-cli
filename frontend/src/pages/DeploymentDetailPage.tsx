import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  IconButton,
  Tooltip,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ArrowBack,
  Refresh,
  Delete,
  Info,
  ExpandMore,
  CloudQueue,
  Person,
  AccessTime,
  Description,
  Settings,
  Storage,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { deploymentsService } from '@/services/deployments';

const getStatusColor = (status: string): 'success' | 'warning' | 'error' | 'info' | 'default' => {
  const statusMap: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
    'CREATE_SUCCESSFUL': 'success',
    'UPDATE_SUCCESSFUL': 'success',
    'CREATE_IN_PROGRESS': 'info',
    'UPDATE_IN_PROGRESS': 'info',
    'CREATE_FAILED': 'error',
    'UPDATE_FAILED': 'error',
    'DELETE_IN_PROGRESS': 'warning',
    'DELETE_FAILED': 'error',
  };
  return statusMap[status] || 'default';
};

const getResourceStateColor = (state: string): 'success' | 'warning' | 'error' | 'info' | 'default' => {
  const stateMap: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
    'SUCCESSFUL': 'success',
    'IN_PROGRESS': 'info',
    'FAILED': 'error',
    'TAINTED': 'warning',
    'DEPLOYED': 'success',
  };
  return stateMap[state] || 'default';
};

const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString);
    return date.toLocaleString();
  } catch {
    return dateString;
  }
};

export const DeploymentDetailPage: React.FC = () => {
  const { deploymentId } = useParams<{ deploymentId: string }>();
  const navigate = useNavigate();

  const {
    data: deploymentData,
    isLoading: isLoadingDeployment,
    error: deploymentError,
    refetch: refetchDeployment,
  } = useQuery({
    queryKey: ['deployment', deploymentId],
    queryFn: () => deploymentsService.getDeployment(deploymentId!),
    enabled: !!deploymentId,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const {
    data: resourcesData,
    isLoading: isLoadingResources,
    refetch: refetchResources,
  } = useQuery({
    queryKey: ['deployment', 'resources', deploymentId],
    queryFn: () => deploymentsService.getDeploymentResources(deploymentId!),
    enabled: !!deploymentId,
    refetchInterval: 30000,
  });

  const deployment = deploymentData?.deployment;
  const resources = resourcesData?.resources || [];

  const handleRefresh = () => {
    refetchDeployment();
    refetchResources();
  };

  if (isLoadingDeployment) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (deploymentError || !deployment) {
    return (
      <Box sx={{ p: 3 }}>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/deployments')} sx={{ mb: 2 }}>
          Back to Deployments
        </Button>
        <Alert severity="error">
          <Typography variant="h6">Deployment Not Found</Typography>
          <Typography>The deployment could not be loaded. It may have been deleted.</Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton onClick={() => navigate('/deployments')}>
            <ArrowBack />
          </IconButton>
          <CloudQueue sx={{ fontSize: 32, color: 'primary.main' }} />
          <Box>
            <Typography variant="h4" component="h1">
              {deployment.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Deployment ID: {deployment.id}
            </Typography>
          </Box>
          <Chip
            label={deployment.status.replace(/_/g, ' ')}
            color={getStatusColor(deployment.status)}
            size="medium"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            color="error"
            startIcon={<Delete />}
            onClick={() => {
              if (window.confirm('Are you sure you want to delete this deployment?')) {
                deploymentsService.deleteDeployment(deploymentId!, true);
                navigate('/deployments');
              }
            }}
          >
            Delete
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Overview Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Info /> Overview
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold', width: '40%' }}>
                      <Person sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
                      Owner
                    </TableCell>
                    <TableCell>{deployment.ownedBy || deployment.createdBy}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>
                      <AccessTime sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
                      Created
                    </TableCell>
                    <TableCell>{formatDate(deployment.createdAt)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>
                      <AccessTime sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
                      Last Updated
                    </TableCell>
                    <TableCell>{formatDate(deployment.lastUpdatedAt)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Project ID</TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                        {deployment.projectId}
                      </Typography>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Organization ID</TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                        {deployment.orgId}
                      </Typography>
                    </TableCell>
                  </TableRow>
                  {deployment.catalogItemId && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Catalog Item</TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                          {deployment.catalogItemId}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                  {deployment.blueprintId && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Blueprint</TableCell>
                      <TableCell>{deployment.blueprintId}</TableCell>
                    </TableRow>
                  )}
                  {deployment.leaseGracePeriodDays && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Lease Grace Period</TableCell>
                      <TableCell>{deployment.leaseGracePeriodDays} days</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>

        {/* Deployment Inputs */}
        {deployment.inputs && Object.keys(deployment.inputs).length > 0 && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Settings /> Deployment Inputs
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <Table size="small">
                  <TableBody>
                    {Object.entries(deployment.inputs).map(([key, value]) => (
                      <TableRow key={key}>
                        <TableCell sx={{ fontWeight: 'bold', width: '40%' }}>
                          {key.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim()}
                        </TableCell>
                        <TableCell>
                          {typeof value === 'object' ? (
                            <pre style={{ margin: 0, fontSize: '0.85rem' }}>
                              {JSON.stringify(value, null, 2)}
                            </pre>
                          ) : value === null ? (
                            <Typography variant="body2" color="text.secondary" fontStyle="italic">
                              null
                            </Typography>
                          ) : (
                            String(value)
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Resources */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Storage /> Resources ({resources.length})
                </Typography>
                {isLoadingResources && <CircularProgress size={20} />}
              </Box>
              <Divider sx={{ mb: 2 }} />

              {resources.length === 0 ? (
                <Alert severity="info">No resources found for this deployment</Alert>
              ) : (
                <Box>
                  {resources.map((resource: any, index: number) => (
                    <Accordion key={resource.id || index}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                          <Typography sx={{ fontWeight: 'bold' }}>{resource.name}</Typography>
                          <Chip label={resource.type} size="small" variant="outlined" />
                          {resource.state && (
                            <Chip
                              label={resource.state}
                              size="small"
                              color={getResourceStateColor(resource.state)}
                            />
                          )}
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Table size="small">
                          <TableBody>
                            <TableRow>
                              <TableCell sx={{ fontWeight: 'bold', width: '30%' }}>Resource ID</TableCell>
                              <TableCell>
                                <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                                  {resource.id}
                                </Typography>
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell sx={{ fontWeight: 'bold' }}>Type</TableCell>
                              <TableCell>{resource.type}</TableCell>
                            </TableRow>
                            {resource.state && (
                              <TableRow>
                                <TableCell sx={{ fontWeight: 'bold' }}>State</TableCell>
                                <TableCell>
                                  <Chip
                                    label={resource.state}
                                    size="small"
                                    color={getResourceStateColor(resource.state)}
                                  />
                                </TableCell>
                              </TableRow>
                            )}
                            {resource.origin && (
                              <TableRow>
                                <TableCell sx={{ fontWeight: 'bold' }}>Origin</TableCell>
                                <TableCell>{resource.origin}</TableCell>
                              </TableRow>
                            )}
                            {resource.createdAt && (
                              <TableRow>
                                <TableCell sx={{ fontWeight: 'bold' }}>Created At</TableCell>
                                <TableCell>{formatDate(resource.createdAt)}</TableCell>
                              </TableRow>
                            )}
                            {resource.properties && Object.keys(resource.properties).length > 0 && (
                              <TableRow>
                                <TableCell sx={{ fontWeight: 'bold', verticalAlign: 'top' }}>Properties</TableCell>
                                <TableCell>
                                  <pre style={{ margin: 0, fontSize: '0.85rem', overflow: 'auto' }}>
                                    {JSON.stringify(resource.properties, null, 2)}
                                  </pre>
                                </TableCell>
                              </TableRow>
                            )}
                          </TableBody>
                        </Table>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

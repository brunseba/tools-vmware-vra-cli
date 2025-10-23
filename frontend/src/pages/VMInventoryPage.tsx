import React, { useState, useMemo, useEffect } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  TextField,
  InputAdornment,
  Alert,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Divider,
  Grid,
} from '@mui/material'
import {
  Computer,
  Search,
  Refresh,
  OpenInNew,
  Info,
} from '@mui/icons-material'
import { useDeployments } from '@/hooks/useDeployments'
import { useSettingsStore } from '@/store/settingsStore'
import { useNavigate } from 'react-router-dom'
import { deploymentsService } from '@/services/deployments'
import { DeploymentResource } from '@/types/api'

interface VMResource {
  id: string
  name: string
  deploymentId: string
  deploymentName: string
  status: string
  type: string
  properties?: Record<string, any>
}

export const VMInventoryPage: React.FC = () => {
  const navigate = useNavigate()
  const { settings } = useSettingsStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [vmResources, setVmResources] = useState<VMResource[]>([])
  const [isLoadingResources, setIsLoadingResources] = useState(false)
  const [selectedVM, setSelectedVM] = useState<VMResource | null>(null)
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)

  // Fetch all deployments
  const { data: deploymentsData, isLoading: isLoadingDeployments, refetch, isRefetching } = useDeployments({
    projectId: settings.defaultProject,
    pageSize: 1000,
  })

  // Fetch resources for all deployments and filter for vSphere machines
  useEffect(() => {
    const fetchAllVMResources = async () => {
      if (!deploymentsData?.deployments || deploymentsData.deployments.length === 0) {
        setVmResources([])
        return
      }

      setIsLoadingResources(true)
      const vms: VMResource[] = []

      try {
        // Fetch resources for each deployment in parallel
        const resourcePromises = deploymentsData.deployments.map(async (deployment) => {
          try {
            const resourcesResponse = await deploymentsService.getDeploymentResources(
              deployment.id,
              false
            )
            
            // Filter for Cloud.vSphere.Machine resources
            if (resourcesResponse.resources) {
              resourcesResponse.resources.forEach((resource: DeploymentResource) => {
                if (resource.type === 'Cloud.vSphere.Machine') {
                  vms.push({
                    id: resource.id,
                    name: resource.name,
                    deploymentId: deployment.id,
                    deploymentName: deployment.name,
                    status: resource.status || deployment.status,
                    type: resource.type,
                    properties: resource.properties,
                  })
                }
              })
            }
          } catch (error) {
            console.error(`Failed to fetch resources for deployment ${deployment.id}:`, error)
          }
        })

        await Promise.all(resourcePromises)
        setVmResources(vms)
      } catch (error) {
        console.error('Error fetching VM resources:', error)
      } finally {
        setIsLoadingResources(false)
      }
    }

    fetchAllVMResources()
  }, [deploymentsData])

  const isLoading = isLoadingDeployments || isLoadingResources

  // Filter VMs based on search query
  const filteredVMs = useMemo(() => {
    if (!searchQuery.trim()) return vmResources

    const query = searchQuery.toLowerCase()
    return vmResources.filter(
      (vm) =>
        vm.name.toLowerCase().includes(query) ||
        vm.deploymentName.toLowerCase().includes(query) ||
        vm.id.toLowerCase().includes(query)
    )
  }, [vmResources, searchQuery])

  // Get status color
  const getStatusColor = (status: string): 'success' | 'error' | 'warning' | 'default' => {
    if (status.includes('SUCCESS')) return 'success'
    if (status.includes('FAILED')) return 'error'
    if (status.includes('INPROGRESS')) return 'warning'
    return 'default'
  }

  // Extract common VM properties
  const getVMInfo = (vm: VMResource) => {
    const props = vm.properties || {}
    return {
      cpu: props.cpuCount || props.cpu || 'N/A',
      memory: props.totalMemoryMB || props.memory || 'N/A',
      powerState: props.powerState || 'Unknown',
      ipAddress: props.address || props.ipAddress || 'N/A',
      osType: props.osType || props.guestOS || 'N/A',
    }
  }

  const handleViewDeployment = (deploymentId: string) => {
    navigate(`/deployments/${deploymentId}`)
  }

  const handleViewDetails = (vm: VMResource) => {
    setSelectedVM(vm)
    setDetailsDialogOpen(true)
  }

  const handleCloseDetails = () => {
    setDetailsDialogOpen(false)
    setSelectedVM(null)
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Computer sx={{ mr: 1, fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            VM Inventory
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Tooltip title="Refresh">
            <IconButton onClick={() => refetch()} disabled={isRefetching}>
              {isRefetching ? <CircularProgress size={24} /> : <Refresh />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Info Alert */}
      <Alert severity="info" sx={{ mb: 3 }}>
        Showing all virtual machines of type <strong>Cloud.vSphere.Machine</strong> across all deployments in the current project.
        {vmResources.length > 0 && ` Found ${vmResources.length} VM${vmResources.length !== 1 ? 's' : ''}.`}
      </Alert>

      {/* Search Bar */}
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search by VM name, deployment name, or resource ID..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {/* VMs Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>VM Name</TableCell>
                  <TableCell>Deployment</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>CPU / Memory</TableCell>
                  <TableCell>Power State</TableCell>
                  <TableCell>IP Address</TableCell>
                  <TableCell>OS Type</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : filteredVMs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                      <Typography variant="body2" color="text.secondary">
                        {searchQuery
                          ? 'No VMs found matching your search.'
                          : 'No vSphere machines found in current project.'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredVMs.map((vm) => {
                    const vmInfo = getVMInfo(vm)
                    return (
                      <TableRow key={vm.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Computer fontSize="small" color="primary" />
                            <Typography variant="body2" fontWeight="bold">
                              {vm.name}
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {vm.id}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{vm.deploymentName}</Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={vm.status}
                            size="small"
                            color={getStatusColor(vm.status)}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {vmInfo.cpu} vCPU / {vmInfo.memory} MB
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={vmInfo.powerState}
                            size="small"
                            color={vmInfo.powerState === 'ON' ? 'success' : 'default'}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{vmInfo.ipAddress}</Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{vmInfo.osType}</Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Resource Details">
                            <IconButton
                              size="small"
                              onClick={() => handleViewDetails(vm)}
                            >
                              <Info fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="View Deployment">
                            <IconButton
                              size="small"
                              onClick={() => handleViewDeployment(vm.deploymentId)}
                            >
                              <OpenInNew fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    )
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Resource Details Dialog */}
      <Dialog open={detailsDialogOpen} onClose={handleCloseDetails} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Computer color="primary" />
            VM Resource Details
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedVM && (
            <Box sx={{ mt: 2 }}>
              {/* Basic Information */}
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Resource Name
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {selectedVM.name}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Resource ID
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {selectedVM.id}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Resource Type
                  </Typography>
                  <Typography variant="body2">{selectedVM.type}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Status
                  </Typography>
                  <Box>
                    <Chip
                      label={selectedVM.status}
                      size="small"
                      color={getStatusColor(selectedVM.status)}
                    />
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Deployment
                  </Typography>
                  <Typography variant="body2">{selectedVM.deploymentName}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Deployment ID
                  </Typography>
                  <Typography variant="body2">{selectedVM.deploymentId}</Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              {/* Resource Properties */}
              <Typography variant="h6" gutterBottom>
                Resource Properties
              </Typography>
              {selectedVM.properties && Object.keys(selectedVM.properties).length > 0 ? (
                <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                  <Grid container spacing={2}>
                    {Object.entries(selectedVM.properties)
                      .sort(([keyA], [keyB]) => keyA.localeCompare(keyB))
                      .map(([key, value]) => (
                        <Grid item xs={12} key={key}>
                          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{ minWidth: 200, fontWeight: 500 }}
                            >
                              {key}:
                            </Typography>
                            <Typography
                              variant="body2"
                              sx={{
                                wordBreak: 'break-word',
                                fontFamily: typeof value === 'object' ? 'monospace' : 'inherit',
                              }}
                            >
                              {typeof value === 'object'
                                ? JSON.stringify(value, null, 2)
                                : String(value)}
                            </Typography>
                          </Box>
                        </Grid>
                      ))}
                  </Grid>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No properties available
                </Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              handleCloseDetails()
              handleViewDeployment(selectedVM?.deploymentId || '')
            }}
            startIcon={<OpenInNew />}
            disabled={!selectedVM}
          >
            View Deployment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

import React, { useState, useMemo } from 'react'
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
  LinearProgress,
} from '@mui/material'
import {
  Computer,
  Search,
  Refresh,
  OpenInNew,
  Info,
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
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

// Fetch VM resources using optimized bulk endpoint
const fetchAllVMResources = async (projectId?: string) => {
  try {
    console.log('[VM Inventory] Fetching resources for project:', projectId)
    const response = await deploymentsService.getAllResources(
      projectId,
      'Cloud.vSphere.Machine',
      false
    )
    
    console.log('[VM Inventory] Response:', response)
    
    if (!response.resources || !Array.isArray(response.resources)) {
      console.warn('[VM Inventory] No resources array in response')
      return []
    }
    
    console.log('[VM Inventory] Found', response.resources.length, 'resources')
    
    // Transform to VMResource format
    const vms: VMResource[] = response.resources.map((resource: any) => ({
      id: resource.id,
      name: resource.name,
      deploymentId: resource.deploymentId,
      deploymentName: resource.deploymentName,
      status: resource.status,
      type: resource.type,
      properties: resource.properties,
    }))
    
    console.log('[VM Inventory] Transformed to', vms.length, 'VMs')
    return vms
  } catch (error) {
    console.error('[VM Inventory] Error fetching VM resources:', error)
    return []
  }
}

export const VMInventoryPage: React.FC = () => {
  const navigate = useNavigate()
  const { settings } = useSettingsStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedVM, setSelectedVM] = useState<VMResource | null>(null)
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)

  // Fetch VM resources with React Query caching - using optimized bulk endpoint
  const {
    data: vmResources = [],
    isLoading,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['vm-inventory', settings.defaultProject],
    queryFn: () => fetchAllVMResources(settings.defaultProject),
    staleTime: 2 * 60 * 1000, // Cache for 2 minutes
    gcTime: 5 * 60 * 1000, // Keep in cache for 5 minutes
    retry: 1,
  })

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
  const getStatusColor = (status?: string): 'success' | 'error' | 'warning' | 'default' => {
    if (!status) return 'default'
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
            <span>
              <IconButton onClick={() => refetch()} disabled={isFetching}>
                {isFetching ? <CircularProgress size={24} /> : <Refresh />}
              </IconButton>
            </span>
          </Tooltip>
        </Box>
      </Box>

      {/* Loading Progress */}
      {isFetching && !isLoading && (
        <Box sx={{ width: '100%', mb: 2 }}>
          <LinearProgress />
        </Box>
      )}

      {/* Info Alert */}
      <Alert severity="info" sx={{ mb: 3 }}>
        Showing all virtual machines of type <strong>Cloud.vSphere.Machine</strong> across all deployments in the current project.
        {vmResources.length > 0 && ` Found ${vmResources.length} VM${vmResources.length !== 1 ? 's' : ''}.`}
        {isFetching && ' Updating...'}
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
                    <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : filteredVMs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
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
                      label={selectedVM.status || 'Unknown'}
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

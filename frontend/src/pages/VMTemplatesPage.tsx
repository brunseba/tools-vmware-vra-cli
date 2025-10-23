import React, { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Alert,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemButton,
  Checkbox,
  Badge,
} from '@mui/material'
import {
  Description,
  Add,
  Edit,
  Delete,
  PlayArrow,
  MoreVert,
  ContentCopy,
  Computer,
  AutoAwesome,
  Inventory,
} from '@mui/icons-material'
import { useDeployments } from '@/hooks/useDeployments'
import { useSettingsStore } from '@/store/settingsStore'
import { useRequestCatalogItem, useCatalogItems } from '@/hooks/useCatalog'
import { useNavigate } from 'react-router-dom'

interface VMTemplate {
  id: string
  name: string
  description: string
  catalogItemId: string
  catalogItemName: string
  inputs: Record<string, any>
  createdAt: string
  updatedAt: string
}

export const VMTemplatesPage: React.FC = () => {
  const navigate = useNavigate()
  const { settings } = useSettingsStore()
  const { data: deploymentsData, isLoading: deploymentsLoading } = useDeployments({
    projectId: settings.defaultProject,
    pageSize: 1000,
  })
  const { data: catalogData } = useCatalogItems({
    project_id: settings.defaultProject,
    page_size: 100,
  })
  const requestCatalogMutation = useRequestCatalogItem()

  const [templates, setTemplates] = useState<VMTemplate[]>([
    {
      id: '1',
      name: 'Development VM - Small',
      description: 'Small VM for development environments (2 vCPU, 4GB RAM)',
      catalogItemId: 'vm-create-id',
      catalogItemName: 'Virtual Machine - Create',
      inputs: {
        vmName: 'dev-vm-{timestamp}',
        cpu: 2,
        memory: 4096,
        diskSize: 40,
        osType: 'ubuntu',
        network: 'dev-network',
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: '2',
      name: 'Production VM - Medium',
      description: 'Medium VM for production workloads (4 vCPU, 8GB RAM)',
      catalogItemId: 'vm-create-id',
      catalogItemName: 'Virtual Machine - Create',
      inputs: {
        vmName: 'prod-vm-{timestamp}',
        cpu: 4,
        memory: 8192,
        diskSize: 100,
        osType: 'centos',
        network: 'prod-network',
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: '3',
      name: 'Test VM - Minimal',
      description: 'Minimal VM for testing (1 vCPU, 2GB RAM)',
      catalogItemId: 'vm-create-id',
      catalogItemName: 'Virtual Machine - Create',
      inputs: {
        vmName: 'test-vm-{timestamp}',
        cpu: 1,
        memory: 2048,
        diskSize: 20,
        osType: 'ubuntu',
        network: 'test-network',
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ])

  const [openDialog, setOpenDialog] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<VMTemplate | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    inputs: '{}',
  })
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(null)
  const [selectedTemplateForMenu, setSelectedTemplateForMenu] = useState<VMTemplate | null>(null)
  const [discoverDialogOpen, setDiscoverDialogOpen] = useState(false)
  const [selectedDeployments, setSelectedDeployments] = useState<Set<string>>(new Set())
  const [deployDialogOpen, setDeployDialogOpen] = useState(false)
  const [templateToDeployData, setTemplateToDeployData] = useState<{
    template: VMTemplate | null
    deploymentName: string
    customInputs: string
  }>({
    template: null,
    deploymentName: '',
    customInputs: '{}',
  })

  const handleOpenDialog = (template?: VMTemplate) => {
    if (template) {
      setEditingTemplate(template)
      setFormData({
        name: template.name,
        description: template.description,
        inputs: JSON.stringify(template.inputs, null, 2),
      })
    } else {
      setEditingTemplate(null)
      setFormData({
        name: '',
        description: '',
        inputs: '{}',
      })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setEditingTemplate(null)
    setFormData({ name: '', description: '', inputs: '{}' })
  }

  const handleSaveTemplate = () => {
    try {
      const inputs = JSON.parse(formData.inputs)
      
      if (editingTemplate) {
        // Update existing template
        setTemplates(prev =>
          prev.map(t =>
            t.id === editingTemplate.id
              ? {
                  ...t,
                  name: formData.name,
                  description: formData.description,
                  inputs,
                  updatedAt: new Date().toISOString(),
                }
              : t
          )
        )
      } else {
        // Create new template
        const newTemplate: VMTemplate = {
          id: Date.now().toString(),
          name: formData.name,
          description: formData.description,
          catalogItemId: 'vm-create-id',
          catalogItemName: 'Virtual Machine - Create',
          inputs,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
        setTemplates(prev => [...prev, newTemplate])
      }
      
      handleCloseDialog()
    } catch (error) {
      alert('Invalid JSON format in inputs')
    }
  }

  const handleDeleteTemplate = (id: string) => {
    if (confirm('Are you sure you want to delete this template?')) {
      setTemplates(prev => prev.filter(t => t.id !== id))
    }
    handleCloseActionMenu()
  }

  const handleDuplicateTemplate = (template: VMTemplate) => {
    const newTemplate: VMTemplate = {
      ...template,
      id: Date.now().toString(),
      name: `${template.name} (Copy)`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    setTemplates(prev => [...prev, newTemplate])
    handleCloseActionMenu()
  }

  const handleDeployTemplate = (template: VMTemplate) => {
    // Open deploy dialog with template data
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
    const deploymentName = template.inputs.vmName?.replace('{timestamp}', timestamp) || `vm-${timestamp}`
    
    setTemplateToDeployData({
      template,
      deploymentName,
      customInputs: JSON.stringify(template.inputs, null, 2),
    })
    setDeployDialogOpen(true)
    handleCloseActionMenu()
  }

  const handleCloseDeployDialog = () => {
    setDeployDialogOpen(false)
    setTemplateToDeployData({
      template: null,
      deploymentName: '',
      customInputs: '{}',
    })
  }

  const handleConfirmDeploy = async () => {
    if (!templateToDeployData.template) return

    try {
      const inputs = JSON.parse(templateToDeployData.customInputs)
      
      // Find the catalog item by name or ID
      const catalogItem = catalogData?.items.find(
        item => 
          item.name.includes('Virtual Machine') && 
          (item.name.includes('Create') || item.name.includes('create'))
      )

      if (!catalogItem) {
        alert('Could not find "Virtual Machine - Create" catalog item. Please ensure it exists in your catalog.')
        return
      }

      // Submit the deployment request
      await requestCatalogMutation.mutateAsync({
        itemId: catalogItem.id,
        requestData: {
          name: templateToDeployData.deploymentName,
          projectId: settings.defaultProject,
          inputs,
        },
      })

      handleCloseDeployDialog()
      
      // Navigate to deployments page after successful request
      setTimeout(() => {
        navigate('/deployments')
      }, 2000)
    } catch (error) {
      console.error('Deployment failed:', error)
      alert(`Failed to deploy: ${error instanceof Error ? error.message : 'Invalid JSON format'}`)
    }
  }

  const handleOpenActionMenu = (event: React.MouseEvent<HTMLElement>, template: VMTemplate) => {
    setActionMenuAnchor(event.currentTarget)
    setSelectedTemplateForMenu(template)
  }

  const handleCloseActionMenu = () => {
    setActionMenuAnchor(null)
    setSelectedTemplateForMenu(null)
  }

  const handleOpenDiscoverDialog = () => {
    setDiscoverDialogOpen(true)
    setSelectedDeployments(new Set())
  }

  const handleCloseDiscoverDialog = () => {
    setDiscoverDialogOpen(false)
    setSelectedDeployments(new Set())
  }

  const handleToggleDeploymentSelection = (deploymentId: string) => {
    setSelectedDeployments(prev => {
      const newSet = new Set(prev)
      if (newSet.has(deploymentId)) {
        newSet.delete(deploymentId)
      } else {
        newSet.add(deploymentId)
      }
      return newSet
    })
  }

  const handleGenerateTemplatesFromDeployments = () => {
    const vmDeployments = deploymentsData?.deployments.filter(d => 
      d.catalogItemName?.includes('Virtual Machine') ||
      d.name?.toLowerCase().includes('vm') ||
      d.name?.toLowerCase().includes('virtual')
    ) || []

    const selectedDeps = vmDeployments.filter(d => selectedDeployments.has(d.id))

    selectedDeps.forEach(deployment => {
      // Extract inputs from deployment
      const inputs = deployment.inputs || {}
      
      // Try to extract common VM parameters
      const templateInputs: Record<string, any> = {
        vmName: deployment.name || 'vm-{timestamp}',
      }

      // Extract CPU, memory, disk, network, etc. from deployment inputs
      Object.keys(inputs).forEach(key => {
        const lowerKey = key.toLowerCase()
        if (lowerKey.includes('cpu') || lowerKey.includes('vcpu')) {
          templateInputs.cpu = inputs[key]
        } else if (lowerKey.includes('memory') || lowerKey.includes('ram')) {
          templateInputs.memory = inputs[key]
        } else if (lowerKey.includes('disk') || lowerKey.includes('storage')) {
          templateInputs.diskSize = inputs[key]
        } else if (lowerKey.includes('os') || lowerKey.includes('image')) {
          templateInputs.osType = inputs[key]
        } else if (lowerKey.includes('network')) {
          templateInputs.network = inputs[key]
        } else {
          // Include other inputs as-is
          templateInputs[key] = inputs[key]
        }
      })

      const newTemplate: VMTemplate = {
        id: `discovered-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: `${deployment.name} (Auto-discovered)`,
        description: `Template auto-generated from deployment: ${deployment.name}${deployment.catalogItemName ? ` (${deployment.catalogItemName})` : ''}`,
        catalogItemId: deployment.catalogItemId || 'vm-create-id',
        catalogItemName: deployment.catalogItemName || 'Virtual Machine - Create',
        inputs: templateInputs,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }

      setTemplates(prev => [...prev, newTemplate])
    })

    handleCloseDiscoverDialog()
  }

  // Filter deployments that look like VM deployments
  const vmDeployments = deploymentsData?.deployments.filter(d => 
    d.catalogItemName?.includes('Virtual Machine') ||
    d.name?.toLowerCase().includes('vm') ||
    d.name?.toLowerCase().includes('virtual')
  ) || []

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Description sx={{ mr: 1, fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            VM Templates
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Badge badgeContent={vmDeployments.length} color="primary">
            <Button
              variant="outlined"
              startIcon={deploymentsLoading ? <CircularProgress size={16} /> : <AutoAwesome />}
              onClick={handleOpenDiscoverDialog}
              disabled={deploymentsLoading || vmDeployments.length === 0}
            >
              Discover from Deployments
            </Button>
          </Badge>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenDialog()}
          >
            New Template
          </Button>
        </Box>
      </Box>

      {/* Info Alert */}
      <Alert severity="info" sx={{ mb: 3 }}>
        Templates allow you to save preconfigured deployment parameters for "Virtual Machine - Create" 
        catalog entries. Use templates to standardize VM deployments across your organization.
      </Alert>

      {/* Templates Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Template Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Catalog Item</TableCell>
                  <TableCell>CPU / Memory</TableCell>
                  <TableCell>Updated</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {templates.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                      <Typography variant="body2" color="text.secondary">
                        No templates found. Create your first template to get started.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  templates.map((template) => (
                    <TableRow key={template.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Computer fontSize="small" color="primary" />
                          <Typography variant="body2" fontWeight="bold">
                            {template.name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {template.description}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={template.catalogItemName}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {template.inputs.cpu || 'N/A'} vCPU / {template.inputs.memory ? `${template.inputs.memory / 1024}GB` : 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(template.updatedAt).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          onClick={(e) => handleOpenActionMenu(e, template)}
                        >
                          <MoreVert />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Action Menu */}
      <Menu
        anchorEl={actionMenuAnchor}
        open={Boolean(actionMenuAnchor)}
        onClose={handleCloseActionMenu}
      >
        <MenuItem onClick={() => selectedTemplateForMenu && handleDeployTemplate(selectedTemplateForMenu)}>
          <ListItemIcon>
            <PlayArrow fontSize="small" />
          </ListItemIcon>
          <ListItemText>Deploy</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedTemplateForMenu && handleOpenDialog(selectedTemplateForMenu)}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedTemplateForMenu && handleDuplicateTemplate(selectedTemplateForMenu)}>
          <ListItemIcon>
            <ContentCopy fontSize="small" />
          </ListItemIcon>
          <ListItemText>Duplicate</ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={() => selectedTemplateForMenu && handleDeleteTemplate(selectedTemplateForMenu.id)}
          sx={{ color: 'error.main' }}
        >
          <ListItemIcon>
            <Delete fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Deploy Template Dialog */}
      <Dialog open={deployDialogOpen} onClose={handleCloseDeployDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PlayArrow color="primary" />
            Deploy from Template
          </Box>
        </DialogTitle>
        <DialogContent>
          {templateToDeployData.template && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
              <Alert severity="info">
                Deploying: <strong>{templateToDeployData.template.name}</strong>
                <br />
                Catalog Item: <strong>{templateToDeployData.template.catalogItemName}</strong>
              </Alert>

              <TextField
                label="Deployment Name"
                fullWidth
                required
                value={templateToDeployData.deploymentName}
                onChange={(e) => setTemplateToDeployData(prev => ({ ...prev, deploymentName: e.target.value }))}
                placeholder="e.g., my-vm-001"
                helperText="Unique name for this VM deployment"
              />

              <TextField
                label="Deployment Inputs (JSON)"
                fullWidth
                multiline
                rows={12}
                required
                value={templateToDeployData.customInputs}
                onChange={(e) => setTemplateToDeployData(prev => ({ ...prev, customInputs: e.target.value }))}
                placeholder='{"cpu": 2, "memory": 4096}'
                helperText="Review and customize the deployment parameters as needed"
                sx={{ fontFamily: 'monospace', '& textarea': { fontFamily: 'monospace' } }}
              />

              {requestCatalogMutation.isPending && (
                <Alert severity="info" icon={<CircularProgress size={20} />}>
                  Submitting deployment request...
                </Alert>
              )}

              {requestCatalogMutation.isError && (
                <Alert severity="error">
                  Deployment failed: {requestCatalogMutation.error?.message}
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeployDialog} disabled={requestCatalogMutation.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDeploy}
            variant="contained"
            disabled={!templateToDeployData.deploymentName || !templateToDeployData.customInputs || requestCatalogMutation.isPending}
            startIcon={requestCatalogMutation.isPending ? <CircularProgress size={16} /> : <PlayArrow />}
          >
            {requestCatalogMutation.isPending ? 'Deploying...' : 'Deploy Now'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Discover Templates Dialog */}
      <Dialog open={discoverDialogOpen} onClose={handleCloseDiscoverDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AutoAwesome color="primary" />
            Discover Templates from Deployments
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Select existing VM deployments to automatically generate templates from their configurations.
            {vmDeployments.length > 0 ? 
              ` Found ${vmDeployments.length} VM deployment${vmDeployments.length !== 1 ? 's' : ''}.` :
              ' No VM deployments found.'}
          </Alert>

          {deploymentsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : vmDeployments.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Inventory sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                No Virtual Machine deployments found in the current project.
              </Typography>
            </Box>
          ) : (
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {vmDeployments.map((deployment) => (
                <ListItem key={deployment.id} disablePadding>
                  <ListItemButton
                    dense
                    onClick={() => handleToggleDeploymentSelection(deployment.id)}
                  >
                    <Checkbox
                      edge="start"
                      checked={selectedDeployments.has(deployment.id)}
                      tabIndex={-1}
                      disableRipple
                    />
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Computer fontSize="small" />
                          <Typography variant="body2" fontWeight="bold">
                            {deployment.name}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 0.5 }}>
                          {deployment.catalogItemName && (
                            <Chip
                              label={deployment.catalogItemName}
                              size="small"
                              variant="outlined"
                              sx={{ mr: 1 }}
                            />
                          )}
                          <Chip
                            label={deployment.status || 'Unknown'}
                            size="small"
                            color={deployment.status?.includes('SUCCESS') ? 'success' : 'default'}
                          />
                        </Box>
                      }
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          )}

          {selectedDeployments.size > 0 && (
            <Alert severity="success" sx={{ mt: 2 }}>
              {selectedDeployments.size} deployment{selectedDeployments.size !== 1 ? 's' : ''} selected. 
              Templates will be auto-generated with their input parameters.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDiscoverDialog}>Cancel</Button>
          <Button
            onClick={handleGenerateTemplatesFromDeployments}
            variant="contained"
            disabled={selectedDeployments.size === 0}
            startIcon={<AutoAwesome />}
          >
            Generate {selectedDeployments.size > 0 ? `${selectedDeployments.size} ` : ''}Template{selectedDeployments.size !== 1 ? 's' : ''}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingTemplate ? 'Edit Template' : 'New Template'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Template Name"
              fullWidth
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Development VM - Small"
            />
            
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={2}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe the purpose and configuration of this template"
            />
            
            <TextField
              label="Deployment Inputs (JSON)"
              fullWidth
              multiline
              rows={10}
              required
              value={formData.inputs}
              onChange={(e) => setFormData({ ...formData, inputs: e.target.value })}
              placeholder='{"vmName": "my-vm", "cpu": 2, "memory": 4096}'
              helperText="Enter the deployment parameters as a JSON object. These values will be pre-filled when deploying this template."
              sx={{ fontFamily: 'monospace' }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSaveTemplate}
            variant="contained"
            disabled={!formData.name || !formData.inputs}
          >
            {editingTemplate ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

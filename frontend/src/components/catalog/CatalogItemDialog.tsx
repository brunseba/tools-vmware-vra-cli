import React, { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  Divider,
  Tab,
  Tabs,
  Alert,
  CircularProgress,
  IconButton,
} from '@mui/material'
import {
  Close,
  Launch,
  Info,
  Code,
  CloudQueue,
} from '@mui/icons-material'
import { CatalogItem } from '@/types/api'
import { useCatalogItemSchema } from '@/hooks/useCatalog'
import { SchemaForm } from './SchemaForm'

interface CatalogItemDialogProps {
  item: CatalogItem
  open: boolean
  onClose: () => void
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`catalog-item-tabpanel-${index}`}
    aria-labelledby={`catalog-item-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
  </div>
)

export const CatalogItemDialog: React.FC<CatalogItemDialogProps> = ({
  item,
  open,
  onClose,
}) => {
  const [currentTab, setCurrentTab] = useState(0)
  
  // Fetch schema for deployment form
  const {
    data: schemaResponse,
    isLoading: schemaLoading,
    error: schemaError,
  } = useCatalogItemSchema(item.id, false)

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
  }

  const getTypeIcon = (typeName: string) => {
    if (typeName.includes('blueprint')) return <CloudQueue />
    if (typeName.includes('workflow')) return <Code />
    return <Code />
  }

  const getStatusColor = (status?: string) => {
    if (!status) return 'default'
    switch (status.toUpperCase()) {
      case 'PUBLISHED':
      case 'ACTIVE':
        return 'success'
      case 'DRAFT':
      case 'INACTIVE':
        return 'warning'
      case 'RETIRED':
      case 'DEPRECATED':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { height: '80vh', display: 'flex', flexDirection: 'column' }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <Box sx={{ flexGrow: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              {getTypeIcon(item.type.name)}
              <Typography variant="h6" component="div">
                {item.name}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip
                label={item.type.name.replace('com.vmw.', '').replace('.', ' ')}
                size="small"
                variant="outlined"
              />
              {item.status && (
                <Chip
                  label={item.status}
                  size="small"
                  color={getStatusColor(item.status) as any}
                  variant="outlined"
                />
              )}
              {item.version && (
                <Chip
                  label={`v${item.version}`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              )}
            </Box>
          </Box>
          
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <Divider />

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs
          value={currentTab}
          onChange={handleTabChange}
          aria-label="catalog item tabs"
        >
          <Tab
            label="Overview"
            id="catalog-item-tab-0"
            aria-controls="catalog-item-tabpanel-0"
            icon={<Info />}
            iconPosition="start"
          />
          <Tab
            label="Deploy"
            id="catalog-item-tab-1"
            aria-controls="catalog-item-tabpanel-1"
            icon={<Launch />}
            iconPosition="start"
          />
          {schemaResponse && (
            <Tab
              label="Schema"
              id="catalog-item-tab-2"
              aria-controls="catalog-item-tabpanel-2"
              icon={<Code />}
              iconPosition="start"
            />
          )}
        </Tabs>
      </Box>

      <DialogContent sx={{ flexGrow: 1, overflow: 'auto', p: 0 }}>
        {/* Overview Tab */}
        <TabPanel value={currentTab} index={0}>
          <Box sx={{ px: 3 }}>
            <Typography variant="h6" gutterBottom>
              Description
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              {item.description || 'No description provided for this catalog item.'}
            </Typography>

            <Typography variant="h6" gutterBottom>
              Details
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 2, mb: 2 }}>
              <Typography variant="body2" color="text.secondary">ID:</Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{item.id}</Typography>
              
              <Typography variant="body2" color="text.secondary">Type:</Typography>
              <Typography variant="body2">{item.type.name}</Typography>
              
              {item.status && (
                <>
                  <Typography variant="body2" color="text.secondary">Status:</Typography>
                  <Typography variant="body2">{item.status}</Typography>
                </>
              )}
              
              {item.version && (
                <>
                  <Typography variant="body2" color="text.secondary">Version:</Typography>
                  <Typography variant="body2">{item.version}</Typography>
                </>
              )}
            </Box>
          </Box>
        </TabPanel>

        {/* Deploy Tab */}
        <TabPanel value={currentTab} index={1}>
          <Box sx={{ px: 3 }}>
            {schemaLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : schemaError ? (
              <Alert severity="warning">
                Unable to load deployment form schema. You can still deploy this item, but input validation may be limited.
              </Alert>
            ) : (
              <SchemaForm
                item={item}
                schema={schemaResponse?.item_schema}
                onClose={onClose}
              />
            )}
          </Box>
        </TabPanel>

        {/* Schema Tab */}
        {schemaResponse && (
          <TabPanel value={currentTab} index={2}>
            <Box sx={{ px: 3 }}>
              <Typography variant="h6" gutterBottom>
                JSON Schema
              </Typography>
              <Box
                component="pre"
                sx={{
                  bgcolor: 'background.paper',
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  p: 2,
                  overflow: 'auto',
                  fontSize: '0.875rem',
                  fontFamily: 'monospace',
                  maxHeight: 400,
                }}
              >
                {JSON.stringify(schemaResponse.item_schema, null, 2)}
              </Box>
            </Box>
          </TabPanel>
        )}
      </DialogContent>

      <Divider />

      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose}>
          Close
        </Button>
        {currentTab === 0 && (
          <Button
            variant="contained"
            startIcon={<Launch />}
            onClick={() => setCurrentTab(1)}
          >
            Deploy
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}
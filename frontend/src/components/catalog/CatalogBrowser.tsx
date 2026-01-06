import React, { useState, useMemo } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Skeleton,
  Pagination,
} from '@mui/material'
import {
  Search,
  FilterList,
  Launch,
  Info,
  Category,
  CloudQueue,
} from '@mui/icons-material'
import { useCatalogItems, useCatalogStats } from '@/hooks/useCatalog'
import { useSettingsStore } from '@/store/settingsStore'
import { CatalogItem } from '@/types/api'
import { CatalogItemCard } from './CatalogItemCard'
import { CatalogItemDialog } from './CatalogItemDialog'

interface CatalogBrowserProps {
  projectId?: string
  onItemSelect?: (item: CatalogItem) => void
  initialFilter?: string
}

export const CatalogBrowser: React.FC<CatalogBrowserProps> = ({
  projectId,
  onItemSelect,
  initialFilter = '',
}) => {
  const { settings } = useSettingsStore()
  const [searchTerm, setSearchTerm] = useState(initialFilter)
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [page, setPage] = useState(1)
  const [selectedItem, setSelectedItem] = useState<CatalogItem | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  // Build query parameters
  const queryParams = useMemo(() => ({
    project_id: projectId,
    page_size: settings.pageSize,
    first_page_only: false,
  }), [projectId, settings.pageSize])

  // Fetch catalog items
  const { 
    data: catalogResponse, 
    isLoading, 
    error, 
    refetch 
  } = useCatalogItems(queryParams)

  // Fetch catalog statistics
  const { data: stats } = useCatalogStats(projectId)

  // Filter and search items
  const filteredItems = useMemo(() => {
    if (!catalogResponse?.items) return []
    
    return catalogResponse.items.filter(item => {
      // Search filter
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase()
        const matchesSearch = 
          item.name.toLowerCase().includes(searchLower) ||
          item.description?.toLowerCase().includes(searchLower) ||
          item.id.toLowerCase().includes(searchLower)
        
        if (!matchesSearch) return false
      }
      
      // Type filter
      if (selectedType !== 'all' && item.type.name !== selectedType) {
        return false
      }
      
      // Status filter
      if (selectedStatus !== 'all' && item.status !== selectedStatus) {
        return false
      }
      
      return true
    })
  }, [catalogResponse?.items, searchTerm, selectedType, selectedStatus])

  // Get unique types and statuses for filter options
  const filterOptions = useMemo(() => {
    if (!catalogResponse?.items) return { types: [], statuses: [] }
    
    const types = [...new Set(catalogResponse.items.map(item => item.type.name))]
    const statuses = [...new Set(catalogResponse.items.map(item => item.status).filter(Boolean))]
    
    return { types, statuses }
  }, [catalogResponse?.items])

  // Pagination
  const totalPages = Math.ceil(filteredItems.length / settings.pageSize)
  const paginatedItems = useMemo(() => {
    const startIndex = (page - 1) * settings.pageSize
    return filteredItems.slice(startIndex, startIndex + settings.pageSize)
  }, [filteredItems, page, settings.pageSize])

  const handleItemClick = (item: CatalogItem) => {
    setSelectedItem(item)
    setDialogOpen(true)
    onItemSelect?.(item)
  }

  const handleDialogClose = () => {
    setDialogOpen(false)
    setSelectedItem(null)
  }

  const handlePageChange = (_: React.ChangeEvent<unknown>, newPage: number) => {
    setPage(newPage)
  }

  if (error) {
    return (
      <Alert 
        severity="error" 
        action={
          <Button color="inherit" size="small" onClick={() => refetch()}>
            Retry
          </Button>
        }
      >
        Failed to load catalog items: {error.message}
      </Alert>
    )
  }

  return (
    <Box>
      {/* Header with stats */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Service Catalog
        </Typography>
        {stats && (
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Chip
              icon={<CloudQueue />}
              label={`${stats.totalItems} total items`}
              variant="outlined"
            />
            <Chip
              icon={<Category />}
              label={`${filteredItems.length} filtered`}
              color="primary"
              variant="outlined"
            />
          </Box>
        )}
      </Box>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search catalog items..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={selectedType}
                  label="Type"
                  onChange={(e) => setSelectedType(e.target.value)}
                >
                  <MenuItem value="all">All Types</MenuItem>
                  {filterOptions.types.map(type => (
                    <MenuItem key={type} value={type}>
                      {type.replace('com.vmw.', '').replace('.', ' ')}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={selectedStatus}
                  label="Status"
                  onChange={(e) => setSelectedStatus(e.target.value)}
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  {filterOptions.statuses.map(status => (
                    <MenuItem key={status} value={status}>
                      {status}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => {
                  setSearchTerm('')
                  setSelectedType('all')
                  setSelectedStatus('all')
                  setPage(1)
                }}
              >
                Clear
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Items Grid */}
      {isLoading ? (
        <Grid container spacing={2}>
          {Array.from({ length: 8 }).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="80%" height={32} />
                  <Skeleton variant="text" width="60%" height={20} />
                  <Skeleton variant="text" width="100%" height={60} />
                </CardContent>
                <CardActions>
                  <Skeleton variant="rectangular" width={80} height={36} />
                  <Skeleton variant="rectangular" width={60} height={36} />
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : paginatedItems.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <CloudQueue sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {searchTerm || selectedType !== 'all' || selectedStatus !== 'all'
                ? 'No items match your filters'
                : 'No catalog items available'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {searchTerm || selectedType !== 'all' || selectedStatus !== 'all'
                ? 'Try adjusting your search or filter criteria'
                : 'Contact your administrator to add catalog items'}
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <>
          <Grid container spacing={2}>
            {paginatedItems.map((item) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={item.id}>
                <CatalogItemCard
                  item={item}
                  onClick={() => handleItemClick(item)}
                />
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
                size="large"
              />
            </Box>
          )}
        </>
      )}

      {/* Item Details Dialog */}
      {selectedItem && (
        <CatalogItemDialog
          item={selectedItem}
          open={dialogOpen}
          onClose={handleDialogClose}
        />
      )}
    </Box>
  )
}
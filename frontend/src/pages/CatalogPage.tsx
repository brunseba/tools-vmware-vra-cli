import React from 'react'
import { Box, Typography } from '@mui/material'
import { StoreMallDirectory } from '@mui/icons-material'
import { CatalogBrowser } from '@/components/catalog/CatalogBrowser'
import { useSettingsStore } from '@/store/settingsStore'
import { useSearchParams } from 'react-router-dom'

export const CatalogPage: React.FC = () => {
  const { settings } = useSettingsStore()
  const [searchParams] = useSearchParams()
  const filterParam = searchParams.get('filter') || ''

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <StoreMallDirectory sx={{ mr: 1, fontSize: 32 }} />
        <Typography variant="h4" component="h1">
          Service Catalog
        </Typography>
      </Box>

      <CatalogBrowser 
        projectId={settings.defaultProject}
        initialFilter={filterParam}
      />
    </Box>
  )
}

import React from 'react'
import { Box, Typography } from '@mui/material'
import { StoreMallDirectory } from '@mui/icons-material'

export const CatalogPage: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <StoreMallDirectory sx={{ mr: 1, fontSize: 32 }} />
        <Typography variant="h4" component="h1">
          Service Catalog
        </Typography>
      </Box>

      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Service Catalog Browser
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Catalog item browser and deployment interface will be implemented here
        </Typography>
      </Box>
    </Box>
  )
}
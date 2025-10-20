import React from 'react'
import { Box, Typography } from '@mui/material'
import { Analytics } from '@mui/icons-material'

export const ReportsPage: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Analytics sx={{ mr: 1, fontSize: 32 }} />
        <Typography variant="h4" component="h1">
          Reports & Analytics
        </Typography>
      </Box>

      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Usage reports, activity timelines, and analytics charts will be implemented here
        </Typography>
      </Box>
    </Box>
  )
}
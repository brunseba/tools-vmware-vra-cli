import React from 'react'
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  Tooltip,
  IconButton,
} from '@mui/material'
import {
  Launch,
  Info,
  CloudQueue,
  Code,
  Storage,
  Settings,
} from '@mui/icons-material'
import { CatalogItem } from '@/types/api'

interface CatalogItemCardProps {
  item: CatalogItem
  onClick?: () => void
}

export const CatalogItemCard: React.FC<CatalogItemCardProps> = ({
  item,
  onClick,
}) => {
  const getTypeIcon = (typeName: string) => {
    if (typeName.includes('blueprint')) return <CloudQueue />
    if (typeName.includes('workflow')) return <Code />
    if (typeName.includes('vro')) return <Settings />
    return <Storage />
  }

  const getTypeDisplay = (typeName: string) => {
    if (typeName.includes('blueprint')) return 'Blueprint'
    if (typeName.includes('workflow')) return 'Workflow'
    if (typeName.includes('vro.workflow')) return 'vRO Workflow'
    return typeName.replace('com.vmw.', '').replace('.', ' ')
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
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 3,
        },
      }}
      onClick={onClick}
    >
      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        {/* Header with type icon and status */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getTypeIcon(item.type.name)}
            <Typography variant="caption" color="text.secondary">
              {getTypeDisplay(item.type.name)}
            </Typography>
          </Box>
          
          {item.status && (
            <Chip
              label={item.status}
              size="small"
              color={getStatusColor(item.status) as any}
              variant="outlined"
            />
          )}
        </Box>

        {/* Item name */}
        <Tooltip title={item.name} placement="top">
          <Typography
            variant="h6"
            component="h3"
            gutterBottom
            sx={{
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              minHeight: 48,
              fontSize: '1rem',
            }}
          >
            {item.name}
          </Typography>
        </Tooltip>

        {/* Description */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            minHeight: 60,
            mb: 2,
          }}
        >
          {item.description || 'No description available'}
        </Typography>

        {/* Version chip */}
        {item.version && (
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              label={`v${item.version}`}
              size="small"
              variant="outlined"
              color="primary"
            />
          </Box>
        )}
      </CardContent>

      <CardActions sx={{ pt: 0, px: 2, pb: 2 }}>
        <Button
          size="small"
          startIcon={<Launch />}
          onClick={(e) => {
            e.stopPropagation()
            onClick?.()
          }}
        >
          Deploy
        </Button>
        
        <Tooltip title="View details">
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation()
              onClick?.()
            }}
          >
            <Info />
          </IconButton>
        </Tooltip>

        <Box sx={{ flexGrow: 1 }} />
        
        {/* Item ID for reference */}
        <Tooltip title={`ID: ${item.id}`}>
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              fontSize: '0.7rem',
              maxWidth: 80,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {item.id}
          </Typography>
        </Tooltip>
      </CardActions>
    </Card>
  )
}
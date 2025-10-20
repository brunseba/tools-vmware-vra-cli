import React from 'react'
import {
  Snackbar,
  Alert,
  AlertTitle,
  IconButton,
  Box,
  Slide,
  SlideProps,
} from '@mui/material'
import { Close } from '@mui/icons-material'
import { useSettingsStore } from '@/store/settingsStore'

function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="left" />
}

export const NotificationSnackbar: React.FC = () => {
  const { notifications, removeNotification } = useSettingsStore()

  if (notifications.length === 0) {
    return null
  }

  // Show the most recent notification
  const notification = notifications[0]

  const handleClose = (_?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return
    }
    removeNotification(notification.id)
  }

  return (
    <Snackbar
      open={true}
      autoHideDuration={notification.autoHide !== false ? (notification.duration || 6000) : null}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      TransitionComponent={SlideTransition}
      sx={{ mt: 8 }} // Account for app bar height
    >
      <Alert
        severity={notification.type}
        variant="filled"
        onClose={handleClose}
        sx={{ 
          minWidth: 300,
          maxWidth: 500,
          '& .MuiAlert-message': {
            width: '100%'
          }
        }}
      >
        {notification.title && (
          <AlertTitle>{notification.title}</AlertTitle>
        )}
        {notification.message}
        
        {/* Show notification count if multiple */}
        {notifications.length > 1 && (
          <Box
            component="span"
            sx={{
              display: 'inline-block',
              ml: 1,
              px: 1,
              py: 0.25,
              borderRadius: 1,
              fontSize: '0.75rem',
              bgcolor: 'rgba(255, 255, 255, 0.2)',
            }}
          >
            +{notifications.length - 1} more
          </Box>
        )}
      </Alert>
    </Snackbar>
  )
}
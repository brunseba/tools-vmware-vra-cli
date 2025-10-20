import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'
import { useAuthStore } from '@/store/authStore'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { CatalogPage } from '@/pages/CatalogPage'
import { DeploymentsPage } from '@/pages/DeploymentsPage'
import { ReportsPage } from '@/pages/ReportsPage'
import { Layout } from '@/components/common/Layout'
import { NotificationSnackbar } from '@/components/common/NotificationSnackbar'

function App() {
  const { user } = useAuthStore()

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {user?.isAuthenticated ? (
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route
              path="/dashboard"
              element={
                <AuthGuard>
                  <DashboardPage />
                </AuthGuard>
              }
            />
            <Route
              path="/catalog"
              element={
                <AuthGuard>
                  <CatalogPage />
                </AuthGuard>
              }
            />
            <Route
              path="/deployments"
              element={
                <AuthGuard>
                  <DeploymentsPage />
                </AuthGuard>
              }
            />
            <Route
              path="/reports"
              element={
                <AuthGuard>
                  <ReportsPage />
                </AuthGuard>
              }
            />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Layout>
      ) : (
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      )}
      
      <NotificationSnackbar />
    </Box>
  )
}

export default App
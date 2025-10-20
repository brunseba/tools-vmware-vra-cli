import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { useSettingsStore } from '@/store/settingsStore'
import App from './App'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
})

// Theme provider component
function ThemedApp() {
  const { theme } = useSettingsStore()

  const muiTheme = React.useMemo(() => {
    return createTheme({
      palette: {
        mode: theme.mode,
        primary: {
          main: theme.primaryColor,
        },
        secondary: {
          main: theme.secondaryColor,
        },
      },
      typography: {
        fontSize: theme.fontSize === 'small' ? 12 : theme.fontSize === 'large' ? 16 : 14,
      },
      components: {
        MuiCssBaseline: {
          styleOverrides: {
            body: {
              scrollbarColor: theme.mode === 'dark' ? '#6b6b6b #2b2b2b' : '#c1c1c1 #ffffff',
              '&::-webkit-scrollbar, & *::-webkit-scrollbar': {
                backgroundColor: theme.mode === 'dark' ? '#2b2b2b' : '#ffffff',
              },
              '&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb': {
                borderRadius: 8,
                backgroundColor: theme.mode === 'dark' ? '#6b6b6b' : '#c1c1c1',
                minHeight: 24,
                border: theme.mode === 'dark' ? '3px solid #2b2b2b' : '3px solid #ffffff',
              },
            },
          },
        },
      },
    })
  }, [theme])

  return (
    <ThemeProvider theme={muiTheme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ThemedApp />
        <ReactQueryDevtools initialIsOpen={false} />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
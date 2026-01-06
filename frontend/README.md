# VMware vRA Web UI

Modern React-based web interface for VMware vRealize Automation operations.

## Features

- 🔐 **Authentication**: Login with vRA credentials
- 🎨 **Material-UI**: Modern, responsive design
- 🌙 **Dark Mode**: Toggle between light and dark themes
- 📱 **Responsive**: Works on desktop, tablet, and mobile
- 🔄 **Real-time**: Live updates and notifications
- 📊 **Dashboard**: Overview metrics and activity
- 🛍️ **Service Catalog**: Browse and deploy catalog items
- 📦 **Deployments**: Manage deployment lifecycle
- 📈 **Reports**: Analytics and usage insights

## Technology Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Material-UI (MUI)** for components and theming
- **React Query (TanStack Query)** for data fetching
- **Zustand** for state management
- **React Router** for navigation
- **Axios** for API communication

## Development Setup

### Prerequisites

- Node.js 18+ 
- Backend REST API server running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at http://localhost:3000

### Building for Production

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture

```
src/
├── components/          # React components
│   ├── auth/           # Authentication components
│   ├── catalog/        # Catalog browser components
│   ├── deployments/    # Deployment management
│   ├── reports/        # Analytics and reports
│   └── common/         # Shared components
├── hooks/              # Custom React hooks
├── pages/              # Page components
├── services/           # API service layer
├── store/              # Zustand stores
├── types/              # TypeScript definitions
└── utils/              # Utility functions
```

## Configuration

The application uses environment variables and runtime configuration:

- **API Proxy**: Configured in `vite.config.ts` to proxy `/api` to `http://localhost:8000`
- **Theme**: Supports light/dark mode with Material-UI theming
- **Persistence**: Settings and auth state persist in localStorage

## API Integration

The frontend integrates with the existing FastAPI backend:

- **Authentication**: `/auth/*` endpoints
- **Catalog**: `/catalog/*` endpoints  
- **Deployments**: `/deployments/*` endpoints
- **Reports**: `/reports/*` endpoints

All API calls include error handling, loading states, and automatic retries.

## Features Implementation Status

- ✅ Authentication system
- ✅ Responsive layout with navigation
- ✅ Dark/light theme support
- ✅ Dashboard with metrics (placeholder)
- ✅ Settings and notification system
- 🚧 Service catalog browser
- 🚧 Deployment management
- 🚧 Reports and analytics
- 🚧 Schema-driven forms
- 🚧 Real-time updates

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Contributing

1. Follow conventional commits
2. Use TypeScript strictly
3. Follow Material-UI patterns
4. Test all features thoroughly
5. Update documentation
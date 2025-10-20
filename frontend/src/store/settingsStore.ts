import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AppSettings, FeatureFlags, ThemeConfig, Notification } from '@/types/app';

interface SettingsState {
  settings: AppSettings;
  theme: ThemeConfig;
  featureFlags: FeatureFlags;
  notifications: Notification[];
  
  // Actions
  updateSettings: (updates: Partial<AppSettings>) => void;
  updateTheme: (updates: Partial<ThemeConfig>) => void;
  toggleDarkMode: () => void;
  updateFeatureFlags: (updates: Partial<FeatureFlags>) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

const defaultSettings: AppSettings = {
  darkMode: false,
  apiBaseUrl: '/api',
  defaultProject: '',
  pageSize: 25,
  autoRefresh: true,
  refreshInterval: 30000, // 30 seconds
};

const defaultTheme: ThemeConfig = {
  mode: 'light',
  primaryColor: '#1976d2',
  secondaryColor: '#dc004e',
  fontSize: 'medium',
};

const defaultFeatureFlags: FeatureFlags = {
  enableReports: true,
  enableWorkflows: true,
  enableBulkOperations: true,
  enableRealTimeUpdates: false,
  enableExport: true,
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      settings: defaultSettings,
      theme: defaultTheme,
      featureFlags: defaultFeatureFlags,
      notifications: [],

      updateSettings: (updates: Partial<AppSettings>) => {
        set((state) => ({
          settings: { ...state.settings, ...updates }
        }));
      },

      updateTheme: (updates: Partial<ThemeConfig>) => {
        set((state) => ({
          theme: { ...state.theme, ...updates }
        }));
        
        // Also update darkMode setting for consistency
        if (updates.mode) {
          set((state) => ({
            settings: { 
              ...state.settings, 
              darkMode: updates.mode === 'dark' 
            }
          }));
        }
      },

      toggleDarkMode: () => {
        set((state) => {
          const newMode = state.theme.mode === 'light' ? 'dark' : 'light';
          return {
            theme: { ...state.theme, mode: newMode },
            settings: { ...state.settings, darkMode: newMode === 'dark' }
          };
        });
      },

      updateFeatureFlags: (updates: Partial<FeatureFlags>) => {
        set((state) => ({
          featureFlags: { ...state.featureFlags, ...updates }
        }));
      },

      addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => {
        const newNotification: Notification = {
          ...notification,
          id: `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date(),
        };

        set((state) => ({
          notifications: [newNotification, ...state.notifications]
        }));

        // Auto-remove notification if specified
        if (notification.autoHide !== false) {
          const duration = notification.duration || 5000;
          setTimeout(() => {
            get().removeNotification(newNotification.id);
          }, duration);
        }
      },

      removeNotification: (id: string) => {
        set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id)
        }));
      },

      clearNotifications: () => {
        set({ notifications: [] });
      },
    }),
    {
      name: 'settings-storage',
      partialize: (state) => ({
        settings: state.settings,
        theme: state.theme,
        featureFlags: state.featureFlags,
      }),
    }
  )
);
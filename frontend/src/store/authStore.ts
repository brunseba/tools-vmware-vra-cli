import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types/app';
import { authService } from '@/services/auth';
import { AuthRequest } from '@/types/api';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: AuthRequest) => Promise<void>;
  logout: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
  refreshToken: () => Promise<void>;
  clearError: () => void;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      error: null,

      login: async (credentials: AuthRequest) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authService.login(credentials);
          
          if (response.success) {
            const user: User = {
              username: credentials.username,
              tenant: credentials.tenant,
              domain: credentials.domain,
              isAuthenticated: true,
            };
            
            set({ 
              user,
              isLoading: false,
              error: null 
            });
          } else {
            throw new Error(response.message || 'Login failed');
          }
        } catch (error: any) {
          set({ 
            isLoading: false,
            error: error.message || 'Login failed',
            user: null 
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true, error: null });
        
        try {
          await authService.logout();
          set({ 
            user: null,
            isLoading: false,
            error: null 
          });
        } catch (error: any) {
          // Even if logout API fails, clear local state
          set({ 
            user: null,
            isLoading: false,
            error: null 
          });
        }
      },

      checkAuthStatus: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authService.getStatus();
          
          if (response.success) {
            // If we have a user in store and auth is valid, keep it
            const currentUser = get().user;
            if (currentUser) {
              set({ isLoading: false, error: null });
              return;
            }
          }
          
          // Otherwise, clear auth state
          set({ 
            user: null,
            isLoading: false,
            error: null 
          });
        } catch (error: any) {
          set({ 
            user: null,
            isLoading: false,
            error: error.message 
          });
        }
      },

      refreshToken: async () => {
        try {
          await authService.refreshToken();
        } catch (error: any) {
          // If refresh fails, logout
          set({ 
            user: null,
            error: 'Session expired. Please login again.' 
          });
          throw error;
        }
      },

      clearError: () => {
        set({ error: null });
      },

      setUser: (user: User | null) => {
        set({ user });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user 
      }),
    }
  )
);
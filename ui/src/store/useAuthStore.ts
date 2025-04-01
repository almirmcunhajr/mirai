import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ApiService } from '../services/api';

interface User {
  email: string;
  name: string;
  picture?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  setError: (error: string | null) => void;
  setLoading: (isLoading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,
      login: (token, user) => {
        ApiService.getInstance().setToken(token);
        set({ token, user, error: null });
      },
      logout: () => {
        ApiService.getInstance().setToken(null);
        set({ token: null, user: null, error: null });
      },
      setError: (error) => set({ error }),
      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'auth-storage',
      onRehydrateStorage: () => (state) => {
        if (state?.token) {
          ApiService.getInstance().setToken(state.token);
        }
      },
    }
  )
); 
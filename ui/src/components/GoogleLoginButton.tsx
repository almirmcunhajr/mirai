import React, { useEffect } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { AuthService } from '../services/auth';

declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          renderButton: (element: HTMLElement, config: any) => void;
        };
      };
    };
  }
}

export const GoogleLoginButton: React.FC = () => {
  const { login, setError, setLoading } = useAuthStore();
  const authService = AuthService.getInstance();

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);

    script.onload = () => {
      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        callback: async (response: any) => {
          try {
            setLoading(true);
            const { token, user } = await authService.loginWithGoogle(response.credential);
            login(token, user);
          } catch (error) {
            setError(error instanceof Error ? error.message : 'Failed to login with Google');
          } finally {
            setLoading(false);
          }
        },
      });

      window.google.accounts.id.renderButton(
        document.getElementById('google-login-button')!,
        { theme: 'outline', size: 'large', width: '100%' }
      );
    };

    return () => {
      document.head.removeChild(script);
    };
  }, [login, setError, setLoading]);

  return (
    <div id="google-login-button" className="w-full max-w-sm mx-auto" />
  );
}; 
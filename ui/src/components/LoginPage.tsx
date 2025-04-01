import React from 'react';
import { GoogleLoginButton } from './GoogleLoginButton';
import { useAuthStore } from '../store/useAuthStore';

export const LoginPage: React.FC = () => {
  const { error, isLoading } = useAuthStore();

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-2xl font-bold text-white text-center mb-6">Welcome to Mir.ai</h1>
        <p className="text-gray-400 text-center mb-8">
          Sign in to start creating your interactive stories
        </p>
        
        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <GoogleLoginButton />
        </div>

        {isLoading && (
          <div className="mt-4 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-white mx-auto"></div>
          </div>
        )}
      </div>
    </div>
  );
}; 
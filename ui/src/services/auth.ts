import { ApiService } from './api';

const API_BASE_URL = import.meta.env.VITE_API_URL;

export interface User {
  email: string;
  name: string;
  picture?: string;
}

export class AuthService {
  private static instance: AuthService;
  private constructor() {}

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  async loginWithGoogle(idToken: string): Promise<{ token: string; user: User }> {
    const response = await fetch(`${API_BASE_URL}/auth/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id_token: idToken }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to login with Google');
    }

    const data = await response.json();
    return {
      token: data.access_token,
      user: await this.getCurrentUser(data.access_token),
    };
  }

  async getCurrentUser(token: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get user information');
    }

    return response.json();
  }
} 
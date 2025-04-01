import { Story, StoryNode, Genre } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL;

export class ApiService {
  private static instance: ApiService;
  private token: string | null = null;

  private constructor() {}

  static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async createStory(genre: Genre, languageCode: string = 'pt-BR'): Promise<Story> {
    const response = await fetch(`${API_BASE_URL}/stories`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ genre, language_code: languageCode }),
    });

    if (!response.ok) {
      throw new Error('Failed to create story');
    }

    return response.json();
  }

  async getStory(storyId: string): Promise<Story> {
    const response = await fetch(`${API_BASE_URL}/stories/${storyId}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to get story');
    }

    return response.json();
  }

  async listStories(): Promise<Story[]> {
    const response = await fetch(`${API_BASE_URL}/stories`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to list stories');
    }

    return response.json();
  }

  async deleteStory(storyId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/stories/${storyId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to delete story');
    }
  }

  async createBranch(storyId: string, parentNodeId: string, decision: string): Promise<Story> {
    const response = await fetch(`${API_BASE_URL}/stories/${storyId}/branches`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ parent_node_id: parentNodeId, decision }),
    });

    if (!response.ok) {
      throw new Error('Failed to create branch');
    }

    return response.json();
  }

  async getStoryTree(storyId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/stories/${storyId}`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch story');
    }
    return response.json();
  }

  async getVideoUrl(storyId: string, nodeId: string): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/videos/stories/${storyId}/nodes/${nodeId}`, {
      headers: {
        'Authorization': this.token ? `Bearer ${this.token}` : '',
        'Accept': 'video/mp4',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch video');
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    return url;
  }
} 
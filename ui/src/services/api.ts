import { Story, StoryNode, Genre } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL;

export class ApiService {
  private static instance: ApiService;
  private constructor() {}

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  async createStory(genre: Genre, languageCode: string = 'pt-BR'): Promise<Story> {
    const response = await fetch(`${API_BASE_URL}/stories`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ genre, language_code: languageCode }),
    });

    if (!response.ok) {
      throw new Error('Failed to create story');
    }

    return response.json();
  }

  async createBranch(storyId: string, parentNodeId: string, decision: string, languageCode: string = 'pt-BR'): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/stories/${storyId}/branches`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        parent_node_id: parentNodeId,
        decision,
        language_code: languageCode,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Failed to create branch' }));
      throw new Error(error.message || 'Failed to create branch');
    }

    const data = await response.json();
    return data;
  }

  async getStoryTree(storyId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/stories/${storyId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch story');
    }
    return response.json();
  }

  async listStories(): Promise<Story[]> {
    const response = await fetch(`${API_BASE_URL}/stories`);

    if (!response.ok) {
      throw new Error('Failed to list stories');
    }

    return response.json();
  }

  async deleteStory(storyId: string): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}/stories/${storyId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete story');
    }

    return response.json();
  }

  getVideoUrl(storyId: string, nodeId: string): string {
    return `${API_BASE_URL}/videos/stories/${storyId}/nodes/${nodeId}`;
  }
} 
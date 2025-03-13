import { Story, StoryNode, Genre } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export class ApiService {
  private static instance: ApiService;
  private constructor() {}

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  async createStory(genre: Genre, languageCode: string = 'en'): Promise<Story> {
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

  async createBranch(storyId: string, parentNodeId: string, decision: string, languageCode: string = 'en'): Promise<Story> {
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
      throw new Error('Failed to create branch');
    }

    return response.json();
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
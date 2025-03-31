import { create, StateCreator } from 'zustand';
import type { Story, StoryNode, Decision, Genre } from '../types';
import { ApiService } from '../services/api';

type View = 'home' | 'create' | 'player';

interface StoryState {
  stories: Story[];
  currentStory: Story | null;
  currentView: View;
  storyNodes: Record<string, StoryNode>;
  isPlaying: boolean;
  volume: number;
  showDecisions: boolean;
  currentVideoTime: number;
  videoDuration: number;
  isLoading: boolean;
  error: string | null;
  createStory: (genre: Genre) => Promise<void>;
  loadStory: (storyId: string) => Promise<void>;
  closeStory: () => void;
  makeDecision: (decision: string) => Promise<void>;
  setPlaying: (isPlaying: boolean) => void;
  setVolume: (volume: number) => void;
  setCurrentView: (view: View) => void;
  setVideoProgress: (time: number, duration: number) => void;
  getCurrentNode: () => StoryNode | null;
  setShowDecisions: (show: boolean) => void;
  fetchStories: () => Promise<void>;
  navigateToNode: (nodeId: string) => void;
}

const api = ApiService.getInstance();

export const useStoryStore = create<StoryState>((set: any, get: any) => ({
  stories: [],
  currentStory: null,
  currentView: 'home',
  storyNodes: {},
  isPlaying: false,
  volume: 1,
  showDecisions: false,
  currentVideoTime: 0,
  videoDuration: 0,
  isLoading: false,
  error: null,
  
  createStory: async (genre: Genre) => {
    try {
      // Immediately switch to player view with loading state
      set({ 
        currentView: 'player',
        isLoading: true,
        error: null,
        currentStory: {
          id: 'pending',
          title: 'Creating your story...',
          genre,
          currentNode: 'pending',
          lastPlayedAt: new Date()
        }
      });

      const newStory = await api.createStory(genre);
      
      // Load the story tree
      const storyTree = await api.getStoryTree(newStory.id);
      
      // Transform nodes into our format
      const nodeMap: Record<string, StoryNode> = {};
      const transformNode = (node: any): StoryNode => {
        const transformedNode: StoryNode = {
          id: node.id,
          content: node.script?.frames?.[0]?.narration || '',
          videoUrl: node.video_url,
          thumbnail_url: node.thumbnail_url,
          decision: node.decision,
          parentId: node.parent_id,
          children: node.children.map((childId: string) => {
            const childNode = storyTree.nodes.find((n: any) => n.id === childId);
            if (childNode) {
              return transformNode(childNode);
            }
            return null;
          }).filter(Boolean) as StoryNode[]
        };
        nodeMap[node.id] = transformedNode;
        return transformedNode;
      };

      // Transform all nodes starting from the root
      const rootNode = storyTree.nodes.find((n: any) => n.id === storyTree.root_node_id);
      if (rootNode) {
        transformNode(rootNode);
      }
      
      set((state: StoryState) => ({
        stories: [...state.stories, newStory],
        currentStory: {
          ...newStory,
          currentNode: storyTree.root_node_id
        },
        storyNodes: nodeMap,
        showDecisions: false,
        isPlaying: true,
        isLoading: false
      }));
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to create story',
        isLoading: false 
      });
    }
  },
  
  loadStory: async (storyId: string) => {
    try {
      set({ isLoading: true, error: null });
      const story = get().stories.find((s: Story) => s.id === storyId);
      if (!story) {
        throw new Error('Story not found');
      }
      
      const storyTree = await api.getStoryTree(storyId);
      
      // Transform nodes into our format
      const nodeMap: Record<string, StoryNode> = {};
      const transformNode = (node: any): StoryNode => {
        const transformedNode: StoryNode = {
          id: node.id,
          content: node.script?.frames?.[0]?.narration || '',
          videoUrl: node.video_url,
          thumbnail_url: node.thumbnail_url,
          decision: node.decision,
          parentId: node.parent_id,
          children: node.children.map((childId: string) => {
            const childNode = storyTree.nodes.find((n: any) => n.id === childId);
            if (childNode) {
              return transformNode(childNode);
            }
            return null;
          }).filter(Boolean) as StoryNode[]
        };
        nodeMap[node.id] = transformedNode;
        return transformedNode;
      };

      // Transform all nodes starting from the root
      const rootNode = storyTree.nodes.find((n: any) => n.id === storyTree.root_node_id);
      if (rootNode) {
        transformNode(rootNode);
      }

      // Find the most recently created leaf node
      let latestNode = storyTree.nodes[0];
      storyTree.nodes.forEach((node: any) => {
        if (node.created_at > latestNode.created_at) {
          latestNode = node;
        }
      });
      
      set((state: StoryState) => ({
        currentStory: {
          ...story,
          currentNode: latestNode.id
        },
        currentView: 'player',
        showDecisions: false,
        isPlaying: true,
        storyNodes: nodeMap,
        isLoading: false
      }));
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to load story',
        isLoading: false 
      });
    }
  },

  closeStory: () => {
    set({ 
      currentStory: null, 
      currentView: 'home',
      showDecisions: false,
      currentVideoTime: 0,
      videoDuration: 0,
      isPlaying: false,
      error: null
    });
  },
  
  makeDecision: async (decision: string) => {
    try {
      set({ isLoading: true, error: null });
      const state = get();
      if (!state.currentStory) {
        throw new Error('No story loaded');
      }

      const response = await api.createBranch(
        state.currentStory.id,
        state.currentStory.currentNode,
        decision
      );

      // Update the current node and story state
      set((state: StoryState) => ({
        currentStory: {
          ...state.currentStory!,
          currentNode: response.nodes[response.nodes.length - 1].id
        },
        showDecisions: false,
        currentVideoTime: 0,
        isPlaying: true,
        isLoading: false,
        error: null
      }));

      // Load the updated story tree
      const storyTree = await api.getStoryTree(state.currentStory.id);
      
      // Transform nodes into our format
      const nodeMap: Record<string, StoryNode> = {};
      const transformNode = (node: any): StoryNode => {
        const transformedNode: StoryNode = {
          id: node.id,
          content: node.script?.frames?.[0]?.narration || '',
          videoUrl: node.video_url,
          thumbnail_url: node.thumbnail_url,
          decision: node.decision,
          parentId: node.parent_id,
          children: node.children.map((childId: string) => {
            const childNode = storyTree.nodes.find((n: any) => n.id === childId);
            if (childNode) {
              return transformNode(childNode);
            }
            return null;
          }).filter(Boolean) as StoryNode[]
        };
        nodeMap[node.id] = transformedNode;
        return transformedNode;
      };

      // Transform all nodes starting from the root
      const rootNode = storyTree.nodes.find((n: any) => n.id === storyTree.root_node_id);
      if (rootNode) {
        transformNode(rootNode);
      }
      
      set({ storyNodes: nodeMap });
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to make decision',
        isLoading: false 
      });
    }
  },
  
  setPlaying: (isPlaying: boolean) => set({ isPlaying }),
  setVolume: (volume: number) => set({ volume }),
  setCurrentView: (view: View) => set((state: StoryState) => ({ currentView: view })),
  setShowDecisions: (show: boolean) => set({ showDecisions: show }),
  
  setVideoProgress: (time: number, duration: number) => {
    set({ currentVideoTime: time, videoDuration: duration });
    // Show decisions when video ends
    if (duration > 0 && duration - time == 0 && !get().showDecisions) {
      set({ showDecisions: true, isPlaying: false });
    }
  },

  getCurrentNode: () => {
    const state = get();
    if (!state.currentStory) return null;
    return state.storyNodes[state.currentStory.currentNode] || null;
  },

  fetchStories: async () => {
    try {
      set({ isLoading: true, error: null });
      const stories = await api.listStories();
      
      // Load story nodes for each story
      const nodeMap: Record<string, StoryNode> = {};
      for (const story of stories) {
        const storyTree = await api.getStoryTree(story.id);
        
        // Transform nodes into our format
        const transformNode = (node: any): StoryNode => {
          const transformedNode: StoryNode = {
            id: node.id,
            content: node.script?.frames?.[0]?.narration || '',
            videoUrl: node.video_url,
            thumbnail_url: node.thumbnail_url,
            decision: node.decision,
            parentId: node.parent_id,
            children: node.children.map((childId: string) => {
              const childNode = storyTree.nodes.find((n: any) => n.id === childId);
              if (childNode) {
                return transformNode(childNode);
              }
              return null;
            }).filter(Boolean) as StoryNode[]
          };
          nodeMap[node.id] = transformedNode;
          return transformedNode;
        };

        // Transform all nodes starting from the root
        const rootNode = storyTree.nodes.find((n: any) => n.id === storyTree.root_node_id);
        if (rootNode) {
          transformNode(rootNode);
        }
      }
      
      // Set the currentNode to root_node_id for each story
      const storiesWithCurrentNode = stories.map(story => ({
        ...story,
        currentNode: story.root_node_id
      }));
      set({ stories: storiesWithCurrentNode, storyNodes: nodeMap, isLoading: false });
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch stories',
        isLoading: false 
      });
    }
  },

  navigateToNode: (nodeId: string) => {
    const { storyNodes } = get();
    const node = storyNodes[nodeId];
    
    if (!node) {
      set({ error: 'Node not found' });
      return;
    }

    set((state: StoryState) => ({
      currentStory: state.currentStory ? {
        ...state.currentStory,
        currentNode: nodeId
      } : null,
      error: null
    }));
  }
}));
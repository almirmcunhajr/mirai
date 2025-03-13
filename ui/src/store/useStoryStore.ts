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
  makeDecision: (nextNode: string) => Promise<void>;
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
      set({ isLoading: true, error: null });
      const newStory = await api.createStory(genre);
      set((state: StoryState) => ({
        stories: [...state.stories, newStory],
        currentStory: newStory,
        currentView: 'player',
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
          decisions: (node.script?.decisions || []).map((text: string, index: number) => ({
            id: `${node.id}-decision-${index}`,
            text,
            targetNodeId: node.children[index] || ''
          })),
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
        currentStory: {
          ...story,
          currentNode: storyTree.root_node_id
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
  
  makeDecision: async (nextNode: string) => {
    try {
      set({ isLoading: true, error: null });
      const state = get();
      if (!state.currentStory) {
        throw new Error('No story loaded');
      }

      const updatedStory = await api.createBranch(
        state.currentStory.id,
        state.currentStory.currentNode,
        nextNode
      );

      // Transform the new branch and add it to the tree
      const transformNode = (node: any): StoryNode => {
        // Transform script decisions into our Decision format
        const decisions = (node.script?.decisions || []).map((text: string, index: number) => ({
          id: `${node.id}-decision-${index}`,
          text,
          targetNodeId: node.children[index] || ''
        }));

        return {
          id: node.id,
          content: node.script?.frames?.[0]?.narration || '',
          videoUrl: node.video_url,
          decisions,
          parentId: node.parent_id,
          children: (node.children || []).map(transformNode)
        };
      };

      const transformedTree = transformNode(updatedStory);
      
      // Update the node map with the new branch
      const nodeMap = { ...state.storyNodes };
      const addToMap = (node: StoryNode) => {
        nodeMap[node.id] = node;
        node.children.forEach(addToMap);
      };
      addToMap(transformedTree);

      set((state: StoryState) => ({
        currentStory: {
          ...state.currentStory,
          currentNode: nextNode,
          lastPlayedAt: new Date()
        },
        storyNodes: nodeMap,
        showDecisions: false,
        currentVideoTime: 0,
        isPlaying: true,
        currentView: 'player',
        isLoading: false
      }));
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
    // Show decisions when video is near the end (2 seconds before end)
    if (duration > 0 && duration - time <= 2 && !get().showDecisions) {
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
      set({ stories, isLoading: false });
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
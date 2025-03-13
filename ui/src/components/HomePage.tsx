import React, { useEffect } from 'react';
import { StoryList } from './StoryList';
import { useStoryStore } from '../store/useStoryStore';

export const HomePage: React.FC = () => {
  const { fetchStories, isLoading, error } = useStoryStore();

  useEffect(() => {
    fetchStories();
  }, [fetchStories]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500 text-center">
          <p className="text-xl font-semibold mb-2">Error</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold text-white mb-6">Continue Your Journey</h2>
      <StoryList />
    </div>
  );
};
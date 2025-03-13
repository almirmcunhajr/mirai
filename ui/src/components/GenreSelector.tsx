import React from 'react';
import { useStoryStore } from '../store/useStoryStore';
import type { Genre } from '../types';
import { Wand2, Rocket, Search, Skull } from 'lucide-react';

const genres: { id: Genre; icon: React.ReactNode; label: string }[] = [
  { id: 'fantasy', icon: <Wand2 size={32} />, label: 'Fantasy' },
  { id: 'sci-fi', icon: <Rocket size={32} />, label: 'Sci-Fi' },
  { id: 'mystery', icon: <Search size={32} />, label: 'Mystery' },
  { id: 'horror', icon: <Skull size={32} />, label: 'Horror' },
];

export const GenreSelector: React.FC = () => {
  const { createStory, isLoading, error } = useStoryStore();

  const handleGenreSelect = async (genre: Genre) => {
    try {
      await createStory(genre);
    } catch (error) {
      // Error is handled by the store
      console.error('Failed to create story:', error);
    }
  };

  if (error) {
    return (
      <div className="text-center text-red-500">
        <p className="text-xl font-semibold mb-2">Error</p>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto p-4">
      {genres.map((genre) => (
        <button
          key={genre.id}
          onClick={() => handleGenreSelect(genre.id)}
          disabled={isLoading}
          className={`flex flex-col items-center justify-center p-6 bg-gray-800 rounded-lg transition duration-300 ${
            isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-700'
          }`}
        >
          <div className="text-red-600 mb-3">{genre.icon}</div>
          <span className="text-white font-medium">{genre.label}</span>
          {isLoading && (
            <div className="mt-2">
              <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
            </div>
          )}
        </button>
      ))}
    </div>
  );
};
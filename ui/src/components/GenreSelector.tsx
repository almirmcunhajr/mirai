import React from 'react';
import { useStoryStore } from '../store/useStoryStore';
import type { Genre } from '../types';
import { 
  Wand2, 
  Rocket, 
  Search, 
  Skull, 
  Sword, 
  Compass, 
  Laugh, 
  Heart, 
  Drama, 
  Zap 
} from 'lucide-react';

const genres: { id: Genre; icon: React.ReactNode; label: string }[] = [
  { id: 'action', icon: <Sword size={32} />, label: 'Action' },
  { id: 'adventure', icon: <Compass size={32} />, label: 'Adventure' },
  { id: 'comedy', icon: <Laugh size={32} />, label: 'Comedy' },
  { id: 'drama', icon: <Drama size={32} />, label: 'Drama' },
  { id: 'fantasy', icon: <Wand2 size={32} />, label: 'Fantasy' },
  { id: 'horror', icon: <Skull size={32} />, label: 'Horror' },
  { id: 'mystery', icon: <Search size={32} />, label: 'Mystery' },
  { id: 'romance', icon: <Heart size={32} />, label: 'Romance' },
  { id: 'science fiction', icon: <Rocket size={32} />, label: 'Science Fiction' },
  { id: 'thriller', icon: <Zap size={32} />, label: 'Thriller' }
];

export const GenreSelector: React.FC = () => {
  const { createStory, error } = useStoryStore();

  const handleGenreSelect = async (genre: Genre) => {
    try {
      await createStory(genre);
    } catch (error) {
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
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 max-w-6xl mx-auto p-4">
      {genres.map((genre) => (
        <button
          key={genre.id}
          onClick={() => handleGenreSelect(genre.id)}
          className="flex flex-col items-center justify-center p-6 bg-gray-800 rounded-lg hover:bg-gray-700 transition duration-300"
        >
          <div className="text-red-600 mb-3">{genre.icon}</div>
          <span className="text-white font-medium">{genre.label}</span>
        </button>
      ))}
    </div>
  );
};
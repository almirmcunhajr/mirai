import React from 'react';
import { useStoryStore } from '../store/useStoryStore';
import { Play } from 'lucide-react';

export const StoryList: React.FC = () => {
  const { stories, loadStory } = useStoryStore();

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
      {stories.map((story) => (
        <div
          key={story.id}
          className="relative group cursor-pointer"
          onClick={() => loadStory(story.id)}
        >
          <img
            src={story.thumbnail}
            alt={story.title}
            className="w-full aspect-video object-cover rounded-lg"
          />
          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-60 transition-all duration-300 flex items-center justify-center rounded-lg">
            <Play
              size={48}
              className="text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            />
          </div>
          <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black to-transparent">
            <h3 className="text-white font-medium">{story.title}</h3>
            <p className="text-gray-300 text-sm capitalize">{story.genre}</p>
          </div>
        </div>
      ))}
    </div>
  );
};
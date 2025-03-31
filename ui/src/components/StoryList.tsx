import React from 'react';
import { useStoryStore } from '../store/useStoryStore';
import { Play, PlusCircle } from 'lucide-react';

export const StoryList: React.FC = () => {
  const { stories, loadStory, storyNodes, setCurrentView } = useStoryStore();

  const getStoryThumbnail = (story: any): string | undefined => {
    const currentNode = storyNodes[story.currentNode];
    const thumbnailUrl = currentNode?.thumbnail_url;
    return thumbnailUrl || 'https://placehold.co/600x400/1a1a1a/ffffff?text=No+Thumbnail';
  };

  if (stories.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] p-4">
        <p className="text-gray-400 text-lg mb-6">No stories yet. Start your first adventure!</p>
        <button
          onClick={() => setCurrentView('create')}
          className="flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
        >
          <PlusCircle size={24} />
          <span>Create New Story</span>
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
      {stories.map((story) => {
        const thumbnail = getStoryThumbnail(story);
        return (
          <div
            key={story.id}
            className="relative group cursor-pointer"
            onClick={() => loadStory(story.id)}
          >
            <div className="w-full aspect-video bg-gray-800 rounded-lg overflow-hidden">
              <img
                src={thumbnail}
                alt={story.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                }}
              />
            </div>
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
        );
      })}
    </div>
  );
};
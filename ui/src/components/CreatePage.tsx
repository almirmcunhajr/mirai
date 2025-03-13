import React from 'react';
import { GenreSelector } from './GenreSelector';

export const CreatePage: React.FC = () => {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold text-white mb-2">Create New Story</h2>
      <p className="text-gray-400 mb-8">Select a genre to begin your new adventure</p>
      <GenreSelector />
    </div>
  );
};
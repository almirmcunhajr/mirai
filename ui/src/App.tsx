import React from 'react';
import { Sidebar } from './components/Sidebar';
import { HomePage } from './components/HomePage';
import { CreatePage } from './components/CreatePage';
import { StoryPlayer } from './components/StoryPlayer';
import { useStoryStore } from './store/useStoryStore';

function App() {
  const { currentView } = useStoryStore();

  return (
    <div className="min-h-screen bg-gray-900">
      <Sidebar />
      
      <main className="ml-16 md:ml-64">
        {currentView === 'home' && <HomePage />}
        {currentView === 'create' && <CreatePage />}
        {currentView === 'player' && <StoryPlayer />}
      </main>
    </div>
  );
}

export default App;
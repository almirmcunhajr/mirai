import React from 'react';
import { Home, PlusCircle, LogOut, User } from 'lucide-react';
import { useStoryStore } from '../store/useStoryStore';
import { useAuthStore } from '../store/useAuthStore';

export const Sidebar: React.FC = () => {
  const { setCurrentView } = useStoryStore();
  const { user, logout } = useAuthStore();

  if (!user) {
    return null;
  }

  return (
    <div className="fixed left-0 top-0 h-screen w-16 md:w-64 bg-black flex flex-col">
      <div className="p-4 md:p-6">
        <h1 className="text-red-600 font-bold text-xl hidden md:block">Mir.ai</h1>
      </div>
      
      <nav className="flex-1 px-2">
        <button
          onClick={() => setCurrentView('home')}
          className="w-full flex items-center gap-4 p-3 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
        >
          <Home size={24} />
          <span className="hidden md:block">Home</span>
        </button>
        
        <button
          onClick={() => setCurrentView('create')}
          className="w-full flex items-center gap-4 p-3 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors mt-2"
        >
          <PlusCircle size={24} />
          <span className="hidden md:block">Create New Story</span>
        </button>
      </nav>

      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-4 p-3 text-gray-400">
          <User size={24} />
          <div className="hidden md:block">
            <p className="text-white font-medium">{user.name}</p>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </div>
        
        <button
          onClick={logout}
          className="w-full flex items-center gap-4 p-3 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors mt-2"
        >
          <LogOut size={24} />
          <span className="hidden md:block">Logout</span>
        </button>
      </div>
    </div>
  );
};
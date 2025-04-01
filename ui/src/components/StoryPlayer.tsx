import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, Volume2, VolumeX, Split, Menu, Home, PlusCircle } from 'lucide-react';
import { useStoryStore } from '../store/useStoryStore';
import { ApiService } from '../services/api';
import { StoryTree } from './StoryTree';
import clsx from 'clsx';

const api = ApiService.getInstance();

export const StoryPlayer: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [showTree, setShowTree] = React.useState(false);
  const [showSidebar, setShowSidebar] = React.useState(false);
  const [showControls, setShowControls] = React.useState(true);
  const [userDecision, setUserDecision] = useState('');
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const controlsTimeoutRef = useRef<NodeJS.Timeout>();
  const {
    isPlaying,
    volume,
    currentStory,
    showDecisions,
    currentVideoTime,
    videoDuration,
    isLoading,
    error,
    setPlaying,
    setVolume,
    closeStory,
    getCurrentNode,
    setVideoProgress,
    makeDecision,
    storyNodes,
    navigateToNode,
    setCurrentView,
    setShowDecisions
  } = useStoryStore();

  const currentNode = getCurrentNode();
  
  useEffect(() => {
    const loadVideo = async () => {
      if (!currentNode?.videoUrl || !currentStory) return;
      try {
        setVideoUrl(null); // Clear previous video URL
        const url = await api.getVideoUrl(currentStory.id, currentNode.id);
        setVideoUrl(url);
        
        // Wait for video to be ready before playing
        if (videoRef.current) {
          videoRef.current.onloadeddata = () => {
            setPlaying(true);
            videoRef.current?.play();
          };
        }
      } catch (error) {
        console.error('Failed to load video:', error);
        // You might want to show an error message to the user here
      }
    };

    loadVideo();

    return () => {
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [currentNode, currentStory]);

  useEffect(() => {
    // Request fullscreen on mount
    document.documentElement.requestFullscreen().catch(() => {
      console.log('Fullscreen request failed');
    });

    return () => {
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {
          console.log('Exit fullscreen failed');
        });
      }
    };
  }, []);

  useEffect(() => {
    const handleMouseMove = () => {
      setShowControls(true);
      
      if (controlsTimeoutRef.current) {
        clearTimeout(controlsTimeoutRef.current);
      }
      
      controlsTimeoutRef.current = setTimeout(() => {
        if (!showTree) { // Don't hide controls if tree is shown
          setShowControls(false);
        }
      }, 3000);
    };

    document.addEventListener('mousemove', handleMouseMove);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      if (controlsTimeoutRef.current) {
        clearTimeout(controlsTimeoutRef.current);
      }
    };
  }, [showTree]);

  useEffect(() => {
    if (!videoRef.current) return;
    
    if (isPlaying) {
      videoRef.current.play();
    } else {
      videoRef.current.pause();
    }
  }, [isPlaying]);

  useEffect(() => {
    if (!videoRef.current) return;
    videoRef.current.volume = volume;
  }, [volume]);

  if (!currentStory) return null;

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    setVideoProgress(
      videoRef.current.currentTime,
      videoRef.current.duration
    );
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!videoRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    const newTime = pos * videoDuration;
    videoRef.current.currentTime = newTime;
    setVideoProgress(newTime, videoDuration);
  };

  const handleDecision = async () => {
    if (!userDecision.trim()) {
      return;
    }

    try {
      // Create a new branch with the user's decision
      await makeDecision(userDecision.trim());
      setUserDecision(''); // Clear the input after submission
      setShowDecisions(false); // Hide decisions until video ends
      if (videoRef.current) {
        videoRef.current.currentTime = 0;
        videoRef.current.onloadeddata = () => {
          setPlaying(true);
          videoRef.current?.play();
        };
      }
    } catch (error) {
      // Error is handled by the store
      console.error('Failed to make decision:', error);
    }
  };

  const handleNodeClick = (nodeId: string) => {
    navigateToNode(nodeId);
    setVideoProgress(0, videoDuration); // Reset progress to 0
    if (videoRef.current) {
      videoRef.current.currentTime = 0; // Reset video time to beginning
      
      // Wait for video to be ready before playing
      videoRef.current.onloadeddata = () => {
        setPlaying(true);
        videoRef.current?.play();
      };
    }
    setShowTree(false); // Close the tree modal
  };

  return (
    <div className="fixed inset-0 bg-black">
      {videoUrl && (
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full object-contain"
          onTimeUpdate={handleTimeUpdate}
          onEnded={() => setPlaying(false)}
          onError={(e) => {
            console.error('Video error:', e);
            // You might want to show an error message to the user here
          }}
          crossOrigin="anonymous"
        />
      )}

      {/* Sidebar with Toggle Button */}
      <div className={clsx(
        "fixed inset-y-0 left-0 transition-transform duration-300 z-40",
        showSidebar ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="relative h-full">
          {/* Sidebar Content */}
          <div className="h-full w-16 md:w-64 bg-black/95 border-r border-gray-800">
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
          </div>

          {/* Toggle Button */}
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className={clsx(
              "absolute top-4 right-0 translate-x-full",
              "p-2 hover:bg-black/30 rounded-full transition text-white/80 hover:text-white",
              !showControls && "opacity-0"
            )}
          >
            <Menu size={24} />
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="absolute inset-0 bg-black flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white mx-auto mb-4"></div>
            <h2 className="text-xl font-semibold text-white mb-2">Creating Your Story</h2>
            <p className="text-gray-400">Please wait while we generate your unique adventure...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="text-red-500 text-center">
            <p className="text-xl font-semibold mb-2">Error</p>
            <p>{error}</p>
          </div>
        </div>
      )}

      {showDecisions && !isLoading && !error && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-gray-900 p-6 rounded-lg max-w-lg w-full mx-4">
            <h3 className="text-white text-xl font-semibold mb-4">What will you do?</h3>
            <div className="space-y-3">
              <input
                type="text"
                value={userDecision}
                onChange={(e) => setUserDecision(e.target.value)}
                placeholder="Enter your decision..."
                className="w-full p-3 text-white bg-gray-800 rounded-lg border border-gray-700 focus:outline-none focus:border-red-500"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleDecision();
                  }
                }}
              />
              <button
                onClick={handleDecision}
                disabled={isLoading || !userDecision.trim()}
                className={clsx(
                  "w-full p-3 text-white rounded-lg transition",
                  isLoading || !userDecision.trim()
                    ? "bg-gray-600 cursor-not-allowed"
                    : "bg-red-600 hover:bg-red-700"
                )}
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Video Controls */}
      <div className={clsx(
        "fixed bottom-0 left-0 right-0 transition-opacity duration-300",
        "bg-gradient-to-t from-black/40 to-transparent",
        !showControls && "opacity-0",
        "text-white p-4"
      )}>
        <div className="max-w-7xl mx-auto">
          <div
            className="w-full h-1 bg-gray-600/50 rounded-full mb-4 cursor-pointer"
            onClick={handleProgressClick}
          >
            <div 
              className="h-full bg-red-600 rounded-full" 
              style={{ width: `${(currentVideoTime / videoDuration) * 100}%` }}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setPlaying(!isPlaying)}
                className="p-2 hover:bg-black/30 rounded-full transition"
              >
                {isPlaying ? <Pause size={24} /> : <Play size={24} />}
              </button>

              <button
                onClick={() => setShowTree(!showTree)}
                className="p-2 hover:bg-black/30 rounded-full transition"
              >
                <Split size={20} className="rotate-90" />
              </button>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setVolume(volume === 0 ? 1 : 0)}
                  className="p-2 hover:bg-black/30 rounded-full transition"
                >
                  {volume === 0 ? <VolumeX size={24} /> : <Volume2 size={24} />}
                </button>
                
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={(e) => setVolume(parseFloat(e.target.value))}
                  className="w-24 accent-red-600"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Story Tree Modal */}
      {showTree && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-gray-900 rounded-lg w-1/2 h-[60vh] overflow-hidden">
            <div className="p-6 h-full flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-white">Story Tree</h2>
                <button
                  onClick={() => setShowTree(false)}
                  className="p-2 hover:bg-gray-800 rounded-full transition text-white"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
              <div className="flex-1 overflow-hidden flex items-center justify-center">
                <StoryTree
                  nodes={storyNodes}
                  currentNodeId={currentStory.currentNode}
                  onNodeClick={handleNodeClick}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
import React, { useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, ChevronUp } from 'lucide-react';
import { useStoryStore } from '../store/useStoryStore';
import { ApiService } from '../services/api';
import { StoryTree } from './StoryTree';
import clsx from 'clsx';

const api = ApiService.getInstance();

export const StoryPlayer: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [showTree, setShowTree] = React.useState(false);
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
    navigateToNode
  } = useStoryStore();

  const currentNode = getCurrentNode();
  
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

  if (!currentStory || !currentNode) return null;

  const videoUrl = currentNode.videoUrl;
  console.log('Current Story:', currentStory);
  console.log('Current Node:', currentNode);
  console.log('Video URL:', videoUrl);
  console.log('Decisions:', currentNode.decisions);

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
    videoRef.current.currentTime = pos * videoRef.current.duration;
  };

  const handleDecision = async (nextNode: string) => {
    try {
      await makeDecision(nextNode);
    } catch (error) {
      // Error is handled by the store
      console.error('Failed to make decision:', error);
    }
  };

  const handleNodeClick = (nodeId: string) => {
    navigateToNode(nodeId);
  };

  return (
    <div className="fixed inset-0 bg-black">
      <video
        ref={videoRef}
        src={videoUrl}
        className="w-full h-full object-contain"
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setPlaying(false)}
      />

      {isLoading && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
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
              {currentNode.decisions.map((decision) => (
                <button
                  key={decision.id}
                  onClick={() => handleDecision(decision.targetNodeId)}
                  disabled={isLoading}
                  className={clsx(
                    "w-full p-3 text-white rounded-lg transition",
                    isLoading
                      ? "bg-gray-600 cursor-not-allowed"
                      : "bg-red-600 hover:bg-red-700"
                  )}
                >
                  {decision.text}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-95 text-white p-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div className="w-10" /> {/* Spacer for balance */}
            <button
              onClick={() => setShowTree(!showTree)}
              className="flex items-center gap-1 p-2 hover:bg-gray-700 rounded-lg transition"
            >
              <ChevronUp size={20} />
            </button>
          </div>

          {showTree && (
            <div className="mb-4 overflow-x-auto">
              <StoryTree
                nodes={storyNodes}
                currentNodeId={currentStory.currentNode}
                onNodeClick={handleNodeClick}
              />
            </div>
          )}
          <div
            className="w-full h-1 bg-gray-600 rounded-full mb-4 cursor-pointer"
            onClick={handleProgressClick}
          >
            <div 
              className="h-full bg-red-600 rounded-full" 
              style={{ width: `${(currentVideoTime / videoDuration) * 100}%` }}
            />
          </div>
          
          <div className="flex items-center gap-4">
            <button
              onClick={() => setPlaying(!isPlaying)}
              className="p-2 hover:bg-gray-700 rounded-full transition"
            >
              {isPlaying ? <Pause size={24} /> : <Play size={24} />}
            </button>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => setVolume(volume === 0 ? 1 : 0)}
                className="p-2 hover:bg-gray-700 rounded-full transition"
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
                className="w-24"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
import React from 'react';
import { StoryNode } from '../types';
import clsx from 'clsx';

interface StoryTreeProps {
  nodes: Record<string, StoryNode>;
  currentNodeId: string;
  onNodeClick: (nodeId: string) => void;
}

export const StoryTree: React.FC<StoryTreeProps> = ({ nodes, currentNodeId, onNodeClick }) => {
  const renderNode = (nodeId: string, level: number = 0): React.ReactNode => {
    const node = nodes[nodeId];
    if (!node) return null;

    const isCurrentNode = nodeId === currentNodeId;
    const hasChildren = node.children.length > 0;

    return (
      <div key={nodeId} className="relative">
        <div className="flex items-center">
          {/* Vertical line from parent */}
          {level > 0 && (
            <div className="absolute left-0 top-0 bottom-1/2 w-px bg-gray-600" />
          )}
          
          {/* Horizontal line to parent */}
          {level > 0 && (
            <div className="absolute left-0 top-1/2 w-4 h-px bg-gray-600" />
          )}
          
          {/* Node content */}
          <button
            onClick={() => onNodeClick(nodeId)}
            className={clsx(
              "px-3 py-1 rounded text-sm transition",
              isCurrentNode
                ? "bg-red-600 text-white"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            )}
          >
            {node.content.substring(0, 30)}...
          </button>
        </div>

        {/* Children */}
        {hasChildren && (
          <div className="flex gap-8 mt-4">
            {node.children.map((child, index) => (
              <div key={child.id} className="relative">
                {/* Vertical line to children */}
                <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-600" />
                {/* Horizontal line to each child */}
                <div className="absolute left-1/2 top-0 w-4 h-px bg-gray-600" />
                {renderNode(child.id, level + 1)}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // Find root node (node without parent)
  const rootNodeId = Object.values(nodes).find(node => !node.parentId)?.id;
  if (!rootNodeId) return null;

  return (
    <div className="p-4 bg-gray-900 rounded-lg">
      <h3 className="text-white text-lg font-semibold mb-4">Story Tree</h3>
      <div className="flex justify-center">
        {renderNode(rootNodeId)}
      </div>
    </div>
  );
}; 
import React from 'react';
import Tree from 'react-d3-tree';
import { StoryNode } from '../types';

interface StoryTreeProps {
  nodes: Record<string, StoryNode>;
  currentNodeId: string;
  onNodeClick: (nodeId: string) => void;
}

export const StoryTree: React.FC<StoryTreeProps> = ({ nodes, currentNodeId, onNodeClick }) => {
  // Convert our nodes structure to D3 tree format
  const convertToD3Tree = (nodeId: string): any => {
    const node = nodes[nodeId];
    if (!node) return null;

    const isCurrentNode = nodeId === currentNodeId;

    // Find the decision text from parent node's decision
    let decisionText = node.decision || 'Start';

    return {
      name: '',  // We'll render text in the custom node component
      id: nodeId,
      attributes: {
        isCurrentNode,
        text: decisionText
      },
      children: node.children.map(child => convertToD3Tree(child.id)).filter(Boolean)
    };
  };

  // Find root node (node without parent)
  const rootNodeId = Object.values(nodes).find(node => !node.parentId)?.id;
  if (!rootNodeId) return null;

  const treeData = convertToD3Tree(rootNodeId);

  // Custom node component
  const renderCustomNode = ({ nodeDatum, toggleNode }: any) => (
    <g>
      <circle
        r={15}
        fill={nodeDatum.attributes.isCurrentNode ? '#dc2626' : '#1f2937'}
        onClick={() => onNodeClick(nodeDatum.id)}
      />
      <text
        fill="white"
        x={20}
        dy="0.31em"
        fontSize={12}
        textAnchor="start"
        style={{ 
          pointerEvents: 'none',
          fill: 'white',
          stroke: 'none'
        }}
      >
        {nodeDatum.attributes.text}
      </text>
    </g>
  );

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <style>
        {`
          .rd3t-link {
            stroke: white !important;
          }
          .rd3t-tree-container {
            fill: white !important;
            color: white !important;
          }
          .rd3t-label {
            fill: white !important;
            color: white !important;
          }
          text {
            fill: white !important;
            color: white !important;
          }
          g text {
            fill: white !important;
            color: white !important;
          }
          .rd3t-label-text {
            fill: white !important;
            color: white !important;
          }
          .node__root text,
          .node__branch text,
          .node__leaf text {
            fill: white !important;
            color: white !important;
          }
        `}
      </style>
      <Tree
        data={treeData}
        orientation="vertical"
        renderCustomNodeElement={renderCustomNode}
        pathFunc="step"
        separation={{ siblings: 2, nonSiblings: 2 }}
        translate={{ x: 400, y: 80 }}
        nodeSize={{ x: 200, y: 100 }}
        rootNodeClassName="node__root"
        branchNodeClassName="node__branch"
        leafNodeClassName="node__leaf"
        centeringTransitionDuration={200}
      />
    </div>
  );
}; 
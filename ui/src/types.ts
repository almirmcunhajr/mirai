export type Genre = 
  | 'action'
  | 'adventure'
  | 'comedy'
  | 'drama'
  | 'fantasy'
  | 'horror'
  | 'mystery'
  | 'romance'
  | 'science fiction'
  | 'thriller';

export interface Story {
  id: string;
  title: string;
  genre: Genre;
  currentNode: string;
  lastPlayedAt: Date;
  root_node_id: string;
}

export interface StoryNode {
  id: string;
  content: string;
  videoUrl: string;
  thumbnail_url: string;
  decision?: string;
  parentId: string | null;
  children: StoryNode[];
}

export interface Decision {
  id: string;
  text: string;
  targetNodeId: string;
}

export interface StoryContent {
  [key: string]: {
    videoUrl: string;
    decisions: {
      text: string;
      nextNode: string;
    }[];
  };
}
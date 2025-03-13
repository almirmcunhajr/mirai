export type Genre = 'fantasy' | 'sci-fi' | 'mystery' | 'horror';

export interface Story {
  id: string;
  title: string;
  genre: Genre;
  currentNode: string;
  lastPlayedAt: Date;
  thumbnail: string;
}

export interface StoryNode {
  id: string;
  content: string;
  videoUrl: string;
  decisions: Decision[];
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
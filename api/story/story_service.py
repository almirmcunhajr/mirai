import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from script.script_service import ScriptService
from script.script import PathNode
from audiovisual.audiovisual_service import AudioVisualService
from story.story import Story, StoryNode
from story.story_repository import StoryRepository
from story.exceptions import StoryGenerationError, BranchCreationError, StoryNotFoundError
from common.genre import Genre
from config import get_video_url, get_video_path

class StoryService:
    def __init__(self, script_service: ScriptService, audiovisual_service: AudioVisualService):
        self.script_service = script_service
        self.audiovisual_service = audiovisual_service
        self.repository = StoryRepository()
        self.logger = logging.getLogger(__name__)

    async def create_story(self, genre: Genre, language_code: str = "pt-BR") -> Story:
        """
        Creates a new story with an initial branch.
        
        Args:
            genre (Genre): The genre of the story
            language_code (str): The language code for the story
            
        Returns:
            Story: The created story with its initial branch
            
        Raises:
            StoryGenerationError: If story generation fails
        """
        try:
            # Generate initial script
            script = self.script_service.generate(genre=genre, language_code=language_code)
            
            # Create root node
            root_node = StoryNode(script=script)
            
            # Create story
            story = Story(
                title=script.title,
                genre=genre,
                root_node_id=root_node.id,
                nodes=[root_node]
            )
            
            # Generate video for the initial branch
            self._generate_video_for_node(story, root_node)
            
            # Save to database
            return await self.repository.create(story)
        except Exception as e:
            self.logger.error(f"Failed to create story: {str(e)}", exc_info=True)
            raise StoryGenerationError(str(e))

    async def create_branch(self, story_id: UUID, parent_node_id: UUID, decision: str, language_code: str = "pt-BR") -> Story:
        """
        Creates a new branch in the story tree based on a decision.
        
        Args:
            story_id (UUID): The story ID
            parent_node_id (UUID): ID of the parent node
            decision (str): The decision that leads to this branch
            language_code (str): The language code for the new branch
            
        Returns:
            Story: The updated story with the new branch
            
        Raises:
            StoryNotFoundError: If the story is not found
            BranchCreationError: If branch creation fails
        """
        try:
            # Get story from database
            story = await self.repository.get_by_id(story_id)
            if not story:
                raise StoryNotFoundError(f"Story with ID {story_id} not found")
            
            # Find parent node
            parent_node = next((node for node in story.nodes if node.id == parent_node_id), None)
            if not parent_node:
                raise ValueError(f"Parent node with ID {parent_node_id} not found")
            
            # Generate new script based on the decision
            path = self._get_path_to_node(story, parent_node_id)
            script = self.script_service.generate(
                genre=story.genre,
                language_code=language_code,
                path=path
            )
            
            # Create new node
            new_node = StoryNode(
                script=script,
                decision=decision,
                parent_id=parent_node_id
            )
            
            # Update parent node
            parent_node.children.append(new_node.id)
            
            # Add new node to story
            story.nodes.append(new_node)
            story.updated_at = datetime.utcnow()
            
            # Generate video for the new branch
            self._generate_video_for_node(story, new_node)
            
            # Update in database
            result = await self.repository.update(story)
            if not result:
                raise StoryNotFoundError(f"Story with ID {story_id} not found")
            return result
        except StoryNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to create branch: {str(e)}", exc_info=True)
            raise BranchCreationError(str(e))

    async def get_story(self, story_id: UUID) -> Story:
        """
        Gets the story.
        
        Args:
            story_id (UUID): The story ID
            
        Returns:
            Story: The story object
            
        Raises:
            StoryNotFoundError: If the story is not found
        """
        story = await self.repository.get_by_id(story_id)
        if not story:
            raise StoryNotFoundError(f"Story with ID {story_id} not found")
        return story

    async def list_stories(self) -> List[Story]:
        """
        Lists all stories.
        
        Returns:
            List[Story]: List of stories
        """
        return await self.repository.list_stories()

    async def delete_story(self, story_id: UUID) -> bool:
        """
        Deletes a story.
        
        Args:
            story_id (UUID): The story ID
            
        Returns:
            bool: True if deleted
            
        Raises:
            StoryNotFoundError: If the story is not found
        """
        success = await self.repository.delete(story_id)
        if not success:
            raise StoryNotFoundError(f"Story with ID {story_id} not found")
        return True

    def _generate_video_for_node(self, story: Story, node: StoryNode) -> None:
        """
        Generates a video for a story node and updates its video_url.
        
        Args:
            story (Story): The story containing the node
            node (StoryNode): The node to generate video for
            
        Raises:
            VideoGenerationError: If video generation fails
        """
        try:
            # Get video path
            video_path = get_video_path(str(story.id), str(node.id))
            self.logger.info(f"Generating video for node {node.id} at path {video_path}")
            
            # Generate video
            self.audiovisual_service.generate_video(
                script=node.script,
                output_path=str(video_path)
            )
            
            # Set video URL
            node.video_url = get_video_url(str(story.id), str(node.id))
            story.updated_at = datetime.utcnow()
            self.logger.info(f"Successfully generated video for node {node.id}")
                
        except Exception as e:
            self.logger.error(f"Error generating video for node {node.id}: {str(e)}", exc_info=True)
            raise e

    def _get_path_to_node(self, story: Story, node_id: UUID) -> List[PathNode]:
        """
        Gets the path from root to a specific node, including scripts and decisions.
        
        Args:
            story (Story): The story to get the path from
            node_id (UUID): ID of the target node
            
        Returns:
            List[PathNode]: List of script-decision pairs representing the path
        """
        path = []
        current_id = node_id
        
        while current_id:
            node = next((n for n in story.nodes if n.id == current_id), None)
            if not node:
                break

            path_node = PathNode(
                script=node.script,
            )
            if node.decision:
                path_node.decision = node.decision
            path.insert(0, path_node)
                
            current_id = node.parent_id
            
        return path 
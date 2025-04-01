import logging
from typing import List
import copy
from uuid import UUID
from datetime import datetime, timezone

from script.script_service import ScriptService
from audiovisual.audiovisual_service import AudioVisualService
from story.story import Story, StoryNode, Style, PathNode
from story.story_repository import StoryRepository
from story.exceptions import StoryGenerationError, BranchCreationError, StoryNotFoundError
from common.genre import Genre
from config import get_video_url, get_video_path
from ttt.ttt import Chat

class StoryService:
    def __init__(self, script_service: ScriptService, audiovisual_service: AudioVisualService):
        self.script_service = script_service
        self.audiovisual_service = audiovisual_service
        self.repository = StoryRepository()
        self.logger = logging.getLogger(__name__)

    async def create_story(self, genre: Genre, language_code: str, style: Style, user_id: str) -> Story:
        try:
            chat = Chat()
            script, subjects = await self.script_service.generate(chat=chat, genre=genre, language_code=language_code)

            root_node = StoryNode(script=script, chat=chat, subjects=subjects)
            story = Story(
                title=script.title,
                genre=genre,
                style=style,
                language=language_code,
                root_node_id=root_node.id,
                nodes=[root_node],
                user_id=user_id
            )

            await self._generate_video_for_node(story, root_node)
            
            return await self.repository.create(story)
        except Exception as e:
            self.logger.error(f"Failed to create story: {str(e)}", exc_info=True)
            raise StoryGenerationError(str(e))

    async def create_branch(self, story_id: UUID, parent_node_id: UUID, decision: str, user_id: str) -> Story:
        try:
            story = await self.repository.find_by_id(story_id, user_id)
            if not story:
                raise StoryNotFoundError(f"Story with ID {story_id} not found")
            
            parent_node = next((node for node in story.nodes if node.id == parent_node_id), None)
            if not parent_node:
                raise ValueError(f"Parent node with ID {parent_node_id} not found")
            
            chat = copy.deepcopy(parent_node.chat)
            script, subjects = await self.script_service.generate(
                chat=chat,
                genre=story.genre,
                language_code=story.language,
                decision=decision,
                subjects=parent_node.subjects,
            )
            
            new_node = StoryNode(
                script=script,
                decision=decision,
                parent_id=parent_node_id,
                chat=chat,
                subjects=subjects,
            )

            parent_node.children.append(new_node.id)

            story.nodes.append(new_node)
            story.updated_at = datetime.now(timezone.utc)
            
            await self._generate_video_for_node(story, new_node)
            
            return await self.repository.update(story)
        except StoryNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to create branch: {str(e)}", exc_info=True)
            raise BranchCreationError(str(e))

    async def get_story(self, story_id: UUID, user_id: str) -> Story:
        story = await self.repository.find_by_id(story_id, user_id)
        if not story:
            raise StoryNotFoundError(f"Story with ID {story_id} not found")
        return story

    async def list_stories(self, user_id: str) -> List[Story]:
        return await self.repository.find_all_by_user(user_id)

    async def delete_story(self, story_id: UUID, user_id: str) -> bool:
        success = await self.repository.delete(story_id, user_id)
        if not success:
            raise StoryNotFoundError(f"Story with ID {story_id} not found")
        return True

    async def _generate_video_for_node(self, story: Story, node: StoryNode) -> None:
        try:
            video_path = get_video_path(str(story.id), str(node.id))

            self.logger.info(f"Generating video for node {node.id} at path {video_path}")
            await self.audiovisual_service.generate_video(
                story_node=node,
                style=story.style,
                output_path=str(video_path)
            )
            
            node.video_url = get_video_url(str(story.id), str(node.id))
            story.updated_at = datetime.now(timezone.utc)
            
            self.logger.info(f"Successfully generated video for node {node.id}")
        except Exception as e:
            self.logger.error(f"Error generating video for node {node.id}: {str(e)}", exc_info=True)
            raise e

    def _get_path_to_node(self, story: Story, node_id: UUID) -> List[PathNode]:
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
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
import os

from story.story_service import StoryService
from story.story import Story
from story.exceptions import StoryNotFoundError, BranchCreationError
from common.genre import Genre
from visual.visual_service import VisualService
from audio.audio_service import AudioService

router = APIRouter(prefix="/stories", tags=["stories"])

class CreateStoryRequest(BaseModel):
    genre: Genre
    language_code: Optional[str] = "en"

class CreateBranchRequest(BaseModel):
    parent_node_id: UUID
    decision: str
    language_code: Optional[str] = "en"

def get_story_service() -> StoryService:
    # TODO: Get these from dependency injection
    from script.script_service import ScriptService
    from audiovisual.audiovisual_service import AudioVisualService
    from facade.chatgpt import ChatGPT
    from facade.dalle import DALLE
    from facade.openai_tts import OpenAITTS
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key not configured")
    
    chatbot = ChatGPT(api_key=openai_api_key)
    dalle = DALLE(api_key=openai_api_key)
    tts = OpenAITTS(api_key=openai_api_key)
    
    script_service = ScriptService(chatbot)
    visual_service = VisualService(dalle)
    audio_service = AudioService(tts)
    audiovisual_service = AudioVisualService(visual_service, audio_service)
    
    return StoryService(script_service, audiovisual_service)

@router.post("")
async def create_story(
    request: CreateStoryRequest,
    story_service: StoryService = Depends(get_story_service)
) -> Story:
    """
    Creates a new story with an initial branch.
    """
    return await story_service.create_story(
        genre=request.genre,
        language_code=request.language_code
    )

@router.post("/{story_id}/branches")
async def create_branch(
    story_id: UUID,
    request: CreateBranchRequest,
    story_service: StoryService = Depends(get_story_service)
) -> Story:
    """
    Creates a new branch in an existing story.
    """
    try:
        return await story_service.create_branch(
            story_id=story_id,
            parent_node_id=request.parent_node_id,
            decision=request.decision,
            language_code=request.language_code
        )
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BranchCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{story_id}/tree")
async def get_story_tree(
    story_id: UUID,
    story_service: StoryService = Depends(get_story_service)
) -> dict:
    """
    Gets the story tree structure for frontend consumption.
    """
    try:
        return await story_service.get_story_tree(story_id)
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("")
async def list_stories(
    story_service: StoryService = Depends(get_story_service)
) -> List[Story]:
    """
    Lists all stories.
    """
    return await story_service.list_stories()

@router.delete("/{story_id}")
async def delete_story(
    story_id: UUID,
    story_service: StoryService = Depends(get_story_service)
) -> bool:
    """
    Deletes a story.
    """
    try:
        return await story_service.delete_story(story_id)
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) 
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from story.story_service import StoryService
from story.story import Story
from story.exceptions import StoryNotFoundError, BranchCreationError
from story.story import Style
from common.genre import Genre
from dependencies import get_story_service, get_current_user
from utils.utils import validate_language

router = APIRouter(prefix="/stories", tags=["stories"])

class CreateStoryRequest(BaseModel):
    genre: Genre
    language_code: Optional[str] = "pt-BR"
    style: Optional[Style] = "anime"

class CreateBranchRequest(BaseModel):
    parent_node_id: UUID
    decision: str

@router.post("")
async def create_story(
    request: CreateStoryRequest,
    story_service: StoryService = Depends(get_story_service),
    current_user = Depends(get_current_user)
) -> Story:
    validate_language(request.language_code)
    if not request.language_code:
        raise HTTPException(status_code=400, detail="Invalid language code")
    story = await story_service.create_story(
        genre=request.genre,
        language_code=request.language_code,
        style=request.style,
        user_id=current_user.id
    )
    return story.model_dump()

@router.post("/{story_id}/branches")
async def create_branch(
    story_id: UUID,
    request: CreateBranchRequest,
    story_service: StoryService = Depends(get_story_service),
    current_user = Depends(get_current_user)
) -> Story:
    try:
        story = await story_service.create_branch(
            story_id=story_id,
            parent_node_id=request.parent_node_id,
            decision=request.decision,
            user_id=current_user.id
        )
        return story.model_dump()
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BranchCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{story_id}")
async def get_story(
    story_id: UUID,
    story_service: StoryService = Depends(get_story_service),
    current_user = Depends(get_current_user)
) -> dict:
    try:
        story = await story_service.get_story(story_id, current_user.id)
        return story.model_dump()
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{story_id}/tree")
async def get_story_tree(
    story_id: UUID,
    story_service: StoryService = Depends(get_story_service),
    current_user = Depends(get_current_user)
) -> dict:
    try:
        return await story_service.get_story_tree(story_id, current_user.id)
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("")
async def list_stories(
    story_service: StoryService = Depends(get_story_service),
    current_user = Depends(get_current_user)
) -> List[Story]:
    stories = await story_service.list_stories(current_user.id)
    return [story.model_dump() for story in stories]

@router.delete("/{story_id}")
async def delete_story(
    story_id: UUID,
    story_service: StoryService = Depends(get_story_service),
    current_user = Depends(get_current_user)
) -> bool:
    try:
        return await story_service.delete_story(story_id, current_user.id)
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) 
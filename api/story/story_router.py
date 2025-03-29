from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from uuid import UUID

from story.story_service import StoryService
from story.story import Story
from story.exceptions import StoryNotFoundError, BranchCreationError
from story.story import Style
from common.genre import Genre
from common.base_model_no_extra import BaseModelNoExtra
from dependencies import get_story_service

router = APIRouter(prefix="/stories", tags=["stories"])

class CreateStoryRequest(BaseModelNoExtra):
    genre: Genre
    language_code: Optional[str] = "pt-BR"
    style: Optional[Style] = "anime"

class CreateBranchRequest(BaseModelNoExtra):
    parent_node_id: UUID
    decision: str

@router.post("")
async def create_story(
    request: CreateStoryRequest,
    story_service: StoryService = Depends(get_story_service)
) -> Story:
    story = await story_service.create_story(
        genre=request.genre,
        language_code=request.language_code,
        style=request.style
    )
    return story.model_dump()

@router.post("/{story_id}/branches")
async def create_branch(
    story_id: UUID,
    request: CreateBranchRequest,
    story_service: StoryService = Depends(get_story_service)
) -> Story:
    try:
        story = await story_service.create_branch(
            story_id=story_id,
            parent_node_id=request.parent_node_id,
            decision=request.decision,
        )
        return story.model_dump()
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BranchCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{story_id}")
async def get_story(
    story_id: UUID,
    story_service: StoryService = Depends(get_story_service)
) -> dict:
    try:
        story = await story_service.get_story(story_id)
        return story.model_dump()
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{story_id}/tree")
async def get_story_tree(
    story_id: UUID,
    story_service: StoryService = Depends(get_story_service)
) -> dict:
    try:
        return await story_service.get_story_tree(story_id)
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("")
async def list_stories(
    story_service: StoryService = Depends(get_story_service)
) -> List[Story]:
    stories = await story_service.list_stories()
    return [story.model_dump() for story in stories]

@router.delete("/{story_id}")
async def delete_story(
    story_id: UUID,
    story_service: StoryService = Depends(get_story_service)
) -> bool:
    try:
        return await story_service.delete_story(story_id)
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) 
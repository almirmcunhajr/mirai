from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from story.story_service import StoryService
from story.story import Story
from story.exceptions import StoryNotFoundError, BranchCreationError
from common.genre import Genre
from dependencies import get_story_service

router = APIRouter(prefix="/stories", tags=["stories"])

class CreateStoryRequest(BaseModel):
    genre: Genre
    language_code: Optional[str] = "pt-BR"

class CreateBranchRequest(BaseModel):
    parent_node_id: UUID
    decision: str
    language_code: Optional[str] = "pt-BR"

@router.post("")
async def create_story(
    request: CreateStoryRequest,
    story_service: StoryService = Depends(get_story_service)
) -> Story:
    """
    Creates a new story with an initial branch.
    """
    story = await story_service.create_story(
        genre=request.genre,
        language_code=request.language_code
    )
    return story.model_dump()

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
        story = await story_service.create_branch(
            story_id=story_id,
            parent_node_id=request.parent_node_id,
            decision=request.decision,
            language_code=request.language_code
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
    """
    Gets the story data.
    """
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
    stories = await story_service.list_stories()
    return [story.model_dump() for story in stories]

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
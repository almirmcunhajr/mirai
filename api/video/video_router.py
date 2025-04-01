from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from fastapi.responses import StreamingResponse

from video.video_service import VideoService
from video.exceptions import VideoNotFoundError
from dependencies import get_video_service, get_current_user
from story.story_service import StoryService
from story.exceptions import StoryNotFoundError
from dependencies import get_story_service

router = APIRouter(prefix="/videos", tags=["videos"])

@router.get("/stories/{story_id}/nodes/{node_id}")
async def stream_story_video(
    story_id: UUID,
    node_id: UUID,
    video_service: VideoService = Depends(get_video_service),
    story_service: StoryService = Depends(get_story_service),
    current_user = Depends(get_current_user)
) -> StreamingResponse:
    try:
        story = await story_service.get_story(story_id, current_user.id)
        if not story:
            raise StoryNotFoundError(f"Story with ID {story_id} not found")
            
        node = next((node for node in story.nodes if node.id == node_id), None)
        if not node:
            raise VideoNotFoundError(f"Node with ID {node_id} not found in story {story_id}")
            
        return video_service.stream_video(str(story_id), str(node_id))
    except StoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except VideoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
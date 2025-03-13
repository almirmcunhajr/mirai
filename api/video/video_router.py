from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from fastapi.responses import StreamingResponse

from video.video_service import VideoService
from video.exceptions import VideoNotFoundError
from dependencies import get_video_service

router = APIRouter(prefix="/videos", tags=["videos"])

@router.get("/stories/{story_id}/nodes/{node_id}")
async def stream_story_video(
    story_id: UUID,
    node_id: UUID,
    video_service: VideoService = Depends(get_video_service)
) -> StreamingResponse:
    """
    Streams a video for a specific story node.
    
    Args:
        story_id (UUID): The story ID
        node_id (UUID): The node ID
        video_service (VideoService): The video service
        
    Returns:
        StreamingResponse: The video stream
    """
    try:
        return video_service.stream_video(str(story_id), str(node_id))
    except VideoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
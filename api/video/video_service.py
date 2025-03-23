import os
from fastapi.responses import StreamingResponse
from typing import Optional

from config import get_video_path
from video.exceptions import VideoNotFoundError

class VideoService:
    def __init__(self, base_dir: str = "output/stories"):
        self.base_dir = base_dir

    def get_video_path(self, story_id: str, node_id: str) -> str:
        return os.path.join(self.base_dir, story_id, node_id, "story.mp4")

    def stream_video(self, story_id: str, node_id: str) -> StreamingResponse:
        video_path = get_video_path(story_id, node_id)
        
        if not video_path.exists():
            raise VideoNotFoundError(f"Video not found for story {story_id}, node {node_id}")
            
        def iterfile():
            with open(video_path, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk
                    
        return StreamingResponse(
            iterfile(),
            media_type="video/mp4",
            headers={
                "Accept-Ranges": "bytes",
                "Content-Disposition": f'inline; filename="story_{node_id}.mp4"'
            }
        ) 
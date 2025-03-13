import os
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional

from config import get_video_path

class VideoService:
    def __init__(self, base_dir: str = "output/stories"):
        self.base_dir = base_dir

    def get_video_path(self, story_id: str, node_id: str) -> str:
        """
        Gets the path to a video file.
        
        Args:
            story_id (str): The story ID
            node_id (str): The node ID
            
        Returns:
            str: The path to the video file
        """
        return os.path.join(self.base_dir, story_id, node_id, "story.mp4")

    def stream_video(self, story_id: str, node_id: str) -> StreamingResponse:
        """
        Streams a video file.
        
        Args:
            story_id (str): The story ID
            node_id (str): The node ID
            
        Returns:
            StreamingResponse: The video stream
            
        Raises:
            HTTPException: If the video file is not found
        """
        video_path = get_video_path(story_id, node_id)
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video not found")
            
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
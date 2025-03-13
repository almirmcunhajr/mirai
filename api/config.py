import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent

# Output directories
OUTPUT_DIR = BASE_DIR / "output"
VIDEOS_DIR = OUTPUT_DIR / "videos"

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_BASE_URL = os.getenv("API_BASE_URL", f"http://{API_HOST}:{API_PORT}")

# Video configuration
VIDEO_BASE_URL = f"{API_BASE_URL}/videos"
VIDEO_EXTENSION = "mp4"

# Create necessary directories
OUTPUT_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

def get_video_path(story_id: str, node_id: str) -> Path:
    """Get the path to a video file."""
    return VIDEOS_DIR / f"{story_id}_{node_id}.{VIDEO_EXTENSION}"

def get_video_url(story_id: str, node_id: str) -> str:
    """Get the URL for a video."""
    return f"{VIDEO_BASE_URL}/stories/{story_id}/nodes/{node_id}" 
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from story.story_router import router as story_router
from video.video_router import router as video_router
from config import API_HOST, API_PORT

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Mirai API",
    description="API for generating and managing interactive stories",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(story_router)
app.include_router(video_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Mirai API",
        "version": "1.0.0",
        "host": API_HOST,
        "port": API_PORT
    } 
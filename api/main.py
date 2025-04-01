import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from story.story_router import router as story_router
from video.video_router import router as video_router
from auth.auth_router import router as auth_router
from config import API_HOST, API_PORT

load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Mirai API",
    description="API for generating and managing interactive stories",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(story_router)
app.include_router(video_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Mirai API",
        "version": "1.0.0",
        "host": API_HOST,
        "port": API_PORT
    } 
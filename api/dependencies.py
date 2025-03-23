from functools import lru_cache
import os
from fastapi import Depends

from ttt.openai import OpenAI as OpenAITTT
from tti.openai import OpenAI as OpenAITTI
from tts.openai import OpenAI as OpenAITTS
from tts.tts import TTS
from tti.tti import TTI
from ttt.ttt import TTT
from tts.elevenlabs import ElevenLabs
from script.script_service import ScriptService
from visual.visual_service import VisualService
from audio.audio_service import AudioService
from audiovisual.audiovisual_service import AudioVisualService
from story.story_service import StoryService
from video.video_service import VideoService

def get_openai_api_key() -> str:
    """Get OpenAI API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not configured")
    return api_key

def get_elevenlabs_api_key() -> str:
    """Get ElevenLabs API key from environment."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ElevenLabs API key not configured")
    return api_key

@lru_cache()
def get_openai_ttt(api_key: str = Depends(get_openai_api_key)) -> OpenAITTT:
    """Get OpenAI TTT instance."""
    return OpenAITTT(api_key=api_key)

@lru_cache()
def get_openai_tts(api_key: str = Depends(get_openai_api_key)) -> OpenAITTS:
    """Get OpenAI TTS instance."""
    return OpenAITTS(api_key=api_key)

@lru_cache()
def get_openai_tti(api_key: str = Depends(get_openai_api_key)) -> OpenAITTI:
    """Get OpenAI TTI instance."""
    return OpenAITTI(api_key=api_key)

@lru_cache()
def get_elevenlabs_tts(api_key: str = Depends(get_elevenlabs_api_key)) -> ElevenLabs:
    """Get ElevenLabs instance."""
    return ElevenLabs(api_key=api_key)

@lru_cache()
def get_script_service(ttt: TTT = Depends(get_openai_ttt)) -> ScriptService:
    """Get ScriptService instance."""
    return ScriptService(ttt)

@lru_cache()
def get_visual_service(tti: TTI = Depends(get_openai_tti)) -> VisualService:
    """Get VisualService instance."""
    return VisualService(tti)

@lru_cache()
def get_audio_service(tts: TTS = Depends(get_openai_tts)) -> AudioService:
    """Get AudioService instance."""
    return AudioService(tts)

@lru_cache()
def get_audiovisual_service(
    visual_service: VisualService = Depends(get_visual_service),
    audio_service: AudioService = Depends(get_audio_service)
) -> AudioVisualService:
    """Get AudioVisualService instance."""
    return AudioVisualService(visual_service, audio_service)

@lru_cache()
def get_story_service(
    script_service: ScriptService = Depends(get_script_service),
    audiovisual_service: AudioVisualService = Depends(get_audiovisual_service)
) -> StoryService:
    """Get StoryService instance."""
    return StoryService(script_service, audiovisual_service)

@lru_cache()
def get_video_service() -> VideoService:
    """Get VideoService instance."""
    return VideoService() 
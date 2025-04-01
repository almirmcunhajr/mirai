from functools import lru_cache
import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ttt.openai import OpenAI as OpenAITTT
from tti.openai import OpenAI as OpenAITTI
from tts.openai import OpenAI as OpenAITTS
from stt.openai import OpenAI as OpenAISTT
from tti.together import Together as TogetherTTI
from tts.tts import TTS
from tti.tti import TTI
from ttt.ttt import TTT
from stt.stt import STT
from tts.elevenlabs import ElevenLabs
from script.script_service import ScriptService
from visual.visual_service import VisualService
from audio.audio_service import AudioService
from audiovisual.audiovisual_service import AudioVisualService
from story.story_service import StoryService
from video.video_service import VideoService
from auth.auth_service import AuthService
from user.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_openai_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not configured")
    return api_key

def get_together_api_key() -> str:
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError("Together API key not configured")
    return api_key

def get_elevenlabs_api_key() -> str:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ElevenLabs API key not configured")
    return api_key

def get_google_client_id() -> str:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise ValueError("Google Client ID not configured")
    return client_id

def get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise ValueError("JWT Secret not configured")
    return secret

@lru_cache()
def get_openai_ttt(api_key: str = Depends(get_openai_api_key)) -> OpenAITTT:
    return OpenAITTT(api_key=api_key)

@lru_cache()
def get_openai_tts(api_key: str = Depends(get_openai_api_key)) -> OpenAITTS:
    return OpenAITTS(api_key=api_key)

@lru_cache()
def get_openai_tti(api_key: str = Depends(get_openai_api_key)) -> OpenAITTI:
    return OpenAITTI(api_key=api_key)

@lru_cache()
def get_openai_stt(api_key: str = Depends(get_openai_api_key)) -> OpenAISTT:
    return OpenAISTT(api_key=api_key)

@lru_cache()
def get_together_tti(api_key: str = Depends(get_together_api_key)) -> TogetherTTI:
    return TogetherTTI(api_key=api_key)

@lru_cache()
def get_elevenlabs_tts(api_key: str = Depends(get_elevenlabs_api_key)) -> ElevenLabs:
    return ElevenLabs(api_key=api_key)

@lru_cache()
def get_script_service(ttt: TTT = Depends(get_openai_ttt)) -> ScriptService:
    return ScriptService(ttt)

@lru_cache()
def get_visual_service(tti: TTI = Depends(get_together_tti), ttt: TTT = Depends(get_openai_ttt)) -> VisualService:
    return VisualService(tti, ttt)

@lru_cache()
def get_audio_service(
    tts: TTS = Depends(get_elevenlabs_tts),
    stt: STT = Depends(get_openai_stt),
    ttt: TTT = Depends(get_openai_ttt),
) -> AudioService:
    return AudioService(tts, stt, ttt)

@lru_cache()
def get_audiovisual_service(
    visual_service: VisualService = Depends(get_visual_service),
    audio_service: AudioService = Depends(get_audio_service)
) -> AudioVisualService:
    return AudioVisualService(visual_service, audio_service)

@lru_cache()
def get_story_service(
    script_service: ScriptService = Depends(get_script_service),
    audiovisual_service: AudioVisualService = Depends(get_audiovisual_service)
) -> StoryService:
    return StoryService(script_service, audiovisual_service)

@lru_cache()
def get_video_service() -> VideoService:
    return VideoService()

@lru_cache()
def get_auth_service(
    google_client_id: str = Depends(get_google_client_id),
    jwt_secret: str = Depends(get_jwt_secret)
) -> AuthService:
    return AuthService(
        google_client_id=google_client_id,
        jwt_secret=jwt_secret
    )

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    return await auth_service.get_current_user(token) 
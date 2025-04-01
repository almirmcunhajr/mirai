from moviepy.audio.io.AudioFileClip import AudioFileClip
from enum import StrEnum

from stt.stt import TranscriptionWord
from script.script import LineType

class SoundEffectType(StrEnum):
    SOUND_EFFECT = "sound_effect"
    AMBIENT = "ambient"

class Audio:
    def __init__(self, clip: AudioFileClip):
        self.clip = clip

class LineAudio(Audio):
    def __init__(self, clip: AudioFileClip, transcription: list[TranscriptionWord], type: LineType):
        super().__init__(clip)
        self.transcription = transcription
        self.type = type

class SoundEffectAudio(Audio):
    def __init__(self, clip: AudioFileClip, type: SoundEffectType):
        self.type = type
        super().__init__(clip)
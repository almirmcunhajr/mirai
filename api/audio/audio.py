from moviepy.audio.io.AudioFileClip import AudioFileClip

from stt.stt import TranscriptionWord

class Audio:
    def __init__(self, clip: AudioFileClip):
        self.clip = clip

class LineAudio(Audio):
    def __init__(self, clip: AudioFileClip, transcription: list[TranscriptionWord], type):
        super().__init__(clip)
        self.transcription = transcription
        self.type = type

class SoundEffectAudio(Audio):
    def __init__(self, clip: AudioFileClip):
        super().__init__(clip)
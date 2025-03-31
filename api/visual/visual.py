from moviepy.video.VideoClip import ImageClip

class Visual:
    def __init__(self, clip: ImageClip, base64_image: str = None):
        self.clip = clip
        self.base64_image = base64_image

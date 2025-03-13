import os
from dotenv import load_dotenv

from facade.chatgpt import ChatGPT
from facade.elevenlabs import ElevenLabs
from script.script_service import ScriptService
from visual.visual_service import VisualService
from audio.audio_service import AudioService
from audiovisual.audiovisual_service import AudioVisualService
from common.genre import Genre
from common.idiom import Idiom
from script.script import Script

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API keys from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not openai_api_key or not elevenlabs_api_key:
        print("Error: Missing API keys. Please set OPENAI_API_KEY and ELEVENLABS_API_KEY in .env file")
        return

    try:
        # Initialize facades
        chatbot = ChatGPT(api_key=openai_api_key)
        tts = ElevenLabs(api_key=elevenlabs_api_key)

        # Initialize services
        script_service = ScriptService(chatbot)
        visual_service = VisualService(chatbot)
        audio_service = AudioService(tts)
        audiovisual_service = AudioVisualService(visual_service, audio_service)

        print("Generating initial script...")
        # Generate initial script (fantasy story in English)
        script = script_service.generate(
            genre=Genre.FANTASY,
            idiom=Idiom.PT
        )
        
        print(f"\nGenerated script with {len(script.frames)} frames:")
        print(f"Title: {script.title}")
        for i, frame in enumerate(script.frames, 1):
            print(f"\nFrame {i}:")
            print(f"Narration: {frame.narration}")
            print(f"Description: {frame.description}")
        print("\nPossible decisions:")
        for i, decision in enumerate(script.decisions, 1):
            print(f"{i}. {decision}")

        # Create output directory
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        print("\nGenerating video...")
        # Generate video from script
        video_path = audiovisual_service.generate_video(script, output_dir)

        if video_path:
            print(f"\nSuccess! Video generated at: {video_path}")
        else:
            print("\nError: Failed to generate video")

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main() 
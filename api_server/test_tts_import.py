import sys
from pathlib import Path

# Setup paths like in tts.py
api_server_path = "/Volumes/FREDDY FILES/ANTIGRAVITY/1001-VIDEO AVATAR/api_server"
sys.path.append(api_server_path)

try:
    print("Attempting to import generate_voiceover...")
    from avatar_tts.tts_engine import generate_voiceover
    print("Import successful!")
    
    # Check if we can get the model (this might be slow)
    # from avatar_tts.tts_engine import get_tts_model
    # print("Loading model...")
    # model = get_tts_model()
    # print("Model loaded successfully!")
    
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

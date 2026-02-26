import gradio as gr
import json
import os
from pathlib import Path
import logging
from tts_engine import generate_voiceover
from sadtalker_runner import run_sadtalker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load voice presets
VOICES_FILE = Path(__file__).parent / "voices" / "voices.json"
VOICES_DIR = Path(__file__).parent / "voices"

def load_voices():
    if not VOICES_FILE.exists():
        return []
    with open(VOICES_FILE, 'r') as f:
        return json.load(f)

def generate_video(image_path, text, voice_id, language):
    if not image_path:
        return None, "Error: Please upload a source image."
    if not text:
        return None, "Error: Please enter text to speak."
    
    voices = load_voices()
    voice_preset = next((v for v in voices if v['id'] == voice_id), None)
    
    if not voice_preset:
        return None, f"Error: Voice preset '{voice_id}' not found."
    
    speaker_wav = VOICES_DIR / Path(voice_preset['path']).name
    
    if not speaker_wav.exists():
        return None, f"Error: Voice sample file missing at {speaker_wav}. Please add the .wav file to the voices directory."

    try:
        # 1. Generate Audio
        yield None, f"Status: Generating audio for '{voice_id}' (CPU)..."
        audio_path = generate_voiceover(text, str(speaker_wav), language)
        
        # 2. Generate Video
        yield None, f"Status: Audio generated. Starting SadTalker animation (CPU, this will take time)..."
        video_path = run_sadtalker(image_path, audio_path)
        
        if video_path:
            yield video_path, "Success: Video generation complete!"
        else:
            yield None, "Error: SadTalker failed to generate video."
            
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        yield None, f"Error: {str(e)}"

# Setup Gradio Interface
voices = load_voices()
voice_choices = [(v['label'], v['id']) for v in voices]

with gr.Blocks(title="TalkFlow - Avatar TTS") as demo:
    gr.Markdown("# TalkFlow: Local Avatar TTS & Animation")
    gr.Markdown("Clone voices with XTTS-v2 and animate them with SadTalker — 100% Local.")
    
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(label="Source Image", type="filepath")
            input_text = gr.Textbox(label="Text to Speak", placeholder="Enter up to 250 characters...", lines=3)
            voice_select = gr.Dropdown(label="Voice Preset", choices=voice_choices, value=voice_choices[0][1] if voice_choices else None)
            lang_select = gr.Dropdown(label="Language Override", choices=["es", "en", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn"], value="es")
            
            generate_btn = gr.Button("Generate Video", variant="primary")
            
        with gr.Column():
            output_video = gr.Video(label="Generated Video")
            status_text = gr.Markdown("Status: Idle")

    generate_btn.click(
        fn=generate_video,
        inputs=[input_image, input_text, voice_select, lang_select],
        outputs=[output_video, status_text]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7861)

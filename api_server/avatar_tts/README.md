# Avatar TTS & SadTalker Local Module

This module provides a local interface for cloning voices using **XTTS-v2** and animating images using **SadTalker**.

## Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements-avatar.txt
   ```

3. **FFmpeg**:
   Ensure you have ffmpeg installed (`brew install ffmpeg` on macOS).

## How to Run

```bash
python app.py
```

## Adding New Voices

1. Place a 10-30 second clear audio sample (`.wav`) in the `voices/` directory.
2. Update `voices/voices.json` with the new entry:
   ```json
   {
     "id": "name",
     "label": "Display Name",
     "path": "voices/name.wav",
     "lang": "en"
   }
   ```

## Technical Notes

- **XTTS-v2**: Runs on CPU. Text limit is enforced at 250 characters for performance.
- **SadTalker**: Uses the existing installation at `/Users/iblstudios/local_sadtalker_test/SadTalker`.
- **Outputs**: Audios and videos are saved in the `outputs/` directory (Git ignored).

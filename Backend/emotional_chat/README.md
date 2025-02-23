# Emotional Chat System

An AI-powered emotional chat system that combines real-time emotion detection with speech interaction and video processing capabilities.

## Project Structure

```
emotional_chat/
├── src/                    # Source code
│   ├── __init__.py        # Package initialization
│   ├── app.py             # Flask API server
│   ├── emotion_monitor.py  # Emotion detection
│   ├── emotional_speech_agent.py  # Main integration
│   ├── frontend_integration.py  # Frontend integration
│   └── speech_converter.py  # Speech handling
│
├── config/                 # Configuration
│   └── config.py          # API keys and settings
│
├── tests/                 # Test files and resources
│   ├── test_api.py       # API endpoint tests
│   ├── record_test_video.py  # Video recording utility
│   └── test_*.mp4        # Test video files
│
├── conversations/        # Conversation history
│   └── conversation_*.json  # Conversation logs
│
├── emotion_logs/        # Emotion detection logs
│   └── emotion_log_*.json  # Daily emotion logs
│
├── run.py              # Main entry point
├── requirements.txt    # Dependencies
├── .env               # Environment variables
├── .env.example       # Example environment file
└── README.md          # This file
```

## Components

1. Source Code (`src/`):
   - `app.py`: Flask API server for handling video and speech processing
   - `emotion_monitor.py`: Real-time emotion detection using webcam
   - `emotional_speech_agent.py`: Main system integration
   - `frontend_integration.py`: Frontend communication layer
   - `speech_converter.py`: Speech-to-text and text-to-speech

2. Configuration:
   - `config/config.py`: API keys and system settings
   - `.env`: Environment variables (not in version control)
   - `.env.example`: Template for environment variables

3. Tests (`tests/`):
   - API endpoint tests
   - Video recording utility
   - Test video and audio files

4. Logs:
   - `conversations/`: JSON files with chat history
   - `emotion_logs/`: Daily emotion detection summaries

## Requirements

- Python 3.8+
- FFmpeg (for video processing)
- OpenCV
- TensorFlow
- Flask
- Other dependencies in `requirements.txt`

## Setup

1. Install FFmpeg:
   ```bash
   # Windows (using Chocolatey)
   choco install ffmpeg
   
   # Or download from https://ffmpeg.org/download.html
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   - Copy `.env.example` to `.env`
   - Add your API keys and settings

4. Run the system:
   ```bash
   # Run the API server
   python src/app.py
   
   # Or run the full application
   python run.py
   ```

## Usage

1. API Endpoints:
   - `POST /api/process_video`: Process video for emotions and speech
     - Accepts: MP4 video file
     - Returns: Emotions, transcribed speech, and AI response

2. Local Application:
   - Start your webcam for emotion detection
   - Listen to your microphone for speech
   - Provide emotionally-aware responses

3. Frontend Integration:
   - Send video recordings to the API
   - Receive real-time emotion analysis
   - Get context-aware AI responses

4. Testing:
   - Use `record_test_video.py` to create test videos
   - Run `test_api.py` to test the API endpoints

## Development

1. Adding New Features:
   - Add source files to `src/`
   - Add tests to `tests/`
   - Update `requirements.txt` if needed

2. Testing:
   - Run API tests: `python tests/test_api.py`
   - Record test videos: `python tests/record_test_video.py`

3. Logs and Monitoring:
   - Check `emotion_logs/` for emotion detection data
   - Review `conversations/` for chat history

## Stopping the Application

- API Server: Press Ctrl+C in the terminal
- Local App: Press 'q' in the emotion window

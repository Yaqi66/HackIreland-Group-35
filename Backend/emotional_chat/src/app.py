"""
Flask application for the Emotional Chat System
"""
import os
import io
import base64
import logging
import tempfile
import shutil
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import json
import traceback
import time
import openai
from .emotional_speech_agent import EmotionalSpeechAgent
from .audio_processor import AudioProcessor
from .video_processor import split_video, cleanup_temp_files
from .config import Config
import subprocess
import uuid

from . import emotional_speech_agent

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Flask to handle trailing slashes
app.url_map.strict_slashes = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize processors
speech_agent = EmotionalSpeechAgent()
audio_processor = AudioProcessor()


# Create temp directory for processing
TEMP_DIR = Path(tempfile.gettempdir()) / "emotional_chat_temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Create necessary directories
for path in [Config.UPLOAD_FOLDER, Config.TEMP_FOLDER, Config.RECORDINGS_FOLDER]:
    path.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Emotional Chat System API is running"
    })

@app.route('/api/detect-wake-word', methods=['POST'])
def detect_wake_word():
    """
    Detect wake word in WebM audio data
    Expects base64 encoded WebM audio data in the request
    """
    logging.info("detect_wake_word endpoint called")
    try:
        # Log request content type and data
        logging.info(f"Content-Type: {request.content_type}")
        logging.info(f"Request data: {request.data[:100]}...")  # Log first 100 chars

        try:
            data = request.get_json()
        except Exception as e:
            logging.error(f"Failed to parse JSON: {str(e)}")
            return jsonify({
                'error': 'Invalid JSON format',
                'details': 'Request must be valid JSON with "audio" key containing base64 data'
            }), 400

        logging.info(f"Parsed JSON data keys: {data.keys() if data else None}")

        if not data:
            return jsonify({
                'error': 'Empty request body'
            }), 400

        if 'audio' not in data:
            return jsonify({
                'error': 'Missing audio data',
                'details': 'Request must include "audio" key with base64 encoded audio data'
            }), 400

        # Process the WebM audio data
        result = audio_processor.process_audio_data_base64(data['audio'])
        return jsonify(result)

    except Exception as e:
        logging.exception("Error in detect_wake_word:")
        return jsonify({
            'error': 'Failed to process audio',
            'details': str(e)
        }), 500 

@app.route('/api/process-video', methods=['POST'])
def process_video():
    """Process video for emotion detection and speech recognition"""
    logging.info("process_video endpoint called")
    logging.info(f"Request method: {request.method}")
    logging.info(f"Request headers: {dict(request.headers)}")
    logging.info(f"Request path: {request.path}")
    logging.info(f"Request data: {request.get_data()[:100]}...")  # Log first 100 chars of data
    
    try:
        if not request.is_json:
            logging.warning("Request is not JSON")
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        if 'video' not in request.json:
            logging.warning("No video data provided")
            return jsonify({'error': 'No video data provided'}), 400

        # Get base64 video data
        video_data = request.json['video']
        logging.info(f"Video data received (length: {len(video_data)} characters)")

        # Create temp directory if it doesn't exist
        temp_dir = Path(tempfile.mkdtemp())
        logging.info(f"Created temporary directory: {temp_dir}")
        video_path = temp_dir / f"{uuid.uuid4()}.webm"
        logging.info(f"Video path: {video_path}")

        try:
            # Decode and save video data
            video_bytes = base64.b64decode(video_data.split(',')[1] if ',' in video_data else video_data)
            with open(video_path, 'wb') as f:
                f.write(video_bytes)
            logging.info(f"Video data saved to {video_path}")

            # Process video
            logging.info(f"Processing video using speech_agent.process_video: {video_path}")
            emotion_result = speech_agent.process_video(str(video_path))
            if not emotion_result or not emotion_result.get('success'):
                error_msg = emotion_result.get('error', 'Failed to process video for emotions') if emotion_result else 'Failed to process video for emotions'
                logging.error(error_msg)
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500

            video_stream, audio_stream = split_video(str(video_path))
            if not audio_stream:
                logging.error("Failed to extract audio from video")
                return jsonify({
                    'success': False,
                    'error': 'Failed to extract audio from video'
                }), 500
            
            # Process the audio file if it was successfully created
            if audio_stream and os.path.exists(audio_stream):
                # Create temp_processing directory if it doesn't exist
                temp_processing = Path(__file__).parent.parent.absolute() / 'src/temp_processing'
                temp_processing.mkdir(exist_ok=True)
                
                try:
                    # Generate unique filename using UUID
                    debug_wav = temp_processing / f"{uuid.uuid4()}.wav"
                    shutil.copy2(audio_stream, debug_wav)
                    logging.info(f"Saved debug WAV file to: {debug_wav}")
                    
                    # Process the audio file
                    asr_response = audio_processor.process_audio_file(str(debug_wav))
                    if not asr_response or not asr_response.get('success'):
                        error_msg = asr_response.get('error', 'Failed to transcribe audio') if asr_response else 'Failed to transcribe audio'
                        logging.error(error_msg)
                        return jsonify({
                            'success': False,
                            'error': error_msg
                        }), 500

                    # Get AI response
                    ai_response = speech_agent.get_response(
                        asr_response['transcription'],
                        {'dominant_emotion': emotion_result['emotions']['dominant']}
                    )
                    if not ai_response:
                        logging.error("Failed to get AI response")
                        return jsonify({
                            'success': False,
                            'error': 'Failed to generate AI response'
                        }), 500

                    # Return the complete result
                    result = {
                        'success': True,
                        'emotions': emotion_result['emotions'],
                        'speech_text': asr_response['transcription'],
                        'response': ai_response
                    }
                    logging.info(f"Final result: {result}")
                    return jsonify(result)

                finally:
                    # Clean up the temporary WAV file
                    try:
                        if debug_wav.exists():
                            debug_wav.unlink()
                            logging.info(f"Removed temporary WAV file: {debug_wav}")
                    except Exception as e:
                        logging.warning(f"Error removing temporary WAV file: {e}")

            logging.info(f"Result from speech_agent.process_video: {emotion_result}")
            return jsonify(emotion_result)

        except Exception as e:
            logging.exception("Error processing video/audio:")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

        finally:
            # Cleanup temp files
            try:
                logging.info("Cleaning up temporary files...")
                if video_path.exists():
                    video_path.unlink()
                    logging.info(f"Deleted {video_path}")
                temp_dir.rmdir()
                logging.info(f"Removed directory {temp_dir}")
            except Exception as e:
                logging.warning(f"Error during temporary file cleanup: {e}")

    except Exception as e:
        logging.exception("Error in process_video endpoint:")
        return jsonify({
            'success': False,
            'error': 'Failed to process request',
            'details': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process chat message with emotion awareness
    """
    logging.info("chat endpoint called")
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            logging.warning("No message provided")
            return jsonify({
                'error': 'No message provided'
            }), 400

        # Get emotion data if available
        emotion = data.get('emotion', 'neutral')

        # Process the chat message
        response = speech_agent.chat(data['message'], emotion)
        return jsonify(response)

    except Exception as e:
        logging.exception("Error in chat endpoint:")
        return jsonify({
            'error': 'Failed to process message',
            'details': str(e)
        }), 500

@app.route('/api/process-emotion', methods=['POST'])
def process_emotion():
    """
    Process video frame for emotion detection
    Expects base64 encoded image data
    """
    logging.info("process_emotion endpoint called")
    try:
        data = request.get_json()

        if not data or 'frame' not in data:
            logging.warning("No frame data provided")
            return jsonify({
                'error': 'No frame data provided'
            }), 400

        # Process the frame
        result = speech_agent.process_emotion(data['frame'])
        return jsonify(result)

    except Exception as e:
        logging.exception("Error in process_emotion endpoint:")
        return jsonify({
            'error': 'Failed to process frame',
            'details': str(e)
        }), 500

@app.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        'status': 'ok',
        'message': 'API is working',
        'method': request.method,
        'path': request.path
    })

@app.route('/api/debug/routes', methods=['GET'])
def list_routes():
    """List all registered routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify(routes)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with more information"""
    logging.warning(f"404 Error: {request.method} {request.url}")
    logging.warning(f"Headers: {dict(request.headers)}")
    return jsonify({
        'error': 'Not Found',
        'message': f'The requested URL {request.path} was not found on the server.',
        'method': request.method,
        'path': request.path,
        'available_routes': [str(rule) for rule in app.url_map.iter_rules()]
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
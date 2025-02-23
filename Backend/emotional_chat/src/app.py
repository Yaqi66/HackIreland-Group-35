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
import threading
import queue
import uuid
from .emotional_speech_agent import EmotionalSpeechAgent
from .command_recognizer import CommandRecognizer
from .audio_processor import AudioProcessor
from .video_processor import split_video, cleanup_temp_files
from .config import Config
from .ThreadWithReturnValue import ThreadWithReturnValue

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
def index(): #basic get check for the server status, if can connect
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

#Methods in main to thread
def process_get_response(speech_agent, transcription, emotion_result):
    """Helper function to get AI response"""
    try:
        if transcription != None and emotion_result != None: #If there is a text

            ai_response = speech_agent.get_response(
            transcription,
            {'dominant_emotion': emotion_result['emotions']['dominant']}
            )
            return ai_response #If that's that send ai.

    except Exception as e:
        logging.exception("Error getting AI response:")
    return None #If that's the case.

def process_get_command(command_recognizer, transcription): #Process to the function
    """Helper function to get command"""
    try:
        if (command_recognizer != None and transcription != None):
            command = command_recognizer.recognize_command(transcription)
            return command

    except Exception as e:
        logging.exception("Error in process_get_command:") #Except to process audio
    return None

@app.route('/api/process-video', methods=['POST'])
def process_video():
    """Process video for emotion detection and speech recognition"""
    logging.info("process_video endpoint called") #Basic log start and call
    logging.info(f"Request method: {request.method}")
    logging.info(f"Request headers: {dict(request.headers)}")
    logging.info(f"Request path: {request.path}") #General checks that the user sent all the data and that the data did not get lost.
    logging.info(f"Request data: {request.get_data()[:100]}...")  # Log first 100 chars of data to check length

    try:
        if not request.is_json: #Checks Json request, from content side.
            logging.warning("Request is not JSON") #Notifies the type, from the request.
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        if 'video' not in request.json: #Checks video from request.Json
            logging.warning("No video data provided") #Check for data inside data
            return jsonify({'error': 'No video data provided'}), 400

        # Get base64 video data from data
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
            with open(video_path, 'wb') as f: #Create the file.
                f.write(video_bytes) #Set information from video data
            logging.info(f"Video data saved to {video_path}") #Notify

            # Process video for audio and emotion
            logging.info(f"Processing video for audio and emotion: {video_path}") #Process video information, from a request
            emotion_result = speech_agent.process_video(str(video_path))  #To a proper string
            if not emotion_result or not emotion_result.get('success'): #From result make sure it is proper, from result make sure it has all the variables, that its accurate
                error_msg = emotion_result.get('error', 'Failed to process video for emotions') if emotion_result else 'Failed to process video for emotions'
                logging.error(error_msg) #Notify the user
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500 #From result return status and value

            video_stream, audio_stream = split_video(str(video_path)) #Video is spilt and all data stored again.
            if not audio_stream: #Checks for audio file and valid link to process audio data
                logging.error("Failed to extract audio from video") #Notify all information is processed in code
                return jsonify({
                    'success': False,
                    'error': 'Failed to extract audio from video'
                }), 500

            # Process the audio file if it was successfully created, after validation, begin new proccess
            if audio_stream and os.path.exists(audio_stream): #If there audio set and has to do with the file location, and the path exists
                temp_processing = Path(__file__).parent.parent.absolute() / 'src/temp_processing'  #Generate path
                temp_processing.mkdir(exist_ok=True) #If there is a path create file

                try:
                    # Create temp name using UUID
                    debug_wav = temp_processing / f"{uuid.uuid4()}.wav"
                    shutil.copy2(audio_stream, debug_wav) #Copy new file to the debug
                    logging.info(f"Saved debug WAV file to: {debug_wav}") #Logging process

                    asr_response = audio_processor.process_audio_file(str(debug_wav))
                    if not asr_response or not asr_response.get('success'):
                        error_msg = asr_response.get('error', 'Failed to transcribe audio') if asr_response else 'Failed to transcribe audio'
                        logging.error(error_msg) #Logging process

                        return jsonify({ #Return results
                            'success': False,
                            'error': error_msg
                        }), 500

                    command_recognizer = CommandRecognizer(Config.OPENAI_API_KEY) #Set base

                    #Here are our methods.
                    get_response_thread = ThreadWithReturnValue(target=process_get_response, args=(speech_agent, asr_response['transcription'], emotion_result))
                    get_command_thread = ThreadWithReturnValue(target=process_get_command, args=(command_recognizer, asr_response['transcription'])) #Set command recognizer.

                    start = time.time()
                    get_response_thread.start() #Set first thread
                    get_command_thread.start() #Set second

                    #Get results.
                    ai_response = get_response_thread.join() #set values for all the code
                    command = get_command_thread.join()

                    end = time.time()
                    print (f"Thread time: {end - start}")

                    result = { #Build object.
                        'success': True,
                        'emotions': emotion_result['emotions'], #all
                        'speech_text': asr_response['transcription'], #Proper names
                        'response': ai_response,
                        'command': command
                    }
                    logging.info(f"Final result: {result}") #Logging and the proper return
                    return jsonify(result)

                finally: #Run try and always do process finally.
                    # Clean up the temporary WAV file
                    try:
                        if debug_wav.exists(): #Ensure exists
                            debug_wav.unlink() #Delink.
                            logging.info(f"Removed temporary WAV file: {debug_wav}") #Print state.
                    except Exception as e: #Check state or print process
                        logging.warning(f"Error removing temporary WAV file: {e}")

            logging.info(f"Result from speech_agent.process_video: {emotion_result}") #Log the start, if there and can access and run.
            return jsonify(emotion_result)

        except Exception as e:
            logging.exception("Error processing video/audio:") #Exception
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500 #All the exception and then print.

        finally:
            # Cleanup temp files, this is what was missed.
            try: #Start.
                logging.info("Cleaning up temporary files...") #Print state.
                if video_path.exists(): #There is a video
                    # video_path.unlink() #Unlink and delete #You may have issues because there may be a different user profile deleting this
                    logging.info(f"Deleted {video_path}") #Print state for data
                temp_dir.rmdir() #Remove the folder
                logging.info(f"Removed directory {temp_dir}") #Print state to let know user.
            except Exception as e: #If some file was lost in this try statement, it doesn't matter, the code still runs.
                logging.warning(f"Error during temporary file cleanup: {e}") #Print state

    except Exception as e: #If major issues occur notify user.
        logging.exception("Error in process_video endpoint:") #Print.
        return jsonify({ #Return information and set variable all with json variable and with key value sets.
            'success': False,
            'error': 'Failed to process request', #Notify
            'details': str(e) #Type of process.
        }), 500

@app.route('/api/chat', methods=['POST']) #Message to talk back from AI to user.
def chat():
    """
    Process chat message with emotion awareness
    """
    logging.info("chat endpoint called") #Log
    try:
        data = request.get_json() #request data and put all data set there

        if not data or 'message' not in data: #if the data does not exist
            logging.warning("No message provided") #print
            return jsonify({ #And push results with all parameters, send result back to main app, send all information in form.
                'error': 'No message provided'
            }), 400

        # Get emotion data if available
        emotion = data.get('emotion', 'neutral')

        # Process the chat message
        response = speech_agent.chat(data['message'], emotion) #Send info from request
        return jsonify(response) #Return

    except Exception as e:
        logging.exception("Error in chat endpoint:") #Print.
        return jsonify({
            'error': 'Failed to process message',
            'details': str(e)
        }), 500

@app.route('/api/process-emotion', methods=['POST']) #API request to send to models and get process from AI set.
def process_emotion():
    """ #DocStrings
    Process video frame for emotion detection
    Expects base64 encoded image data
    """
    logging.info("process_emotion endpoint called") #Log

    try: #Try running this code or process data request.
        data = request.get_json() #get all data into a value or to data

        if not data or 'frame' not in data: #Check data.exists, from the keys see if "from" exists.
            logging.warning("No frame data provided") #Print status
            return jsonify({ #Return json and keys with information.
                'error': 'No frame data provided' #Error that there is no data.
            }), 400

        # Process the frame
        result = speech_agent.process_emotion(data['frame']) #set result.
        return jsonify(result) #return that value

    except Exception as e: #There is data
        logging.exception("Error in process_emotion endpoint:") #The type of exception.
        return jsonify({ #The code was not successfully run.
            'error': 'Failed to process frame', #What error.
            'details': str(e) #Extra steps.
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

@app.route('/api/news', methods=['GET'])
def get_news():
    """Get news based on user preferences"""
    try:
        # For now, return a simple mock response
        news_data = {
            'success': True,
            'news': [
                {
                    'title': 'Technology News Update',
                    'description': 'Latest developments in AI and machine learning.',
                    'category': 'technology'
                },
                {
                    'title': 'World News Headlines',
                    'description': 'Current events from around the globe.',
                    'category': 'world'
                }
            ]
        }
        return jsonify(news_data)
    except Exception as e:
        logging.error(f"Error getting news: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch news'
        }), 500

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
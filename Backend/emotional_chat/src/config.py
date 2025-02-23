"""
Configuration settings for the Emotional Chat System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Base directory
    BASE_DIR = Path(__file__).parent.parent.absolute()
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '150'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Chat Configuration
    MAX_HISTORY = int(os.getenv('MAX_HISTORY', '5'))
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '30.0'))
    
    # Audio settings
    AUDIO_SAMPLE_RATE = 44100
    AUDIO_CHANNELS = 1
    
    # Wake word settings
    WAKE_WORDS = ['eva', 'ava']
    
    # Paths
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    TEMP_FOLDER = BASE_DIR / 'temp'
    RECORDINGS_FOLDER = BASE_DIR / 'recordings'
    CONVERSATIONS_FOLDER = BASE_DIR / 'conversations'
    
    # Video Processing
    VIDEO_WIDTH = 640
    VIDEO_HEIGHT = 480
    VIDEO_FPS = 30
    FRAME_SKIP = 5  # Process every Nth frame
    
    # API settings
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'webm'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Speech recognition settings
    SPEECH_ENERGY_THRESHOLD = 1000
    SPEECH_PAUSE_THRESHOLD = 0.8
    SPEECH_PHRASE_THRESHOLD = 0.3
    
    # Emotion detection settings
    EMOTION_THRESHOLD = 0.5
    EMOTIONS = [
        'angry', 'disgust', 'fear', 'happy', 
        'neutral', 'sad', 'surprise'
    ]
    
    @staticmethod
    def allowed_file(filename):
        """Check if the file extension is allowed"""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        # Create required directories
        for folder in [cls.UPLOAD_FOLDER, cls.TEMP_FOLDER, cls.RECORDINGS_FOLDER, cls.CONVERSATIONS_FOLDER]:
            folder.mkdir(parents=True, exist_ok=True)
            
        # Validate numeric values
        if cls.MAX_TOKENS < 1:
            raise ValueError("MAX_TOKENS must be greater than 0")
        if not 0 <= cls.TEMPERATURE <= 1:
            raise ValueError("TEMPERATURE must be between 0 and 1")
        if cls.MAX_HISTORY < 1:
            raise ValueError("MAX_HISTORY must be greater than 0")
        if not 0 <= cls.CONFIDENCE_THRESHOLD <= 100:
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0 and 100")

# Validate configuration on import
Config.validate()

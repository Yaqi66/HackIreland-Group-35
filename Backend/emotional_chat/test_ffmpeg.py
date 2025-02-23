"""
Test script to verify ffmpeg installation and functionality
"""
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_ffmpeg():
    """Test if ffmpeg is installed and working"""
    try:
        # Try to run ffmpeg -version
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            logging.info("ffmpeg is installed and accessible")
            logging.info("Version info:")
            logging.info(result.stdout.split('\n')[0])  # Print first line of version info
            return True
        else:
            logging.error("ffmpeg command failed")
            logging.error(f"Error output: {result.stderr}")
            return False
            
    except FileNotFoundError:
        logging.error("ffmpeg is not installed or not in PATH")
        return False
    except Exception as e:
        logging.error(f"Error testing ffmpeg: {e}")
        return False

if __name__ == "__main__":
    print("\n=== Testing FFmpeg Installation ===")
    if test_ffmpeg():
        print("\nFFmpeg is properly installed and working!")
        print("You can proceed with video/audio processing.")
    else:
        print("\nFFmpeg is not properly installed or configured.")
        print("Please install FFmpeg and make sure it's in your system PATH:")
        print("1. Download FFmpeg from: https://ffmpeg.org/download.html")
        print("2. Add FFmpeg's bin directory to your system PATH")
        print("3. Restart your terminal/IDE")

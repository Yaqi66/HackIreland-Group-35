"""
Test script for real-time speech conversion using microphone input.
Press Ctrl+C to stop the test.
"""
import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.speech_converter import SpeechConverter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Main function to test microphone input"""
    try:
        print("\n=== Speech Converter Microphone Test ===")
        print("This will test real-time speech conversion using your laptop's microphone.")
        print("Speak clearly into your microphone.")
        print("Press Ctrl+C to stop the test.\n")
        
        # Initialize speech converter
        converter = SpeechConverter()
        
        # Main loop
        while True:
            print("\nListening... (speak now)")
            text = converter.listen_and_convert()
            
            if text:
                print(f"\nYou said: {text}")
                
                # Echo back using text-to-speech
                print("Converting your speech back to audio...")
                converter.speak(f"You said: {text}")
            else:
                print("\nCould not understand audio. Please try again.")
            
            # Ask if user wants to continue
            response = input("\nPress Enter to continue or 'q' to quit: ")
            if response.lower() == 'q':
                break
                
    except KeyboardInterrupt:
        print("\n\nStopping speech converter...")
    except Exception as e:
        logging.error(f"Error in speech conversion: {e}")
    finally:
        print("\nTest complete!")

if __name__ == "__main__":
    main()

"""
Speech conversion module using SpeechRecognition
"""
import os
import tempfile
from pathlib import Path
import speech_recognition as sr
import base64
import numpy as np
import logging
import pyttsx3
from typing import Optional
from pydub import AudioSegment
import shutil

class SpeechConverter:
    """Class for converting speech to text using SpeechRecognition"""

    def __init__(self):
        """Initialize the speech converter"""
        self.recognizer = sr.Recognizer()

        # Adjust recognition settings
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        # Configure logging
        logging.basicConfig(level=logging.INFO)

        # Initialize microphone
        self.mic = sr.Microphone()
        try:
            with self.mic as source:
                print("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Ready for speech input!")
        except Exception as e:
            logging.error(f"Error during microphone initialization: {e}")

    def process_video(self, video_path):
        # This is a test comment
        """
        Extract audio from video and convert speech to text

        Args:
            video_path (str): Path to the video file

        Returns:
            str: Transcribed text from the video's audio
        """
        logging.info(f"process_video called with video_path: {video_path}")
        try:
            # Create temp directory for audio extraction
            temp_dir = Path(tempfile.mkdtemp())
            audio_path = temp_dir / 'temp_audio.wav'
            logging.info(f"Created temp directory: {temp_dir}")
            logging.info(f"Audio path: {audio_path}")

            try:
                # Extract audio using pydub
                logging.info("Extracting audio from video using pydub...")
                video = AudioSegment.from_file(video_path)
                video.export(str(audio_path), format='wav')
                logging.info("Audio extraction complete.")

                import os
                import shutil
                from pathlib import Path

                # Create test directory outside the temp directory
                base_dir = Path(__file__).resolve().parent  # Get the directory of the current file
                test_dir = base_dir / "test"
                if not os.path.exists(test_dir):
                    os.makedirs(test_dir)
                test_audio_path = test_dir / "temp_audio.wav"
                shutil.copy(audio_path, test_audio_path)
                logging.info(f"Copied audio file to test directory: {test_audio_path}")

                # Convert audio to text
                logging.info("Converting audio to text using SpeechRecognition...")
                with sr.AudioFile(str(audio_path)) as source:
                    # Adjust for ambient noise in the audio file
                    logging.info("Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Record the entire file
                    logging.info("Recording audio...")
                    audio = self.recognizer.record(source)
                    
                    # Use Google's speech recognition
                    logging.info("Using Google's speech recognition...")
                    try:
                        text = self.recognizer.recognize_google(audio)
                        logging.info(f"Transcription successful: {text}")
                        return text
                    except sr.UnknownValueError:
                        logging.warning("Google Speech Recognition could not understand audio")
                        return ""
                    except sr.RequestError as e:
                        logging.error(f"Could not request results from Google Speech Recognition service: {e}")
                        return ""

            except Exception as e:
                logging.error(f"Error during audio processing: {e}", exc_info=True)
                return ""

            finally:
                # Cleanup temp files
                try:
                    logging.info("Cleaning up temporary files...")
                    # if audio_path.exists():
                    #     audio_path.unlink()
                    #     logging.info(f"Deleted audio file: {audio_path}")
                    # temp_dir.rmdir()
                    # logging.info(f"Removed temp directory: {temp_dir}")
                except Exception as e:
                    logging.warning(f"Error during temporary file cleanup: {e}")

        except Exception as e:
            logging.exception(f"Error processing video audio:")
            return ""

    def process_audio_data(self, audio_data):
        """
        Process base64 encoded audio data

        Args:
            audio_data (str): Base64 encoded audio data

        Returns:
            dict: Dictionary containing success status and transcribed text
        """
        logging.info("process_audio_data called")
        temp_dir = None
        audio_path = None
        try:
            # Create temp directory
            temp_dir = Path(tempfile.mkdtemp())
            audio_path = temp_dir / 'temp_audio.wav'
            logging.info(f"Created temp directory: {temp_dir}")
            logging.info(f"Audio path: {audio_path}")

            try:
                # Decode and save audio data
                logging.info("Decoding base64 audio data...")
                audio_bytes = base64.b64decode(audio_data.split(',')[1] if ',' in audio_data else audio_data)
                with open(audio_path, 'wb') as f:
                    f.write(audio_bytes)
                logging.info("Audio data saved to file.")

                # Convert to text
                logging.info("Converting audio to text using SpeechRecognition...")
                with sr.AudioFile(str(audio_path)) as source:
                    # Adjust for ambient noise
                    logging.info("Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    # Record the entire file
                    logging.info("Recording audio...")
                    audio = self.recognizer.record(source)
                    # Use Google's speech recognition
                    logging.info("Using Google's speech recognition...")
                    text = self.recognizer.recognize_google(audio)
                    logging.info(f"Transcription: {text}")

                return {
                    'success': True,
                    'text': text
                }

            except Exception as e:
                logging.error(f"Error during audio processing: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        except Exception as e:
            logging.error(f"Error processing audio data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

        finally:
            # Cleanup temp files
            try:
                logging.info("Cleaning up temporary files...")
                # if audio_path and audio_path.exists():
                #     os.remove(str(audio_path))
                #     logging.info(f"Deleted audio file: {audio_path}")
                # if temp_dir and temp_dir.exists():
                #     temp_dir.rmdir()
                #     logging.info(f"Removed temp directory: {temp_dir}")
            except Exception as e:
                logging.warning(f"Error during temporary file cleanup: {e}")

    def listen_and_convert(self) -> Optional[str]:
        """Listen for speech and convert to text

        Returns:
            Optional[str]: Transcribed text or None if error
        """
        logging.info("listen_and_convert called")
        try:
            with self.mic as source:
                logging.info("Listening...")
                audio = self.recognizer.listen(source)

            logging.info("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            logging.info(f"Transcribed: {text}")
            return text

        except sr.UnknownValueError:
            logging.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logging.error(f"Could not request results; {e}")
            return None
        except Exception as e:
            logging.error(f"Error in speech recognition: {e}")
            return None

    def speak(self, text: str):
        """Convert text to speech

        Args:
            text (str): Text to convert to speech
        """
        try:
            logging.info(f"Speaking text: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"Error in text-to-speech: {e}")

    def process_audio_data_bytes(self, audio_data: bytes) -> Optional[str]:
        """Process raw audio data and convert to text

        Args:
            audio_data (bytes): Raw audio data

        Returns:
            Optional[str]: Transcribed text or None if error
        """
        logging.info("process_audio_data_bytes called")
        try:
            # Create temp file for audio data
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            logging.info(f"Created temp file: {temp_path}")

            # Convert to text
            with sr.AudioFile(temp_path) as source:
                # Adjust for ambient noise
                logging.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Record the entire file
                logging.info("Recording audio...")
                audio = self.recognizer.record(source)
                # Use Google's speech recognition
                logging.info("Using Google's speech recognition...")
                text = self.recognizer.recognize_google(audio)
                logging.info(f"Transcription: {text}")
                return text

        except Exception as e:
            logging.error(f"Error processing audio data: {e}")
            return None

        finally:
            # Cleanup temp file
            try:
                logging.info("Cleaning up temporary file...")
                # os.unlink(temp_path)
                # logging.info(f"Deleted temp file: {temp_path}")
            except Exception as e:
                logging.warning(f"Error during temporary file cleanup: {e}")

def main():
    """Test the speech converter"""
    converter = SpeechConverter()

    try:
        while True:
            # Get text input for text-to-speech conversion
            text_input = input("\nEnter text to convert to speech (or 'q' to quit): ")
            if text_input.lower() == 'q':
                break
            converter.speak(text_input)

            # Get speech input
            text = converter.listen_and_convert()
            if text:
                print(f"\nYou said: {text}")

                # Convert back to speech
                converter.speak(f"You said: {text}")

    except KeyboardInterrupt:
        print("\nStopping speech converter...")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
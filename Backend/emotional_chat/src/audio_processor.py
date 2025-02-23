"""
Audio processing module for handling different audio formats and wake word detection
"""
import os
import base64
import tempfile
import logging
from pathlib import Path
import speech_recognition as sr
import subprocess
import numpy as np
import soundfile as sf

class AudioProcessor:
    """Audio processing class for handling different audio formats and wake word detection"""

    def __init__(self):
        """Initialize the audio processor"""
        self.recognizer = sr.Recognizer()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.ffmpeg_path = "ffmpeg"  # Rely on the system PATH, was C:\ffmpeg\bin\ffmpeg.exe
        self.wake_words = ['eva', 'ava']

        # Configure speech recognition settings
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5
        self.recognizer.phrase_threshold = 0.3

        # Create temp directory if it doesn't exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def process_audio_file(self, audio_file):
        """
        Convert audio file to text using speech recognition

        Args:
            audio_file (str): Path to the audio file (WAV format)

        Returns:
            str: Transcribed text or empty string if failed
        """
        try:
            # Verify input file exists
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")

            logging.info(f"Processing audio file: {audio_file}")

            with sr.AudioFile(audio_file) as source:
                # Record audio from file
                audio = self.recognizer.record(source)

                try:
                    # Convert speech to text
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    logging.info(f"Transcribed text: {text}")
                    return text

                except sr.UnknownValueError:
                    logging.warning("Speech recognition could not understand audio")
                    return ""
                except sr.RequestError as e:
                    logging.error(f"Could not request results from speech recognition service: {e}")
                    return ""

        except Exception as e:
            logging.error(f"Error processing audio file: {e}")
            return ""

    def _convert_webm_to_wav(self, webm_data):
        """
        Convert WebM audio data to WAV format

        Args:
            webm_data (bytes): Raw WebM audio data

        Returns:
            str: Path to the converted WAV file
        """
        try:
            # Create temporary files
            webm_path = self.temp_dir / "temp_audio.webm"
            wav_path = self.temp_dir / "temp_audio.wav"

            # Write WebM data to temporary file
            with open(webm_path, 'wb') as f:
                f.write(webm_data)

            # Convert to WAV using ffmpeg
            command = [
                self.ffmpeg_path,
                '-i', str(webm_path),
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',  # Overwrite output file if it exists
                str(wav_path)
            ]

            logging.info(f"Running conversion command: {' '.join(command)}") #log the command

            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if process.returncode != 0:
                logging.error(f"FFmpeg conversion failed: {process.stderr}") #Log the error
                raise Exception(f"FFmpeg conversion failed: {process.stderr}") #Properly raise the error

            logging.info(f"Conversion successful, returning wav_path: {wav_path}")#Log the path
            return str(wav_path)

        except Exception as e:
            logging.exception("Error converting WebM to WAV:")
            raise Exception(f"Error converting WebM to WAV: {str(e)}")

    def process_audio_data(self, audio_wav_file_path):
        """
        Process audio data for wake word detection

        Args:
            audio_wav_file_path (str): Path to the WAV audio file

        Returns:
            dict: Result containing wake word detection status and transcription
        """
        try:
            logging.info("process_audio_data called")

            # Process the WAV file
            with sr.AudioFile(audio_wav_file_path) as source:
                # Record audio from file
                logging.info("Recording audio from file...")
                audio = self.recognizer.record(source)

                try:
                    # Convert speech to text
                    logging.info("Converting speech to text...")
                    text = self.recognizer.recognize_google(audio, language='en-US').lower()
                    logging.info(f"Transcribed text: {text}")

                    # Check for wake words
                    wake_word_detected = any(word in text for word in self.wake_words)
                    detected_words = [word for word in self.wake_words if word in text]

                    return {
                        'success': True,
                        'wake_word_detected': wake_word_detected,
                        'detected_words': detected_words,
                        'transcription': text
                    }

                except sr.UnknownValueError:
                    logging.warning("Speech recognition could not understand audio")
                    return {
                        'success': True,
                        'wake_word_detected': False,
                        'error': 'Could not understand audio'
                    }
                except sr.RequestError as e:
                    logging.error(f"Error with speech recognition service: {str(e)}")
                    return {
                        'success': False,
                        'error': f'Error with speech recognition service: {str(e)}'
                    }

        except Exception as e:
            logging.exception("Error processing audio:")
            return {
                'success': False,
                'error': f'Error processing audio: {str(e)}'
            }

        finally:
            # Cleanup temporary files
            try:
                logging.info("Cleaning up temporary files...")
                for temp_file in self.temp_dir.glob('*'):
                    temp_file.unlink()
            except Exception as e:
                logging.warning(f"Error during temporary file cleanup: {e}")

    def cleanup(self):
        """Clean up temporary files"""
        try:
            logging.info("Cleaning up temporary files...")
            for temp_file in self.temp_dir.glob('*'):
                temp_file.unlink()
            self.temp_dir.rmdir()
        except Exception as e:
            logging.warning(f"Error during cleanup: {e}")
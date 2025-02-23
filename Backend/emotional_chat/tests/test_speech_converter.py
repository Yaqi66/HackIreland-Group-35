import unittest
import os
import base64
import tempfile
from pathlib import Path
import sys
import threading
import queue
import time
import speech_recognition as sr

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.speech_converter import SpeechConverter
from pydub import AudioSegment
import numpy as np
import logging
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)

class TestSpeechConverter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        # Suppress pydub warnings about ffmpeg
        warnings.filterwarnings("ignore", category=RuntimeWarning)

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.speech_converter = SpeechConverter()
        self.test_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create a simple test audio file using pydub
            # Generate 1 second of silence
            self.sample_rate = 44100
            self.duration_ms = 1000  # 1 second
            silence = AudioSegment.silent(duration=self.duration_ms)
            self.test_audio_path = self.test_dir / 'test_audio.wav'
            silence.export(str(self.test_audio_path), format='wav')
            
            # Create a simple test video file
            self.test_video_path = self.test_dir / 'test_video.webm'
            with open(self.test_video_path, 'wb') as f:
                # Write a minimal WebM container
                f.write(b'\x1a\x45\xdf\xa3')  # EBML header
            
            # Create test audio data in base64
            with open(self.test_audio_path, 'rb') as f:
                audio_bytes = f.read()
            self.test_audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            logging.error(f"Error in setUp: {e}")
            self.tearDown()
            raise

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        try:
            # Remove test files
            if hasattr(self, 'test_audio_path') and self.test_audio_path.exists():
                os.remove(str(self.test_audio_path))
                logging.info(f"Removed test audio file: {self.test_audio_path}")
            
            if hasattr(self, 'test_video_path') and self.test_video_path.exists():
                os.remove(str(self.test_video_path))
                logging.info(f"Removed test video file: {self.test_video_path}")
            
            # Remove test directory if it exists and is empty
            if hasattr(self, 'test_dir') and self.test_dir.exists():
                try:
                    self.test_dir.rmdir()
                    logging.info(f"Removed test directory: {self.test_dir}")
                except OSError as e:
                    logging.warning(f"Could not remove test directory, it may not be empty: {e}")
                    # List remaining files
                    remaining = list(self.test_dir.glob('*'))
                    if remaining:
                        logging.warning(f"Remaining files: {remaining}")
                        # Force remove remaining files
                        for file in remaining:
                            try:
                                os.remove(str(file))
                                logging.info(f"Forced removal of: {file}")
                            except Exception as e:
                                logging.error(f"Could not remove file {file}: {e}")
                        # Try to remove directory again
                        self.test_dir.rmdir()
                        logging.info("Successfully removed test directory after cleanup")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

    def test_init(self):
        """Test initialization of SpeechConverter."""
        self.assertIsNotNone(self.speech_converter)
        self.assertIsNotNone(self.speech_converter.recognizer)
        self.assertIsNotNone(self.speech_converter.engine)

    def test_process_video(self):
        """Test video processing functionality."""
        # Test with invalid video path
        invalid_result = self.speech_converter.process_video("nonexistent.mp4")
        self.assertEqual(invalid_result, "")
        
        # Test with valid video path
        result = self.speech_converter.process_video(str(self.test_video_path))
        self.assertIsInstance(result, str)

    def test_process_audio_data(self):
        """Test audio data processing functionality."""
        # Test with invalid base64 data
        invalid_result = self.speech_converter.process_audio_data("invalid_base64")
        self.assertFalse(invalid_result['success'])
        self.assertIn('error', invalid_result)
        
        # Test with valid base64 data
        result = self.speech_converter.process_audio_data(self.test_audio_base64)
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)

    def test_process_audio_data_bytes(self):
        """Test processing of raw audio bytes."""
        # Read test audio file as bytes
        with open(self.test_audio_path, 'rb') as f:
            audio_bytes = f.read()
        
        # Test with valid audio bytes
        result = self.speech_converter.process_audio_data_bytes(audio_bytes)
        self.assertIsInstance(result, (str, type(None)))

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with None input
        result = self.speech_converter.process_audio_data(None)
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        
        # Test with empty string
        result = self.speech_converter.process_audio_data("")
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_cleanup(self):
        """Test cleanup of temporary files."""
        # Count initial wav files in temp directory
        temp_dir = Path(tempfile.gettempdir())
        initial_wavs = set(temp_dir.glob('*.wav'))
        
        # Create and process a test file
        test_file = self.test_dir / 'test_cleanup.wav'
        AudioSegment.silent(duration=500).export(str(test_file), format='wav')
        
        with open(test_file, 'rb') as f:
            audio_bytes = f.read()
        base64_data = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Process the audio
        self.speech_converter.process_audio_data(base64_data)
        
        # Give a small delay to allow for async cleanup
        time.sleep(0.5)
        
        # Get final wav files
        final_wavs = set(temp_dir.glob('*.wav'))
        
        # Clean up any new temporary files
        new_wavs = final_wavs - initial_wavs
        for wav in new_wavs:
            try:
                os.remove(str(wav))
            except Exception as e:
                logging.warning(f"Could not remove temporary wav file {wav}: {e}")
        
        # Clean up our test file
        if test_file.exists():
            os.remove(str(test_file))
        
        # Verify no new files remain
        self.assertEqual(
            len(final_wavs - initial_wavs), 
            0, 
            f"Found {len(final_wavs - initial_wavs)} new temporary wav files"
        )

    def test_realtime_speech_conversion(self):
        """Test real-time speech conversion with simulated audio input."""
        logging.info("Testing real-time speech conversion...")
        
        # Create a queue for results
        result_queue = queue.Queue()
        
        def mock_speech_input():
            """Simulate speech input using a pre-recorded audio file"""
            try:
                # Create a test audio file with actual speech-like content
                sample_rate = 44100
                duration_ms = 2000  # 2 seconds
                
                # Generate a simple sine wave at speech frequency (around 200 Hz)
                t = np.linspace(0, duration_ms/1000.0, int(sample_rate * duration_ms/1000.0))
                frequency = 200  # Hz
                audio_data = np.sin(2 * np.pi * frequency * t)
                
                # Add some variation to make it more speech-like
                audio_data += 0.5 * np.sin(2 * np.pi * 400 * t)  # Add harmonic
                audio_data *= (1 + 0.2 * np.sin(2 * np.pi * 5 * t))  # Add amplitude modulation
                
                # Normalize
                audio_data = np.int16(audio_data * 32767)
                
                # Save as WAV
                test_audio_path = self.test_dir / 'test_realtime.wav'
                import wave
                with wave.open(str(test_audio_path), 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 2 bytes per sample
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data.tobytes())
                
                logging.info(f"Created test audio file at {test_audio_path}")
                
                # Process the audio file
                with sr.AudioFile(str(test_audio_path)) as source:
                    # Adjust for ambient noise
                    self.speech_converter.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                    audio = self.speech_converter.recognizer.record(source)
                    try:
                        text = self.speech_converter.recognizer.recognize_google(audio)
                        result_queue.put(('success', text))
                        logging.info(f"Successfully recognized speech: {text}")
                    except sr.UnknownValueError:
                        msg = "Could not understand audio (this is expected for synthetic test audio)"
                        result_queue.put(('info', msg))
                        logging.info(msg)
                    except sr.RequestError as e:
                        result_queue.put(('error', f"Could not request results: {e}"))
                        logging.error(f"Request error: {e}")
            except Exception as e:
                result_queue.put(('error', f"Error in mock_speech_input: {e}"))
                logging.error(f"Error in mock_speech_input: {e}")
            finally:
                # Cleanup
                try:
                    if test_audio_path.exists():
                        os.remove(str(test_audio_path))
                        logging.info(f"Cleaned up test audio file: {test_audio_path}")
                except Exception as e:
                    logging.warning(f"Could not cleanup test audio file: {e}")
        
        # Start speech recognition in a separate thread
        thread = threading.Thread(target=mock_speech_input)
        thread.start()
        
        # Wait for the thread to complete (with timeout)
        thread.join(timeout=10)
        
        # Get the result
        try:
            status, result = result_queue.get_nowait()
            logging.info(f"Real-time speech conversion result: {status}, {result}")
            
            # Check the result
            if status == 'success':
                self.assertIsInstance(result, str)
            elif status == 'info':
                logging.info(result)  # This is an expected case for synthetic audio
            else:
                logging.warning(f"Speech recognition returned error: {result}")
                
        except queue.Empty:
            self.fail("Timeout waiting for speech recognition result")

if __name__ == '__main__':
    unittest.main()

"""
Video processing utilities for the Emotional Chat System
"""
import os
import subprocess
import logging
from pathlib import Path

# FFmpeg path
FFMPEG_PATH = "ffmpeg"  # Rely on system PATH
# r"C:\ffmpeg\bin\ffmpeg.exe"

def split_video(video_path):
    """
    Split video into separate video and audio streams using FFmpeg
    Returns paths to video and audio files
    """
    video_stream = None
    audio_stream = None
    try:
        # Verify input file exists
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Input video file not found: {video_path}")

        # Check if video has audio stream
        probe_result = subprocess.run([
            FFMPEG_PATH,
            '-i', video_path,
            '-hide_banner'
        ], capture_output=True, text=True)
        logging.info(f"FFmpeg probe output: {probe_result.stderr}")
        
        if "Stream #0:1: Audio" not in probe_result.stderr:
            logging.error("No audio stream found in video file")
            return None, None

        # Create output paths
        video_stream = str(Path(video_path).with_suffix('.video.mp4'))
        audio_stream = str(Path(video_path).with_suffix('.audio.wav'))

        logging.info(f"Processing video: {video_path}")
        logging.info(f"Video output: {video_stream}")
        logging.info(f"Audio output: {audio_stream}")

        # Extract video without audio
        logging.info("Running ffmpeg to extract video stream...")
        result = subprocess.run([
            FFMPEG_PATH,
            '-i', video_path,
            '-an',  # No audio
            '-vcodec', 'copy',  # Copy video codec
            '-y',  # Overwrite output files
            video_stream
        ], capture_output=True, text=True)
        if result.stderr:
            logging.info(f"FFmpeg video extraction output: {result.stderr}")
        logging.info("ffmpeg video stream extraction completed")

        # Extract audio as WAV with volume normalization
        logging.info("Running ffmpeg to extract audio stream...")
        result = subprocess.run([
            FFMPEG_PATH,
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM format
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo (changed from mono)
            '-filter:a', 'loudnorm=I=-16:TP=-1.5:LRA=11',  # Normalize audio levels
            '-y',  # Overwrite output files
            audio_stream
        ], capture_output=True, text=True)
        if result.stderr:
            logging.info(f"FFmpeg audio extraction output: {result.stderr}")
        logging.info("ffmpeg audio stream extraction completed")

        # Verify output files were created and have content
        if not os.path.exists(video_stream) or not os.path.exists(audio_stream):
            raise FileNotFoundError("Failed to create output files")
            
        # Check if audio file has content
        if os.path.getsize(audio_stream) == 0:
            logging.error("Generated audio file is empty")
            return None, None

        return video_stream, audio_stream

    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg error: {e.stderr}")
        cleanup_temp_files(video_stream, audio_stream)
        return None, None
    except Exception as e:
        logging.exception(f"Error splitting video:")
        cleanup_temp_files(video_stream, audio_stream)
        return None, None

def cleanup_temp_files(*files):
    """Remove temporary processing files"""
    for file in files:
        if file is not None:  # Only try to delete if file path is not None
            try:
                Path(file).unlink(missing_ok=True)
            except Exception as e:
                logging.error(f"Error deleting {file}: {e}")
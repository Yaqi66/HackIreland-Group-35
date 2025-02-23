"""
Video processing utilities for the Emotional Chat System
"""
import os
import subprocess
import logging
from pathlib import Path

# FFmpeg path
FFMPEG_PATH = "ffmpeg"  # Rely on system PATH

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
            '-i', video_path
        ], capture_output=True, text=True)
        logging.info(f"FFmpeg probe output: {probe_result.stderr}")
        
        # Create output paths
        video_stream = str(Path(video_path).with_suffix('.video.mp4'))
        audio_stream = str(Path(video_path).with_suffix('.audio.wav'))
        
        logging.info(f"Processing video: {video_path}")
        logging.info(f"Video output: {video_stream}")
        logging.info(f"Audio output: {audio_stream}")

        # Extract audio as WAV
        logging.info("Running ffmpeg to extract audio stream...")
        result = subprocess.run([
            FFMPEG_PATH,
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM format
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo
            '-y',  # Overwrite output files
            audio_stream
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.error(f"FFmpeg audio extraction failed: {result.stderr}")
            return None, None
            
        logging.info(f"FFmpeg audio extraction output: {result.stderr}")
        logging.info("ffmpeg audio stream extraction completed")

        # Extract video without audio
        logging.info("Running ffmpeg to extract video stream...")
        result = subprocess.run([
            FFMPEG_PATH,
            '-i', video_path,
            '-c:v', 'libx264',  # Use H.264 codec
            '-preset', 'ultrafast',
            '-y',  # Overwrite output files
            video_stream
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.error(f"FFmpeg video extraction failed: {result.stderr}")
            return None, None
            
        logging.info(f"FFmpeg video extraction output: {result.stderr}")
        logging.info("ffmpeg video stream extraction completed")

        # Verify output files were created and have content
        if not os.path.exists(audio_stream) or os.path.getsize(audio_stream) == 0:
            logging.error("Audio extraction failed or file is empty")
            return None, None

        if not os.path.exists(video_stream) or os.path.getsize(video_stream) == 0:
            logging.error("Video extraction failed or file is empty")
            return None, None

        return video_stream, audio_stream

    except Exception as e:
        logging.error(f"Error in split_video: {str(e)}")
        return None, None

def cleanup_temp_files(*files):
    """Remove temporary processing files"""
    for f in files:
        if f and os.path.exists(f):
            try:
                os.remove(f)
                logging.info(f"Removed temporary file: {f}")
            except Exception as e:
                logging.error(f"Error removing file {f}: {str(e)}")
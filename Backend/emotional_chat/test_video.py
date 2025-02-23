"""
Test script to verify video processing
"""
import os
import base64
import logging
from pathlib import Path
from src.emotional_speech_agent import EmotionalSpeechAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_test_video():
    """Create a test video file with known content"""
    import cv2
    import numpy as np
    from pathlib import Path
    import tempfile
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    video_path = temp_dir / 'test.webm'
    
    try:
        # Create a video writer
        fourcc = cv2.VideoWriter_fourcc(*'VP80')  # WebM codec
        out = cv2.VideoWriter(str(video_path), fourcc, 20.0, (640,480))
        
        # Create frames (2 seconds)
        for i in range(40):
            # Create a frame with changing text
            frame = np.zeros((480,640,3), np.uint8)
            cv2.putText(frame, f'Frame {i}', (200,240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            out.write(frame)
        
        out.release()
        logging.info(f"Created test video at: {video_path}")
        return video_path, temp_dir
        
    except Exception as e:
        logging.error(f"Error creating test video: {e}")
        return None, temp_dir

def test_video_processing():
    """Test video processing with a sample video"""
    temp_dir = None
    try:
        # Create a test video
        video_path, temp_dir = create_test_video()
        if not video_path:
            logging.error("Failed to create test video")
            return None
            
        logging.info("Testing video processing...")
        agent = EmotionalSpeechAgent()
        
        # Read video file as base64
        with open(video_path, 'rb') as f:
            video_bytes = f.read()
        video_base64 = base64.b64encode(video_bytes).decode('utf-8')
        
        # Process video directly
        result = agent.process_video(str(video_path))
        logging.info(f"Processing result: {result}")
        
        # Also test through the base64 method
        base64_result = {
            'video': video_base64
        }
        logging.info("Testing with base64 data...")
        logging.info(f"Video base64 length: {len(video_base64)}")
        
        return result
            
    except Exception as e:
        logging.exception("Error in test_video_processing:")
        return None
        
    finally:
        # Cleanup
        if temp_dir:
            try:
                for file in temp_dir.glob('*'):
                    file.unlink()
                temp_dir.rmdir()
                logging.info("Cleaned up temporary files")
            except Exception as e:
                logging.warning(f"Error during cleanup: {e}")

if __name__ == "__main__":
    print("\n=== Testing Video Processing ===")
    result = test_video_processing()
    if result and result.get('success'):
        print("\nVideo processing test successful!")
        print(f"Speech text: {result.get('speech_text', '')}")
        print(f"Emotions: {result.get('emotions', {})}")
        print(f"Response: {result.get('response', '')}")
    else:
        print("\nVideo processing test failed!")
        if result:
            print(f"Error: {result.get('error', 'Unknown error')}")
        print("Check the logs for more details.")

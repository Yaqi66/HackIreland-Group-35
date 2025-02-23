"""
Emotion monitoring module for real-time emotion detection using OpenCV
"""
import os
import cv2
import numpy as np
import logging
from pathlib import Path

class EmotionMonitor:
    """Class for monitoring emotions in video streams and frames using OpenCV"""
    
    def __init__(self):
        """Initialize the emotion monitor"""
        # Initialize face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Define emotion labels
        self.emotions = ['neutral', 'happy', 'sad', 'surprise', 'angry']
        
        # Initialize video capture
        self.cap = None
        self.running = False
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
    
    def process_video(self, video_path):
        """
        Process video file for emotion detection
        
        Args:
            video_path (str): Path to the video file
            
        Returns:
            list: List of detected emotions throughout the video
        """
        try:
            # Verify video file exists
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
                
            logging.info(f"Processing video for emotions: {video_path}")
            
            # Open video file
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception("Failed to open video file")
                
            emotions = []
            frame_count = 0
            
            while True:
                # Read frame
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Process every 5th frame to reduce processing time
                if frame_count % 5 == 0:
                    # Detect emotion in frame
                    frame_emotions = self.process_frame(frame)
                    if frame_emotions:
                        emotions.extend(frame_emotions)
                        
                frame_count += 1
                
            # Close video file
            cap.release()
            
            # Get most common emotions
            if emotions:
                unique_emotions = list(set(emotions))
                emotion_counts = [(emotion, emotions.count(emotion)) for emotion in unique_emotions]
                emotion_counts.sort(key=lambda x: x[1], reverse=True)
                top_emotions = [emotion for emotion, count in emotion_counts[:3]]
                return top_emotions
            else:
                return ['neutral']
                
        except Exception as e:
            logging.error(f"Error processing video: {str(e)}")
            return ['neutral']
    
    def process_frame(self, frame_data):
        """
        Process a single frame for emotion detection
        
        Args:
            frame_data (bytes or numpy.ndarray): Frame data either as bytes or numpy array
            
        Returns:
            list: Detected emotions in the frame
        """
        try:
            # Convert bytes to numpy array if needed
            if isinstance(frame_data, bytes):
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                frame = frame_data
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            frame_emotions = []
            
            # Process each face
            for (x, y, w, h) in faces:
                # Extract face ROI
                roi_gray = gray[y:y+h, x:x+w]
                
                # Simple emotion detection based on face features
                # This is a simplified approach - in production you would want to use a trained model
                emotion = self._detect_emotion_from_features(roi_gray)
                frame_emotions.append(emotion)
            
            return frame_emotions if frame_emotions else ['neutral']
            
        except Exception as e:
            logging.error(f"Error processing frame: {str(e)}")
            return ['neutral']
    
    def _detect_emotion_from_features(self, face_roi):
        """
        Simple emotion detection based on face features
        This is a basic implementation - in production use a trained model
        
        Args:
            face_roi (numpy.ndarray): Grayscale face region of interest
            
        Returns:
            str: Detected emotion
        """
        try:
            # Normalize image
            face_roi = cv2.resize(face_roi, (48, 48))
            face_roi = cv2.equalizeHist(face_roi)
            
            # Calculate features
            mean_intensity = np.mean(face_roi)
            std_intensity = np.std(face_roi)
            
            # Calculate gradients for edge detection
            sobelx = cv2.Sobel(face_roi, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(face_roi, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            edge_intensity = np.mean(gradient_magnitude)
            
            # More balanced emotion detection based on multiple features
            if edge_intensity > 40:  # High edge intensity might indicate strong expression
                if mean_intensity > 120:  # Brighter regions often indicate positive emotions
                    if std_intensity > 45:
                        return 'surprise'  # High contrast + bright + edges = surprise
                    else:
                        return 'happy'    # Moderate contrast + bright + edges = happy
                else:  # Darker regions with strong edges
                    if std_intensity > 45:
                        return 'angry'    # High contrast + dark + edges = angry
                    else:
                        return 'sad'      # Moderate contrast + dark + edges = sad
            else:  # Lower edge intensity suggests more neutral expression
                if std_intensity < 35:
                    return 'neutral'      # Low contrast + low edges = neutral
                else:
                    # Fallback based on intensity
                    return 'happy' if mean_intensity > 120 else 'neutral'
                
        except Exception as e:
            logging.error(f"Error detecting emotion from features: {str(e)}")
            return 'neutral'
    
    def start(self):
        """Start emotion monitoring"""
        if not self.running:
            self.running = True
            logging.info("Emotion monitoring started")
    
    def stop(self):
        """Stop emotion monitoring"""
        self.running = False
        if self.cap:
            self.cap.release()
        logging.info("Emotion monitoring stopped")

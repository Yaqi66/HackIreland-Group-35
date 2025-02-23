"""
EmotionalSpeechAgent: An agent that combines speech recognition and emotion-aware responses.
"""
import os
import cv2
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import json
import logging  # Import the logging module
from .emotion_monitor import EmotionMonitor
from .speech_converter import SpeechConverter
from .config import Config

# Load environment variables
load_dotenv()

class EmotionalSpeechAgent:
    def __init__(self):
        """Initialize the emotional speech agent with its components"""
        print("\nInitializing components...")
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)

        # Initialize components
        self.emotion_monitor = EmotionMonitor()
        self.speech_converter = SpeechConverter()
        self.running = False
        self.conversation_history = []
        print("Initialization complete!")

    def start(self):
        """Start the emotional speech agent"""
        print("\nStarting Emotional Speech Agent...")
        self.running = True
        self.emotion_monitor.start()
        self.run()

    def stop(self):
        """Stop the emotional speech agent"""
        print("\nStopping the system...")
        self.running = False
        self.emotion_monitor.stop()
        print("Emotion monitoring stopped")
        print("System stopped.")
        # Save conversation on exit
        self.save_conversation()

    def generate_emotion_aware_prompt(self, user_text, emotion_data):
        """Generate an emotion-aware prompt that focuses 90% on user's text and 10% on emotional state"""
        try:
            emotion = emotion_data['dominant_emotion']
            confidence = emotion_data.get('confidence', 0)

            prompt = f"""You are Eva, an empathetic AI assistant. Respond as naturally as possible to the user's input: '{user_text}'.
                      Maintain a conversational tone and keep the response concise (2-3 sentences).""" #Simplify general responses to follow.

            # Adjusting responses based on the emotions
            if emotion == "happy":
                prompt += " Given that the user may be happy, respond with enthusiasm. "
            elif emotion == "sad":
                prompt += " Given that the user sounds like they could use support, respond with empathy and encouragement. "
            elif emotion == "angry":
                prompt += " Given that the user may be frustrated, respond calmly and try to de-escalate where possible. "

            # Adjust emotional level on the confidence
            if emotion in ["happy", "sad", "angry"] and confidence < 50:
                prompt += " Note that the user is experiencing low emotion, focus primarily on the content of their message."

            return prompt
        except Exception as e:
            logging.error(f"An error occurred in generate_emotion_aware_prompt: {e}")
            return f"""You are Eva, an empathetic AI assistant. Respond as naturally as possible to the user's input: '{user_text}'.
                      Maintain a conversational tone and keep the response concise (2-3 sentences).""" #Return default
    
    def get_response(self, user_text, emotion_data):
        """Get AI response with 90% weight on user's text and 10% on emotional state"""
        try:
            # Generate the emotion-aware prompt
            prompt = self.generate_emotion_aware_prompt(user_text, emotion_data)

            # Get response from OpenAI
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt},
                ],
                model=Config.OPENAI_MODEL,
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE
            )

            # Extract the response text
            ai_response = response.choices[0].message.content.strip()

            # Store in conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_text': user_text,
                'emotion': emotion_data,
                'prompt': prompt,
                'response': ai_response
            })

            return ai_response

        except Exception as e:
            logging.error(f"Error getting AI response: {str(e)}", exc_info=True)
            return "I apologize, but I'm having trouble processing that right now. Could you please try again?"

    def process_interaction(self):
        """Process one round of user interaction"""
        try:
            # Get speech input
            text = self.speech_converter.listen_and_convert()
            if not text:
                return

            print(f"\nYou said: {text}")

            # Get current emotion
            emotion_data = self.emotion_monitor.get_dominant_emotion() #Should get the emotion
            print(f"\nDetected Emotion: {emotion_data['dominant_emotion']}") #Print dominant emotion
            print(f"Confidence: {emotion_data['confidence']:.1f}%") # Print confidence level

            # Get and speak response
            response = self.get_response(text, emotion_data)
            if response:
                print("\nAI Response:", response)
                self.speech_converter.convert_to_speech(response)

        except Exception as e:
            print(f"Error in interaction: {e}")

    def save_conversation(self):
        """Save the conversation history to a file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'conversation_{timestamp}.json'
            with open(filename, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            print(f"\nConversation saved to {filename}")
        except Exception as e:
            print(f"Error saving conversation history: {str(e)}")

    def process_video(self, video_path):
        """
        Process video file for emotion detection
        Args:
            video_path (str): Path to the video file
        Returns:
            dict: Dictionary containing success status and detected emotions
        """
        logging.info(f"Starting video processing for {video_path}")
        try:
            # Process video frames for emotion detection
            logging.info("Processing video frames for emotion detection...")
            detected_emotions = self.emotion_monitor.process_video(video_path)
            logging.info(f"Detected emotions: {detected_emotions}")
            
            if not detected_emotions:
                logging.warning("No emotions detected in the video")
                return {
                    'success': False,
                    'error': 'No emotions detected'
                }

            # Use sliding window to analyze emotions
            window_size = 5
            windows = []
            # Create windows of emotions
            for i in range(len(detected_emotions) - window_size + 1):
                window = detected_emotions[i:i + window_size]
                windows.append(window)

            # If we have fewer emotions than window size, just use what we have
            if not windows and detected_emotions:
                windows = [detected_emotions]

            # Calculate dominant emotion for each window
            window_dominants = []
            for window in windows:
                emotion_counts = {}
                for emotion in window:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                dominant = max(emotion_counts.items(), key=lambda x: x[1])[0]
                window_dominants.append(dominant)

            # Calculate overall emotion percentages
            total_windows = len(window_dominants)
            emotion_percentages = {}
            for emotion in set(window_dominants):
                count = window_dominants.count(emotion)
                emotion_percentages[emotion] = (count / total_windows) * 100

            # Get the final dominant emotion
            final_dominant = max(emotion_percentages.items(), key=lambda x: x[1])[0]
            logging.info(f"Final dominant emotion: {final_dominant}")
            logging.info(f"Emotion percentages: {emotion_percentages}")

            # Return the emotion analysis result
            return {
                'success': True,
                'emotions': {
                    'dominant': final_dominant,
                    'percentages': emotion_percentages
                }
            }

        except Exception as e:
            logging.exception(f"Error in process_video:")
            return {
                'success': False,
                'error': f'Failed to process video: {str(e)}'
            }

    def process_frame(self, frame_data):
        """
        Process a single video frame for emotion detection

        Args:
            frame_data (str): Base64 encoded image data

        Returns:
            dict: Dictionary containing success status and detected emotions
        """
        try:
            # Process frame for emotion detection
            emotions = self.emotion_monitor.process_frame(frame_data)

            return {
                'success': True,
                'emotions': emotions
            }

        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def run(self):
        """Run the main interaction loop"""
        try:
            print("\nReady for interaction! Press Ctrl+C to stop.")
            while self.running:
                self.process_interaction()

        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"Error: {e}")
            self.stop()

def main():
    """Run the emotional speech agent"""
    agent = EmotionalSpeechAgent()
    agent.start()

if __name__ == "__main__":
    main()
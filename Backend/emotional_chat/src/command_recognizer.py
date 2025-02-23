"""
Command recognition module for processing voice commands
"""
import logging
import openai
from .config import Config

class CommandRecognizer:
    """Class for recognizing and processing voice commands"""

    VALID_COMMANDS = {'news', 'play_music', 'show_image', 'play_youtube_video', 'none'}

    def __init__(self, openai_api_key):
        """Initialize the command recognizer with OpenAI client and prompt"""
        try:
            self.client = openai.OpenAI(api_key=openai_api_key)
            logging.info("CommandRecognizer initialized with OpenAI client")

            # Define the prompt in the constructor so it's only defined once
            self.prompt = """Identify the command in the User Speech. Return ONLY ONE WORD from these options: news, play_music, show_image, play_youtube_video, none.

Examples:
User Speech: play a song
Answer: play_music
User Speech: play a video
Answer: play_youtube_video
User Speech: show me my pictures
Answer: show_image
User Speech: get news
Answer: news
User Speech: tell me about weather
Answer: none

User Speech: {user_speech}
Answer:"""

        except Exception as e:
            logging.error(f"Error initializing OpenAI client: {e}")
            self.client = None
            self.prompt = None

    def recognize_command(self, user_speech):
        """
        Recognize commands from text input

        Args:
            user_speech (str): User's speech text to process

        Returns:
            str: Recognized command ('news', 'play_music', 'show_image', 'play_youtube_video')
                 or 'none' if no command is matched or an error occurs
        """
        try:
            if not self.client or not self.prompt:
                logging.warning("OpenAI client or prompt is not initialized.")
                return 'none'

            # Inject the user's speech into the prompt
            final_prompt = self.prompt.format(user_speech=user_speech)

            # Call the OpenAI API
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": final_prompt}],
                model=Config.OPENAI_MODEL,
                max_tokens=Config.MAX_TOKENS,
                temperature=0.3  # Lower temperature for more consistent responses
            )
            
            # Get the response and ensure it's a valid command
            command = response.choices[0].message.content.strip().lower()
            return command if command in self.VALID_COMMANDS else 'none'

        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return 'none'
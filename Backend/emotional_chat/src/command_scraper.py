"""
Module for handling command scraping and query generation
"""
from openai import OpenAI
import requests
import re
from urllib.parse import quote
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
from src.scraper import Scraper, search_youtube, search_image, Command
from src.config import Config

class commandScraper:
    def __init__(self):
        """Initialize the command scraper with OpenAI client"""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.mapping = {
            "news": "get_news",
            "play_music": "play_youtube",
            "show_image": "show_image",
            "play_youtube": "play_youtube"
        }
        self.messages = []

    def _generate_query(self, command_type: str, user_speech: str) -> str:
        """Generate an optimal search query using GPT"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates optimal search queries. Return ONLY the search query, nothing else."},
            {"role": "user", "content": f"Generate a search query for {command_type} based on: {user_speech}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=50,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating query: {e}")
            return user_speech  # Fallback to using the original speech as query

    def get_response(self, command_type: str, user_speech: str) -> Optional[Dict[str, Any]]:
        """
        Process user speech and return appropriate response based on command type
        Args:
            command_type: Type of command (news, play_music, show_image, etc.)
            user_speech: User's speech input
        Returns:
            dict containing response type and content (url, query, or articles)
        """
        try:
            # Map the command type to the appropriate function
            command = self.mapping.get(command_type)
            if not command:
                return None

            # First get GPT's interpretation of the user's request
            query = self._generate_query(command_type, user_speech)

            # Execute command based on type
            if command == "play_youtube":
                url = search_youtube(query)
                return {"type": command, "url": url, "query": query} if url else None
            elif command == "show_image":
                url = search_image(query)
                return {"type": command, "url": url, "query": query} if url else None
            elif command == "get_news":
                # Execute the news command directly
                result = Scraper.execute_command(Command("get_news", {}))
                return {"type": command, "articles": result} if result else None

            return None
        except Exception as e:
            print(f"Error in get_response: {e}")
            return None

    def get_conversation_response(self, user_speech: str) -> str:
        """
        Get a conversational response using the system prompt
        Args:
            user_speech: User's speech input
        Returns:
            str: AI's response
        """
        system_prompt = """You are a helpful and knowledgeable voice assistant that can answer questions, play YouTube videos, show images, and read news headlines. You're role is in a nursing home and you have been deployed to keep a particular patient engaged who may suffer from loneliness. Notes on the patient are attached below. It is **ESSENTIAL** that you use and refer to context in the notes to keep the patient grounded.

## Commands to Use for Different Features

You are able to invoke particular tools on request of the patient. Feel free to suggest some of these behaviours.

- For videos: [COMMAND:type=play_youtube,query=SEARCH_QUERY]
- For images: [COMMAND:type=show_image,query=SEARCH_QUERY]
- For news: [COMMAND:type=get_news] 

### Examples of Tool Use

- "Play Frank Sinatra" → [COMMAND:type=play_youtube,query=Frank Sinatra My Way]
- "Show me cats" → [COMMAND:type=show_image,query=cute cats]
- "What's in the news?" → [COMMAND:type=get_news]

## Guidelines for General Questions

- Be conversational and friendly
- Keep responses natural and conversational
- Give clear, concise, and accurate answers
- Keep responses under 3-4 sentences unless more detail is specifically requested
- You **NEVER** attempt produce news items without using the get_news function. Doing so leads to the risk of feeding false information to the patient.

## Remember

- For questions, give a brief answer first, then optionally suggest relevant media
- Use the conversation history to provide more contextual and relevant responses
- For media requests (play, watch, show, see, get news), **ALWAYS** include the appropriate command
- If there is something in the patient notes that might be useful, you use them
"""
        try:
            # Set up conversation messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_speech}
            ]
            
            # Get response from GPT
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in get_conversation_response: {e}")
            return "I apologize, but I'm having trouble understanding. Could you please try again?"
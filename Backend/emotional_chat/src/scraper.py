from openai import OpenAI
import requests
import re
from urllib.parse import quote
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional

@dataclass
class Command:
    name: str
    parameters: Dict[str, Any]

    @staticmethod
    def parse(command_str: str) -> Optional['Command']:
        """Parse a command string into a Command object"""
        if not command_str:
            return None
        command = {}
        for param in command_str.split(','):
            key, value = param.split('=')
            command[key.strip()] = value.strip()
        return Command(name=command.pop("type"), parameters=command)

class Scraper:
    @staticmethod
    def execute_command(command: Command) -> Optional[List[str]]:
        """Execute a command and return the result"""
        if command.name == "get_news":
            # Simplified news fetching
            return ["Sample news article 1", "Sample news article 2"]
        elif command.name == "play_youtube":
            url = search_youtube(command.parameters.get("query", ""))
            return [f"Youtube video presented successfully: {url}"] if url else None
        elif command.name == "show_image":
            url = search_image(command.parameters.get("query", ""))
            return [f"Image searched successfully: {url}"] if url else None
        return None

def search_youtube(query: str) -> Optional[str]:
    """Search YouTube and return the first video URL"""
    if not query:
        return None
    search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"An error occurred while searching YouTube: {e}")
        return None
    video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
    
    if video_ids:
        return f"https://www.youtube.com/watch?v={video_ids[0]}"
    return None

def search_image(query: str) -> Optional[str]:
    """Search and return the first image URL"""
    if not query:
        return None
    search_url = f"https://www.google.com/search?q={quote(query)}&tbm=isch"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"An error occurred while searching images: {e}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for img in soup.find_all('img'):
        if 'src' in img.attrs and 'http' in img['src']:
            return img['src']
    return None

def parse_commands(response: str) -> Tuple[str, List[Command]]:
    """Parse the response for any commands"""
    commands = []
    
    # Look for commands in the format: [COMMAND:type=play_youtube,query=Frank Sinatra]
    command_pattern = r'\[COMMAND:([^\]]+)\]'
    matches = re.finditer(command_pattern, response)

    for match in matches:
        command_str = match.group(1)
        command = Command.parse(command_str)
        commands.append(command)

    # Remove the command text from the response
    clean_response = re.sub(command_pattern, '', response)
    return clean_response, commands

def get_user_input():
    """Get user input through text"""
    text = input("\nType your message: ")
    return text

def main():
    print("Text-Based Assistant Started!")

    while True:
        try:
            # Get user input
            text = get_user_input()

            if text:
                print(f"\nYou typed: {text}")

                # Get ChatGPT response using conversation history
                # For simplicity, we assume the conversation history is empty
                response = "Sample response from ChatGPT"

                # Parse any commands in the response
                clean_response, commands = parse_commands(response)

                command_outputs = []

                # Execute any commands
                for command in commands:
                    command_output = Scraper.execute_command(command)
                    print(f"Command output: {command_output}")
                    command_outputs.append(command_output)

                # Print the clean response
                print(f"\nAssistant: {clean_response}\n")

        except KeyboardInterrupt:
            print("\nExiting text-based assistant...")
            break
        
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

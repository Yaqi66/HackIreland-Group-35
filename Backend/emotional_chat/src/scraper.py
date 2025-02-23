import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from openai import OpenAI
from dataclasses import dataclass
import os
import pyttsx3
from typing import List, Dict, Any, Tuple
import webbrowser
import requests
import re
from urllib.parse import quote
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from .database import get_patients, supabase as supabase_client, download_file, upload_file_to_bucket
from supabase import Client as SupabaseClient
from werkzeug.utils import secure_filename
from storage3.exceptions import StorageApiError

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

class ScraperBucket:
    """
    A class designed to cache the sites that we're scraping
    """
    
    def __init__(self, bucket_name: str, client: SupabaseClient):
        self.bucket_name = bucket_name
        self.supabase_client = client
    
    def scrape_page(self, url: str) -> BeautifulSoup:
        url_key = secure_filename(url)
        try:
            data = download_file(self.bucket_name, url_key)
        except StorageApiError as e:
            if int(e.status) != 404:
                # bubble the error
                raise e
            print(f'Could not find {url} in cache, going to download it')
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            upload_file_to_bucket(response.content, self.bucket_name, url_key)
            data = response.content
        return BeautifulSoup(data, features="html.parser")

class GoodNewsNetworkScraper:
    """A class that scrapes 'https://www.goodnewsnetwork.org/'"""
    
    def __init__(self, scraper: ScraperBucket):
        self.scraper = scraper

    def get_news_articles(self) -> List[str]:
        """Get positive news stories from Good News Network"""
        
        soup = self.scraper.scrape_page("https://www.goodnewsnetwork.org/")
        headlines = [header.find('a') for header in soup.find_all(class_='entry-title')]
        articles = []
        for headline in headlines[:5]:
            article_soup = scraper_bucket.scrape_page(headline['href'])
            paragraphs = [p.text for p in article_soup.find(class_='td-post-content').find_all('p')]
            articles.append("\n\n".join(paragraphs[:5]))
        return articles
        
scraper_bucket = ScraperBucket(bucket_name="scraper-cache", client=supabase_client)
good_news_network_scraper = GoodNewsNetworkScraper(scraper=scraper_bucket)

class Conversation:
    def __init__(self, patient):
        self.messages = []
        self.system_message = f"""You are a helpful and knowledgeable voice assistant that can answer questions, play YouTube videos, show images, and read news headlines. You're role is in a nursing home and you have been deployed to keep a particular patient engaged who may suffer from loneliness. Notes on the patient are attached below. It is **ESSENTIAL** that you use and refer to context in the notes to keep the patient grounded.

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
- You are to refer to and greet the patient by name.
- If relevant, offer to show related images or videos
- Use patient notes to provide context
- Keep responses under 3-4 sentences unless more detail is specifically requested
- You **NEVER** attempt produce news items without using the get_news function. Doing so leads to the risk of feeding false information to the patient.

## Remember

- For questions, give a brief answer first, then optionally suggest relevant media
- Use the conversation history to provide more contextual and relevant responses
- For media requests (play, watch, show, see, get news), **ALWAYS** include the appropriate command
- If there is something in the patient notes that might be useful, you use them

## Patient Notes

The patient's name is {patient['name']}.

{patient['notes']}
"""
        print(self.system_message)

        # Initialize with system message
        self.messages.append({"role": "system", "content": self.system_message})

    def add_message(self, role, content):
        """Add a message to the conversation history"""
        self.messages.append({"role": role, "content": content})

        # Keep only the last 10 messages to avoid hitting token limits
        if len(self.messages) > 11:  # 1 system message + 10 conversation messages
            self.messages = [self.messages[0]] + self.messages[-10:]

    def get_response(self):
        """Get a response from ChatGPT based on the conversation history"""
        try:
            # Get response from ChatGPT
            response = client.chat.completions.create(model="gpt-4o-mini", messages=self.messages)
            # Get the assistant's response
            assistant_response = response.choices[0].message.content
            # Add assistant's response to conversation
            self.add_message("assistant", assistant_response)
            return assistant_response

        except Exception as e:
            print(f"Error getting response from ChatGPT: {e}")
            return None

def speak_text(text):
    """Convert text to speech"""
    # engine.say(text)
    # engine.runAndWait()
    pass

def search_youtube(query):
    """Search YouTube and play the first video"""
    try:
        # Search for the video first
        search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
        response = requests.get(search_url)

        # Extract video ID using regex
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)

        if video_ids:
            # Get the first video ID and create a direct video URL
            video_id = video_ids[0]
            video_url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
            print(f"\nPlaying YouTube video: {video_url}")
            webbrowser.open(video_url)
            return True
        else:
            print("No videos found")
            return False

    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return False

def search_image(query):
    """Search and display the first image result"""
    try:
        # Try DuckDuckGo Images first
        search_url = f"https://duckduckgo.com/?q={quote(query)}&iax=images&ia=images"
        print(f"\nSearching for images of: {query}")
        webbrowser.open(search_url)
        return True

    except Exception as e:
        print(f"Error searching for images: {e}")
        return False

@dataclass
class Command:
    name: str
    parameters: Dict[str, Any]

    def format_parameters(self) -> str:
        return ", ".join(f"{key}={value}" for key, value in self.parameters.items())
    
    def start_output_sign(self) -> str:
        return f"[START COMMAND OUTPUT:{self.name} {self.format_parameters()}]"

    def end_output_sign(self) -> str:
        return f"[END COMMAND OUTPUT:{self.name} {self.format_parameters()}]"

def parse_commands(response: str) -> Tuple[str, List[Command]]:
    """Parse the response for any commands"""
    commands = []
    
    # Look for commands in the format: [COMMAND:type=play_youtube,query=Frank Sinatra]
    command_pattern = r'\[COMMAND:([^\]]+)\]'
    matches = re.finditer(command_pattern, response)

    for match in matches:
        command_str = match.group(1)
        command = {}
        for param in command_str.split(','):
            key, value = param.split('=')
            command[key.strip()] = value.strip()
        commands.append(Command(name=command.pop("type"), parameters=command))

    # Remove the command text from the response
    clean_response = re.sub(command_pattern, '', response)
    return clean_response, commands

def execute_command(command: Command) -> str:
    """Execute a command from the AI response and returns context for the LLM to use"""
    if command.name == "play_youtube":
        search_youtube(command.parameters["query"])
        return "Youtube video presented successfully"
    elif command.name == "show_image":
        search_image(command.parameters["query"])
        # TODO: USE CLIP OR SOMETHING TO PROVIDE IMAGE UNDERSTANDING
        return "Image searched successfully"
    elif command.name == "get_news":
        return "\n---\n".join(good_news_network_scraper.get_news_articles())
    return f"Could not find any command suitable for the invocation '{command}'"

def get_user_input(dev_mode=False):
    """Get user input either through voice or text"""
    if dev_mode:
        # Development mode - type input
        text = input("\nType your message (or 'switch' to toggle voice mode): ")
        if text.lower().strip() == 'switch':
            return None  # Signal to switch modes
        return text
    else:
        # Voice mode
        recording, sample_rate = record_audio()
        temp_file = save_audio(recording, sample_rate)
        return transcribe_audio(temp_file)

def record_audio(duration=5, sample_rate=44100):
    """Record audio from microphone"""
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    return recording, sample_rate

def save_audio(recording, sample_rate, filename="temp.wav"):
    """Save recorded audio to file"""
    wav.write(filename, sample_rate, recording)
    return filename

def transcribe_audio(filename):
    """Transcribe audio file using OpenAI's Whisper model"""
    try:
        with open(filename, "rb") as audio_file:
            transcript = client.audio.transcribe("whisper-1", audio_file)
            return transcript.text
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def load_patient_info():
    """Load patient information from JSON file"""
    
    return get_patients()[0]

def greet_patient():
    """Greet the patient by name"""
    patient_data = load_patient_info()
    greeting = f"Hello {patient_data['name']}! How can I help you today?"
    print(greeting)
    speak_text(greeting)

def main():
    print("Voice Assistant Started!")
    dev_mode = True  # Start in development mode by default
    print("Currently in DEVELOPMENT MODE (typing). Say 'switch' to toggle voice mode.")

    patient = load_patient_info()

    # Greet the patient
    greet_patient()

    # Initialize conversation
    conversation = Conversation(patient)
    
    while True:
        try:
            if not dev_mode:
                input("Press Enter to start recording...")

            # Get user input
            text = get_user_input(dev_mode)

            # Check if we need to switch modes
            if text is None:
                dev_mode = not dev_mode
                mode_name = "DEVELOPMENT" if dev_mode else "VOICE"
                print(f"\nSwitched to {mode_name} MODE")
                continue

            if text:
                print(f"\nYou {'typed' if dev_mode else 'said'}: {text}")

                # Get ChatGPT response using conversation history
                conversation.add_message("user", text)
                response = conversation.get_response()
                print("Raw response is:", response)
                if response:
                    # Parse any commands in the response
                    clean_response, commands = parse_commands(response)

                    command_outputs = []

                    # Execute any commands
                    for command in commands:
                        command_output = execute_command(command)
                        full_tool_context = f"""{command.start_output_sign()}
{command_output}
{command.end_output_sign()}"""
                        print(f"Raw log adding tool: {full_tool_context}")
                        command_outputs.append(full_tool_context)
                        conversation.add_message("assistant", command_output)

                    # Speak and print the clean response
                    print(f"\nAssistant: {clean_response}\n")
                    speak_text(clean_response)

                    next_response = conversation.get_response()
                    print(f"\nAssistant: {next_response}\n")
                    conversation.add_message("assistant", next_response)

        except KeyboardInterrupt:
            print("\nExiting voice assistant...")
            speak_text("Goodbye!")
            break
        
        except Exception as e:
            print(f"An error occurred: {e}")
            speak_text("Sorry, an error occurred.")

def test_command_invocation():
    command = Command(name="get_news", parameters={"hello":"world"})
    print(command.dump())

if __name__ == "__main__":
    main()
    
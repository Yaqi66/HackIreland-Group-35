import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import openai
import os
import pyttsx3
import webbrowser
import requests
import re
import json
from urllib.parse import quote
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from database import get_patients


# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

class Conversation:
    def __init__(self, patient):
        self.messages = []
        self.system_message = f"""You are a helpful and knowledgeable voice assistant that can answer questions, play YouTube videos, show images, and read news headlines.

        Use these commands for different features:
        1. For videos: [COMMAND:type=play_youtube,query=SEARCH_QUERY]
        2. For images: [COMMAND:type=show_image,query=SEARCH_QUERY]
        3. For news: [COMMAND:type=get_news] 
           

        Examples:
        - "Play Frank Sinatra" → [COMMAND:type=play_youtube,query=Frank Sinatra My Way]
        - "Show me cats" → [COMMAND:type=show_image,query=cute cats]
        - "What's in the news?" → [COMMAND:type=get_news]
        
        
        For general questions:
        - Give clear, concise, and accurate answers
        - Be conversational and friendly
        - If relevant, offer to show related images or videos
        - Keep responses under 3-4 sentences unless more detail is specifically requested
        - Reference previous parts of the conversation when relevant
        - Use patient notes to provide context 
        
        When asked about news:
        - Use the get_news command

        Remember:
        1. For media requests (play, watch, show, see), ALWAYS include the appropriate command
        2. For questions, give a brief answer first, then optionally suggest relevant media
        3. Keep responses natural and conversational
        4. Use the conversation history to provide more contextual and relevant responses
        5. IF THERE IS SOMETHING IN THE PATIENT NOTES THAT MIGHT BE relevant, suggest answers that use these notes         
        Notes on the patient:
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
    
    def get_response(self, user_input):
        """Get a response from ChatGPT based on the conversation history"""
        try:
            # Add user's input to conversation
            self.add_message("user", user_input)
            
            # Get response from ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages
            )
            
            # Get the assistant's response
            assistant_response = response.choices[0].message["content"]
            
            # Add assistant's response to conversation
            self.add_message("assistant", assistant_response)
            
            return assistant_response
            
        except Exception as e:
            print(f"Error getting response from ChatGPT: {e}")
            return None

def speak_text(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()

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

def get_news_headlines():
    """Get positive news stories from Good News Network"""
    try:
        # Good News Network main URL
        url = "https://www.goodnewsnetwork.org/"
        
        # Send request with headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find news headlines from the main content area
        headlines = []
        articles = soup.find_all('article', class_='post')[:5]  # Get first 5 articles
        
        for article in articles:
            # Get the headline
            headline_elem = article.find('h3', class_='entry-title') or article.find('h2', class_='entry-title')
            if headline_elem:
                headline = headline_elem.get_text().strip()
                # Get the date if available
                date_elem = article.find('time', class_='entry-date')
                date = date_elem.get_text().strip() if date_elem else ""
                
                if headline:
                    headlines.append((headline, date))
        
        if headlines:
            news_text = "Here are some positive news stories for you:\n\n"
            for i, (headline, date) in enumerate(headlines, 1):
                date_text = f" [{date}]" if date else ""
                news_text += f"{i}.{date_text} {headline}\n"
            return news_text
        else:
            return "Sorry, I couldn't find any positive news stories at the moment. Please try again later."
            
    except Exception as e:
        print(f"Error getting headlines: {e}")
        return "Sorry, I couldn't fetch the good news right now. Please try again later."

def execute_command(command):
    """Execute a command from the AI response"""
    if command.get("type") == "play_youtube":
        return search_youtube(command["query"])
    elif command.get("type") == "show_image":
        return search_image(command["query"])
    elif command.get("type") == "get_news":
        headlines = get_news_headlines()
        print(f"\n{headlines}")
        speak_text("Here are the latest headlines.")
        return True
    return False

def parse_commands(response):
    """Parse the response for any commands"""
    import re
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
        commands.append(command)
    
    # Remove the command text from the response
    clean_response = re.sub(command_pattern, '', response)
    return clean_response, commands

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
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1,
                      dtype=np.int16)
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
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            return transcript["text"]
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
                response = conversation.get_response(text)
                if response:
                    # Parse any commands in the response
                    clean_response, commands = parse_commands(response)
                    
                    # Execute any commands
                    for command in commands:
                        execute_command(command)
                    
                    # Speak and print the clean response
                    print(f"\nAssistant: {clean_response}\n")
                    speak_text(clean_response)
            
        except KeyboardInterrupt:
            print("\nExiting voice assistant...")
            speak_text("Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            speak_text("Sorry, an error occurred.")

if __name__ == "__main__":
    main()

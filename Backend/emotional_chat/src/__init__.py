"""
Emotional Chat System
A system that combines emotion recognition with speech interaction for elderly care.
Part of the HackIreland Project.
"""

from src.emotion_monitor import EmotionMonitor
from src.emotional_speech_agent import EmotionalSpeechAgent
from src.speech_converter import SpeechConverter

__version__ = '1.0.0'

__all__ = [
    'EmotionMonitor',
    'EmotionalSpeechAgent',
    'SpeechConverter'
]

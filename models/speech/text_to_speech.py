"""
Text-to-Speech module for multilingual offline speech synthesis
using pyttsx3 for cross-platform compatibility.
"""

import os
import yaml
import pyttsx3
import platform
import subprocess

def load_config(config_path='config/config.yaml'):
    """Load configuration settings from a YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class TextToSpeech:
    def __init__(self):
        """Initialize the TextToSpeech with the configured engine."""
        self.config = load_config()
        self.engine_name = self.config['speech']['tts']['engine']
        self.output_path = self.config['speech']['tts']['output_path']
        self.language = self.config['language']['default']
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_path, exist_ok=True)
        
        # Initialize the TTS engine
        if self.engine_name == "pyttsx3":
            self.engine = pyttsx3.init()
            self.setup_pyttsx3_voice()
        else:
            print(f"Warning: Unsupported TTS engine '{self.engine_name}', falling back to pyttsx3")
            self.engine_name = "pyttsx3"
            self.engine = pyttsx3.init()
            self.setup_pyttsx3_voice()
    
    def setup_pyttsx3_voice(self):
        """Setup pyttsx3 voice properties based on configuration."""
        # Set speech rate and volume
        self.engine.setProperty('rate', self.config['speech']['tts'].get('rate', 150))
        self.engine.setProperty('volume', self.config['speech']['tts'].get('volume', 1.0))
        
        # Try to set language-specific voice if available
        voices = self.engine.getProperty('voices')
        selected_voice = None
        
        # Language codes mapping (adjust based on your system's available voices)
        language_codes = {
            'english': ['en', 'english'],
            'urdu': ['ur', 'urdu'],
            'hindi': ['hi', 'hindi'],
            'punjabi': ['pa', 'punjabi']
        }
        
        # Get the codes for the current language
        target_codes = language_codes.get(self.language.lower(), ['en'])
        
        # Try to find a voice that matches the language
        for voice in voices:
            voice_id = voice.id.lower()
            voice_name = voice.name.lower()
            
            # Check if any of the target codes are in the voice ID or name
            if any(code in voice_id or code in voice_name for code in target_codes):
                selected_voice = voice.id
                break
        
        # If a matching voice was found, set it
        if selected_voice:
            self.engine.setProperty('voice', selected_voice)
            print(f"Set voice to {selected_voice} for {self.language}")
        else:
            print(f"No specific voice found for {self.language}, using default voice")
    
    def change_language(self, language):
        """Change the current language for speech synthesis."""
        if language in self.config['language']['supported']:
            self.language = language
            if self.engine_name == "pyttsx3":
                self.setup_pyttsx3_voice()
            return True
        else:
            print(f"Language {language} not supported")
            return False
    
    def speak(self, text, filename=None):
        """
        Convert text to speech and either play it or save to file.
        
        Args:
            text: Text to convert to speech
            filename: Optional filename to save the audio (without extension)
            
        Returns:
            Path to the saved audio file if filename is provided, None otherwise
        """
        if not text:
            print("Warning: Empty text provided to speak()")
            return None
        
        # With pyttsx3
        if self.engine_name == "pyttsx3":
            if filename:
                # Save to file
                output_file = os.path.join(self.output_path, f"{filename}.wav")
                self.engine.save_to_file(text, output_file)
                self.engine.runAndWait()
                print(f"Speech saved to {output_file}")
                return output_file
            else:
                # Speak immediately
                self.engine.say(text)
                self.engine.runAndWait()
                return None
    
    def list_available_voices(self):
        """List all available voices in the system."""
        if self.engine_name == "pyttsx3":
            voices = self.engine.getProperty('voices')
            print(f"Found {len(voices)} voices:")
            for i, voice in enumerate(voices):
                print(f"{i+1}. ID: {voice.id}")
                print(f"   Name: {voice.name}")
                print(f"   Languages: {voice.languages}")
                print(f"   Gender: {voice.gender}")
                print(f"   Age: {voice.age}")
                print()
            return voices
        return []

if __name__ == "__main__":
    tts = TextToSpeech()
    
    # List available voices
    print("Available voices:")
    tts.list_available_voices()
    
    # Test with different languages
    for lang in ['english', 'urdu']:
        if lang in tts.config['language']['supported']:
            print(f"\nTesting {lang} speech synthesis:")
            tts.change_language(lang)
            
            # Sample texts in different languages
            test_texts = {
                'english': "Hello, this is a test of the speech synthesis system.",
                'urdu': "السلام علیکم، یہ ایک ٹیسٹ ہے۔",
                'hindi': "नमस्ते, यह एक परीक्षण है।",
                'punjabi': "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਇਹ ਇੱਕ ਟੈਸਟ ਹੈ।"
            }
            
            # Get text for current language or use English as fallback
            text = test_texts.get(lang, test_texts['english'])
            
            # Speak and save to file
            print(f"Speaking: {text}")
            file_path = tts.speak(text, f"test_{lang}")
            
            # Speak directly
            tts.speak(f"Test completed for {lang}")
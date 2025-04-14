"""
Enhanced emotion detection module for multilingual support
with special focus on Roman Urdu using Ollama-hosted models.
"""

import yaml
import json
import os
import time
import requests
import sys
from pymongo import MongoClient
from pathlib import Path

# Add parent directory to path for importing modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Now import from utils package
from utils.transliteration import detect_language, urdu_to_roman, roman_to_urdu

def load_config(config_path='config/config.yaml'):
    """Load configuration settings from a YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class EmotionDetector:
    def __init__(self):
        """Initialize the EmotionDetector with Ollama API."""
        config = load_config()
        
        # MongoDB connection for logging
        try:
            self.client = MongoClient(config['mongodb']['uri'], serverSelectionTimeoutMS=2000)
            self.db = self.client[config['mongodb']['database']]
            self.collection = self.db[config['mongodb']['collection']]
            # Test the connection
            self.client.server_info()
            self.mongodb_available = True
        except Exception as e:
            print(f"Warning: MongoDB connection failed: {e}")
            print("Emotion detection will work, but interactions won't be logged to MongoDB")
            self.mongodb_available = False
        
        # Initialize Ollama API settings
        self.model_name = config['llm']['model_name']
        self.api_endpoint = f"{config['ollama']['api_url']}/generate"
        
        # Supported emotions
        self.supported_emotions = ['happy', 'sad', 'neutral', 'angry']
        
        # Language settings
        self.language = config['language']['default']
        self.supported_languages = config['language']['supported']
        
        # For Roman Urdu
        self.use_transliteration = True
    
    def change_language(self, language):
        """Change the current language for emotion detection."""
        if language in self.supported_languages:
            self.language = language
            if language == "urdu":
                self.use_transliteration = True
            else:
                self.use_transliteration = False
            return True
        else:
            print(f"Language {language} not supported")
            return False
    
    def detect_emotion(self, text):
        """
        Detect emotions in the provided text.
        
        Args:
            text: User input text
            
        Returns:
            List of detected emotions with labels and scores
        """
        if not text or not text.strip():
            return [{'label': 'neutral', 'score': 1.0}]
        
        # For Roman Urdu detection
        original_text = text
        if self.language == "urdu" and self.use_transliteration:
            # Detect if we need to transliterate
            lang_type = detect_language(text)
            if lang_type == "urdu_script":
                # Convert to Roman Urdu for better processing
                text = urdu_to_roman(text)
                print(f"Converted Urdu text to Roman Urdu: {text}")
        
        # Prepare prompt for emotion detection based on language
        prompt = self._create_emotion_detection_prompt(text)
        
        # Send request to the Ollama API
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": 0.1,  # Lower temperature for more deterministic results
            "num_predict": 50,   # Limit token generation
            "stream": False      # Disable streaming for simpler handling
        }
        
        try:
            # Send request to the Ollama API
            response = requests.post(self.api_endpoint, json=payload)
            
            if response.status_code != 200:
                print(f"Error from Ollama API: {response.text}")
                return [{'label': 'neutral', 'score': 1.0}]  # Default to neutral on error
            
            # Extract and parse emotion from response
            response_data = response.json()
            response_text = response_data.get('response', '').strip().lower()
            
            # Handle various response formats
            detected_emotions = []
            
            for emotion in self.supported_emotions:
                if emotion in response_text:
                    detected_emotions.append({
                        'label': emotion,
                        'score': 0.9  # Arbitrary high score since Ollama doesn't provide scores
                    })
            
            # If no emotions detected, default to neutral
            if not detected_emotions:
                if 'neutral' not in response_text:
                    detected_emotions.append({'label': 'neutral', 'score': 0.7})
                else:
                    detected_emotions.append({'label': 'neutral', 'score': 0.9})
            
            return detected_emotions
            
        except Exception as e:
            print(f"Error in emotion detection: {str(e)}")
            return [{'label': 'neutral', 'score': 1.0}]  # Default to neutral on error
    
    def _create_emotion_detection_prompt(self, text):
        """Create a prompt for emotion detection based on the current language."""
        # Multilingual prompts
        prompts = {
            'english': f"""
Analyze the following text and detect the primary emotion.
Text: "{text}"
Choose exactly one emotion from these options: happy, sad, neutral, angry.
Only respond with the emotion name, nothing else:
""",
            'urdu': f"""
Analyze the following Roman Urdu text and detect the primary emotion.
Text: "{text}"
Choose exactly one emotion from these options: happy, sad, neutral, angry.
Only respond with the emotion name, nothing else:
""",
            'hindi': f"""
निम्नलिखित टेक्स्ट का विश्लेषण करें और प्राथमिक भावना का पता लगाएं।
टेक्स्ट: "{text}"
इन विकल्पों में से एक भावना चुनें: खुश, दुखी, तटस्थ, क्रोधित।
केवल भावना के नाम के साथ प्रतिक्रिया दें, कुछ और नहीं:
""",
            'punjabi': f"""
ਹੇਠਾਂ ਦਿੱਤੇ ਟੈਕਸਟ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ ਅਤੇ ਮੁੱਖ ਭਾਵਨਾ ਦਾ ਪਤਾ ਲਗਾਓ।
ਟੈਕਸਟ: "{text}"
ਇਹਨਾਂ ਵਿਕਲਪਾਂ ਵਿੱਚੋਂ ਇੱਕ ਭਾਵਨਾ ਚੁਣੋ: ਖੁਸ਼, ਉਦਾਸ, ਨਿਰਪੱਖ, ਗੁੱਸੇ।
ਸਿਰਫ ਭਾਵਨਾ ਦੇ ਨਾਮ ਨਾਲ ਜਵਾਬ ਦਿਓ, ਹੋਰ ਕੁਝ ਨਹੀਂ:
"""
        }
        
        # Get prompt for current language or use English as fallback
        return prompts.get(self.language, prompts['english'])
    
    def log_interaction(self, user_input, emotions, response):
        """Log the interaction to MongoDB."""
        if not self.mongodb_available:
            return
            
        log = {
            'timestamp': time.time(),
            'user_input': user_input,
            'emotions_detected': emotions,
            'response': response,
            'language': self.language
        }
        
        try:
            self.collection.insert_one(log)
        except Exception as e:
            print(f"Error logging to MongoDB: {str(e)}")

if __name__ == "__main__":
    detector = EmotionDetector()
    
    # Test with different languages
    for lang in ['english', 'urdu']:
        if lang in detector.supported_languages:
            print(f"\nTesting {lang} emotion detection:")
            detector.change_language(lang)
            
            # Test sentences in different languages
            test_texts = {
                'english': [
                    "I'm so happy today!",
                    "I feel very sad and depressed.",
                    "This is just a normal statement.",
                    "I'm furious about what happened!"
                ],
                'urdu': [
                    "Main aaj bohat khush hoon!",  # Roman Urdu: I'm very happy today!
                    "Mujhe bohat afsoos aur udaasi mehsoos hoti hai.",  # Roman Urdu: I feel very sad and depressed
                    "Yeh ek aam bayan hai.",  # Roman Urdu: This is a normal statement
                    "Main is waqiye se bohat ghusay main hoon!",  # Roman Urdu: I'm very angry about this incident
                    "میں آج بہت خوش ہوں!",  # Urdu script: I'm very happy today!
                ]
            }
            
            # Get texts for current language or use English as fallback
            texts = test_texts.get(lang, test_texts['english'])
            
            for text in texts:
                print(f"\nInput: {text}")
                emotions = detector.detect_emotion(text)
                print(f"Detected emotions: {emotions}")
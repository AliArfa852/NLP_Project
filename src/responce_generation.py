"""
Enhanced response generation module for multilingual support
using Ollama-hosted models with special focus on Roman Urdu.
"""

import requests
import yaml
import json
import time
import sys
from pathlib import Path

# Add parent directory to path for importing modules
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, parent_dir)

from utils.transliteration import detect_language, urdu_to_roman, roman_to_urdu

def load_config(config_path='config/config.yaml'):
    """Load configuration settings from a YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class ResponseGenerator:
    def __init__(self):
        """Initialize the ResponseGenerator with the Ollama API endpoint and model."""
        config = load_config()
        self.model_name = config['llm']['model_name']
        self.api_endpoint = f"{config['ollama']['api_url']}/generate"
        
        # Language settings
        self.language = config['language']['default']
        self.supported_languages = config['language']['supported']
        
        # For Roman Urdu
        self.use_transliteration = True
    
    def change_language(self, language):
        """Change the current language for response generation."""
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
    
    def generate_response(self, user_input, emotions):
        """
        Generate a response using the Ollama API based on user input and detected emotions.
        
        Args:
            user_input: The text input from the user
            emotions: List of detected emotions with labels and scores
            
        Returns:
            Generated response text
        """
        if not user_input or not user_input.strip():
            return self._get_default_response('greeting')
        
        # Process for Roman Urdu if needed
        original_text = user_input
        if self.language == "urdu" and self.use_transliteration:
            # Detect if we need to transliterate
            lang_type = detect_language(user_input)
            if lang_type == "urdu_script":
                # Convert to Roman Urdu for better processing
                user_input = urdu_to_roman(user_input)
                print(f"Converted Urdu text to Roman Urdu for processing: {user_input}")
        
        # Create a prompt based on detected emotions and language
        prompt = self._create_response_generation_prompt(user_input, emotions)
        
        # Payload for the Ollama API
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True
        }
        
        try:
            # Send request to the Ollama API
            response = requests.post(self.api_endpoint, json=payload, stream=True)
            
            if response.status_code != 200:
                print(f"Error from Ollama API: {response.text}")
                return self._get_default_response('error')
            
            # Handle streamed response
            complete_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():  # Skip empty lines
                    try:
                        json_data = json.loads(line)
                        if "response" in json_data:
                            complete_response += json_data["response"]
                        if json_data.get("done", False):  # Stop if "done" is true
                            break
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON line: {line}\nError: {e}")
                        continue
            
            response_text = complete_response.strip()
            
            # Ensure response is in Roman Urdu for Urdu language
            if self.language == "urdu" and self.use_transliteration:
                # Check if response is in Urdu script
                lang_type = detect_language(response_text)
                if lang_type == "urdu_script":
                    # Convert to Roman Urdu
                    response_text = urdu_to_roman(response_text)
                    print(f"Converted response to Roman Urdu: {response_text}")
            
            return response_text
            
        except Exception as e:
            print(f"Error in response generation: {str(e)}")
            return self._get_default_response('error')
    
    def _create_response_generation_prompt(self, user_input, emotions):
        """Create a prompt for response generation based on emotions and current language."""
        # Extract emotion labels
        emotion_labels = [e['label'] for e in emotions]
        
        # Multilingual prompts
        prompts = {
            'english': f"""
You are a helpful and empathetic chatbot that responds to users based on their emotions.
User said: "{user_input}"
Detected emotions: {', '.join(emotion_labels)}

Generate a considerate response in English that acknowledges the user's emotions and provides appropriate support or engagement.
Keep your response concise (1-3 sentences):
""",
            'urdu': f"""
You are a helpful and empathetic chatbot that responds to users based on their emotions.
User said (in Roman Urdu): "{user_input}"
Detected emotions: {', '.join(emotion_labels)}

Generate a considerate response in ROMAN URDU that acknowledges the user's emotions and provides appropriate support or engagement.
Use simple Roman Urdu (English alphabet to write Urdu) so it's easy to read.
Keep your response concise (1-3 sentences):
""",
            'hindi': f"""
आप एक सहायक और संवेदनशील चैटबॉट हैं जो उपयोगकर्ताओं की भावनाओं के आधार पर प्रतिक्रिया देता है।
उपयोगकर्ता ने कहा: "{user_input}"
पता चली भावनाएँ: {', '.join(emotion_labels)}

हिंदी में एक विचारशील प्रतिक्रिया दें जो उपयोगकर्ता की भावनाओं को स्वीकार करती है और उचित समर्थन या जुड़ाव प्रदान करती है।
अपनी प्रतिक्रिया को संक्षिप्त रखें (1-3 वाक्य):
""",
            'punjabi': f"""
ਤੁਸੀਂ ਇੱਕ ਮਦਦਗਾਰ ਅਤੇ ਹਮਦਰਦ ਚੈਟਬੋਟ ਹੋ ਜੋ ਉਪਭੋਗਤਾਵਾਂ ਦੀਆਂ ਭਾਵਨਾਵਾਂ ਦੇ ਆਧਾਰ 'ਤੇ ਜਵਾਬ ਦਿੰਦਾ ਹੈ।
ਉਪਭੋਗਤਾ ਨੇ ਕਿਹਾ: "{user_input}"
ਪਤਾ ਲੱਗੀਆਂ ਭਾਵਨਾਵਾਂ: {', '.join(emotion_labels)}

ਪੰਜਾਬੀ ਵਿੱਚ ਇੱਕ ਵਿਚਾਰਸ਼ੀਲ ਜਵਾਬ ਤਿਆਰ ਕਰੋ ਜੋ ਉਪਭੋਗਤਾ ਦੀਆਂ ਭਾਵਨਾਵਾਂ ਨੂੰ ਸਵੀਕਾਰ ਕਰਦਾ ਹੈ ਅਤੇ ਢੁਕਵੀਂ ਸਹਾਇਤਾ ਜਾਂ ਸ਼ਮੂਲੀਅਤ ਪ੍ਰਦਾਨ ਕਰਦਾ ਹੈ।
ਆਪਣੇ ਜਵਾਬ ਨੂੰ ਸੰਖੇਪ ਰੱਖੋ (1-3 ਵਾਕ):
"""
        }
        
        # Get prompt for current language or use English as fallback
        return prompts.get(self.language, prompts['english'])
    
    def _get_default_response(self, response_type):
        """Get a default response based on type and current language."""
        # Default responses for different situations
        responses = {
            'greeting': {
                'english': "Hello! How are you feeling today?",
                'urdu': "آداب! آج آپ کیسا محسوس کر رہے ہیں؟",
                'hindi': "नमस्ते! आज आप कैसा महसूस कर रहे हैं?",
                'punjabi': "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਅੱਜ ਤੁਸੀਂ ਕਿਵੇਂ ਮਹਿਸੂਸ ਕਰ ਰਹੇ ਹੋ?"
            },
            'error': {
                'english': "I'm sorry, I'm having trouble processing that. Could you try again?",
                'urdu': "معذرت، مجھے اس کی پروسیسنگ میں دشواری ہو رہی ہے۔ کیا آپ دوبارہ کوشش کر سکتے ہیں؟",
                'hindi': "मुझे खेद है, मुझे इसे संसाधित करने में परेशानी हो रही है। क्या आप फिर से प्रयास कर सकते हैं?",
                'punjabi': "ਮੈਨੂੰ ਮਾਫ਼ ਕਰਨਾ, ਮੈਨੂੰ ਇਸ ਨੂੰ ਪ੍ਰੋਸੈਸ ਕਰਨ ਵਿੱਚ ਮੁਸ਼ਕਲ ਹੋ ਰਹੀ ਹੈ। ਕੀ ਤੁਸੀਂ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰ ਸਕਦੇ ਹੋ?"
            },
            'empty': {
                'english': "I didn't catch that. Could you please say something?",
                'urdu': "مجھے وہ نہیں ملا۔ کیا آپ کچھ کہہ سکتے ہیں؟",
                'hindi': "मुझे वह नहीं मिला। क्या आप कुछ कह सकते हैं?",
                'punjabi': "ਮੈਨੂੰ ਉਹ ਨਹੀਂ ਮਿਲਿਆ। ਕੀ ਤੁਸੀਂ ਕੁਝ ਕਹਿ ਸਕਦੇ ਹੋ?"
            }
        }
        
        # Get response for current language or use English as fallback
        language_responses = responses.get(response_type, responses['greeting'])
        return language_responses.get(self.language, language_responses['english'])

if __name__ == "__main__":
    generator = ResponseGenerator()
    
    # Test with different languages
    for lang in ['english', 'urdu']:
        if lang in generator.supported_languages:
            print(f"\nTesting {lang} response generation:")
            generator.change_language(lang)
            
            # Test inputs with different emotions
            test_inputs = [
                ("I'm so happy today!", [{'label': 'happy', 'score': 0.9}]),
                ("I feel very sad and depressed.", [{'label': 'sad', 'score': 0.9}]),
                ("This is just a normal statement.", [{'label': 'neutral', 'score': 0.9}]),
                ("I'm furious about what happened!", [{'label': 'angry', 'score': 0.9}])
            ]
            
            for user_input, emotions in test_inputs:
                print(f"\nUser: {user_input}")
                print(f"Emotions: {emotions}")
                response = generator.generate_response(user_input, emotions)
                print(f"Response: {response}")
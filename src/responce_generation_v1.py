"""
Enhanced response generation module for multilingual support
using Ollama-hosted models with special focus on Roman Urdu.
Includes Reinforcement Learning integration and personality customization.
"""

import requests
import yaml
import json
import time
import sys
import os
from pathlib import Path

# Add parent directory to path for importing modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Now import from utils package
from utils.transliteration import detect_language, urdu_to_roman, roman_to_urdu
from utils.personalities import get_personality_prompt, get_available_personalities

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
        
        # Personality settings
        self.personality = config.get('personality', {}).get('default', 'default')
        
        # Flag to enable/disable RL
        self.use_rl = config['rl'].get('enabled', True)
        
        # Initialize the reinforcement learning module
        try:
            from src.reinforcement_learning import ReinforcementLearner
            self.rl = ReinforcementLearner()
            self.rl_available = True
        except Exception as e:
            print(f"Warning: Could not initialize reinforcement learning: {e}")
            print("Response generation will work without learning capability")
            self.rl_available = False
    
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
    
    def change_personality(self, personality_id):
        """Change the chatbot's personality."""
        available_personalities = get_available_personalities()
        if personality_id in available_personalities:
            self.personality = personality_id
            print(f"Personality changed to: {available_personalities[personality_id]['name']}")
            return True
        else:
            print(f"Personality {personality_id} not available")
            return False
    
    def toggle_rl(self):
        """Toggle reinforcement learning on/off."""
        if not self.rl_available:
            print("Reinforcement learning module is not available")
            return False
            
        self.use_rl = not self.use_rl
        return self.use_rl
    
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
        
        # Extract primary emotion (highest score)
        primary_emotion = emotions[0]['label'] if emotions else 'neutral'
        
        # Process for Roman Urdu if needed
        original_text = user_input
        if self.language == "urdu" and self.use_transliteration:
            # Detect if we need to transliterate
            lang_type = detect_language(user_input)
            if lang_type == "urdu_script":
                # Convert to Roman Urdu for better processing
                user_input = urdu_to_roman(user_input)
                print(f"Converted Urdu text to Roman Urdu for processing: {user_input}")
        
        # Check if RL can suggest a response
        suggested_response = None
        enhanced_prompt = ""
        
        if self.use_rl and self.rl_available:
            suggested_response = self.rl.get_suggested_response(
                user_input, 
                primary_emotion, 
                self.language
            )
            
            # Get enhanced prompt from RL
            enhanced_prompt = self.rl.enhance_prompt(
                user_input, 
                primary_emotion, 
                self.language
            )
        
        # If we have a suggested response and we're not always exploring, use it
        if suggested_response:
            print("Using RL-suggested response")
            
            # Update RL model with this interaction (will calculate reward on next input)
            if self.rl_available:
                self.rl.update_with_response(
                    user_input, 
                    primary_emotion, 
                    suggested_response, 
                    primary_emotion,  # We don't know next emotion yet
                    self.language
                )
            
            return suggested_response
        
        # Create a prompt based on detected emotions, language, and personality
        base_prompt = self._create_response_generation_prompt(user_input, emotions)
        
        # If we have enhancements from RL, add them
        prompt = base_prompt
        if enhanced_prompt and self.use_rl and self.rl_available:
            prompt = f"{base_prompt}\n\n{enhanced_prompt}"
        
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
            
            # Update RL model with this interaction (will calculate reward on next input)
            if self.use_rl and self.rl_available:
                self.rl.update_with_response(
                    user_input, 
                    primary_emotion, 
                    response_text, 
                    primary_emotion,  # We don't know next emotion yet
                    self.language
                )
            
            return response_text
            
        except Exception as e:
            print(f"Error in response generation: {str(e)}")
            return self._get_default_response('error')
    
    def _create_response_generation_prompt(self, user_input, emotions):
        """Create a prompt for response generation based on emotions, language, and personality."""
        # Extract emotion labels
        emotion_labels = [e['label'] for e in emotions]
        
        # Get personality prompt
        personality_prompt = get_personality_prompt(self.personality, self.language)
        
        # Multilingual base prompts
        base_prompts = {
            'english': f"""
{personality_prompt}

User said: "{user_input}"
Detected emotions: {', '.join(emotion_labels)}

Generate a considerate response in English that acknowledges the user's emotions and provides appropriate support or engagement.
Keep your response concise (1-3 sentences):
""",
            'urdu': f"""
{personality_prompt}

User said (in Roman Urdu): "{user_input}"
Detected emotions: {', '.join(emotion_labels)}

Generate a considerate response in ROMAN URDU that acknowledges the user's emotions and provides appropriate support or engagement.
Use simple Roman Urdu (English alphabet to write Urdu) so it's easy to read.
Keep your response concise (1-3 sentences):
""",
            'hindi': f"""
{personality_prompt}

उपयोगकर्ता ने कहा: "{user_input}"
पता चली भावनाएँ: {', '.join(emotion_labels)}

हिंदी में एक विचारशील प्रतिक्रिया दें जो उपयोगकर्ता की भावनाओं को स्वीकार करती है और उचित समर्थन या जुड़ाव प्रदान करती है।
अपनी प्रतिक्रिया को संक्षिप्त रखें (1-3 वाक्य):
""",
            'punjabi': f"""
{personality_prompt}

ਉਪਭੋਗਤਾ ਨੇ ਕਿਹਾ: "{user_input}"
ਪਤਾ ਲੱਗੀਆਂ ਭਾਵਨਾਵਾਂ: {', '.join(emotion_labels)}

ਪੰਜਾਬੀ ਵਿੱਚ ਇੱਕ ਵਿਚਾਰਸ਼ੀਲ ਜਵਾਬ ਤਿਆਰ ਕਰੋ ਜੋ ਉਪਭੋਗਤਾ ਦੀਆਂ ਭਾਵਨਾਵਾਂ ਨੂੰ ਸਵੀਕਾਰ ਕਰਦਾ ਹੈ ਅਤੇ ਢੁਕਵੀਂ ਸਹਾਇਤਾ ਜਾਂ ਸ਼ਮੂਲੀਅਤ ਪ੍ਰਦਾਨ ਕਰਦਾ ਹੈ।
ਆਪਣੇ ਜਵਾਬ ਨੂੰ ਸੰਖੇਪ ਰੱਖੋ (1-3 ਵਾਕ):
"""
        }
        
        # Get prompt for current language or use English as fallback
        return base_prompts.get(self.language, base_prompts['english'])
    
    def _get_default_response(self, response_type):
        """Get a default response based on type, language, and personality."""
        # Base responses for different situations
        responses = {
            'greeting': {
                'default': {
                    'english': "Hello! How can I help you today?",
                    'urdu': "Assalam-o-alaikum! Main aap ki kya madad kar sakta hoon?",
                    'hindi': "नमस्ते! आज मैं आपकी क्या मदद कर सकता हूँ?",
                    'punjabi': "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਅੱਜ ਤੁਹਾਡੀ ਕੀ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?"
                },
                'therapist': {
                    'english': "Hello there. I'm here to listen and support you. How are you feeling today?",
                    'urdu': "Salam. Main aap ki baat sunne aur madad karne ke liye hazir hoon. Aaj aap kaisa mehsoos kar rahe hain?",
                    'hindi': "नमस्ते। मैं आपकी बात सुनने और आपका समर्थन करने के लिए यहां हूं। आज आप कैसा महसूस कर रहे हैं?",
                    'punjabi': "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ। ਮੈਂ ਤੁਹਾਡੀ ਗੱਲ ਸੁਣਨ ਅਤੇ ਸਹਿਯੋਗ ਦੇਣ ਲਈ ਇੱਥੇ ਹਾਂ। ਅੱਜ ਤੁਸੀਂ ਕਿਵੇਂ ਮਹਿਸੂਸ ਕਰ ਰਹੇ ਹੋ?"
                },
                'friend': {
                    'english': "Hey there! What's up? How's your day going?",
                    'urdu': "Oy! Kya ho raha hai? Aaj ka din kaisa jaa raha hai?",
                    'hindi': "अरे! क्या चल रहा है? आज का दिन कैसा जा रहा है?",
                    'punjabi': "ਓਏ! ਕੀ ਚੱਲ ਰਿਹਾ ਹੈ? ਅੱਜ ਦਾ ਦਿਨ ਕਿਵੇਂ ਜਾ ਰਿਹਾ ਹੈ?"
                },
                'coach': {
                    'english': "Hello there! Ready to make today amazing? Let's talk about what you want to achieve!",
                    'urdu': "Hello! Aaj ka din kamaal banane ke liye tayyar hain? Bataein, aap kya hasil karna chahte hain!",
                    'hindi': "नमस्ते! आज के दिन को अद्भुत बनाने के लिए तैयार हैं? बताइए, आप क्या हासिल करना चाहते हैं!",
                    'punjabi': "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਅੱਜ ਦੇ ਦਿਨ ਨੂੰ ਸ਼ਾਨਦਾਰ ਬਣਾਉਣ ਲਈ ਤਿਆਰ ਹੋ? ਦੱਸੋ, ਤੁਸੀਂ ਕੀ ਪ੍ਰਾਪਤ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ!"
                },
                'teacher': {
                    'english': "Hello! I'm here to help with any questions you might have. What would you like to learn about today?",
                    'urdu': "Salam! Main aap ke sawalon ka jawab dene ke liye maujood hoon. Aaj aap kya seekhna chahte hain?",
                    'hindi': "नमस्ते! मैं आपके किसी भी प्रश्न का उत्तर देने के लिए यहां हूं। आज आप क्या सीखना चाहते हैं?",
                    'punjabi': "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡੇ ਕਿਸੇ ਵੀ ਸਵਾਲ ਦਾ ਜਵਾਬ ਦੇਣ ਲਈ ਇੱਥੇ ਹਾਂ। ਅੱਜ ਤੁਸੀਂ ਕੀ ਸਿੱਖਣਾ ਚਾਹੁੰਦੇ ਹੋ?"
                },
                'poet': {
                    'english': "Greetings, wanderer of words! How dances your spirit on this journey through time?",
                    'urdu': "Salaam, alfaaz ke musafir! Is waqt ke safar mein aap ki rooh kis tarah raqs kar rahi hai?",
                    'hindi': "प्रणाम, शब्दों के यात्री! समय की इस यात्रा में आपकी आत्मा कैसे नृत्य कर रही है?",
                    'punjabi': "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ, ਸ਼ਬਦਾਂ ਦੇ ਯਾਤਰੀ! ਸਮੇਂ ਦੀ ਇਸ ਯਾਤਰਾ ਵਿੱਚ ਤੁਹਾਡੀ ਆਤਮਾ ਕਿਵੇਂ ਨੱਚ ਰਹੀ ਹੈ?"
                }
            },
            'error': {
                'default': {
                    'english': "I'm sorry, I'm having trouble processing that. Could you try again?",
                    'urdu': "Mujhe maaf kijiye, mujhe is ko process karne mein mushkil ho rahi hai. Kya aap dobara koshish kar sakte hain?",
                    'hindi': "मुझे खेद है, मुझे इसे संसाधित करने में परेशानी हो रही है। क्या आप फिर से प्रयास कर सकते हैं?",
                    'punjabi': "ਮੈਨੂੰ ਮਾਫ਼ ਕਰਨਾ, ਮੈਨੂੰ ਇਸ ਨੂੰ ਪ੍ਰੋਸੈਸ ਕਰਨ ਵਿੱਚ ਮੁਸ਼ਕਲ ਹੋ ਰਹੀ ਹੈ। ਕੀ ਤੁਸੀਂ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰ ਸਕਦੇ ਹੋ?"
                }
            },
            'empty': {
                'default': {
                    'english': "I didn't catch that. Could you please say something?",
                    'urdu': "Mujhe kuch sunai nahi diya. Kya aap kuch keh sakte hain?",
                    'hindi': "मुझे वह नहीं मिला। क्या आप कुछ कह सकते हैं?",
                    'punjabi': "ਮੈਨੂੰ ਉਹ ਨਹੀਂ ਮਿਲਿਆ। ਕੀ ਤੁਸੀਂ ਕੁਝ ਕਹਿ ਸਕਦੇ ਹੋ?"
                },
                'therapist': {
                    'english': "I'm listening whenever you're ready to share.",
                    'urdu': "Jab aap share karne ke liye tayyar hon, main sun raha hoon.",
                    'hindi': "जब आप साझा करने के लिए तैयार हों, मैं सुन रहा हूं।",
                    'punjabi': "ਜਦੋਂ ਤੁਸੀਂ ਸਾਂਝਾ ਕਰਨ ਲਈ ਤਿਆਰ ਹੋਵੋ, ਮੈਂ ਸੁਣ ਰਿਹਾ ਹਾਂ।"
                }
            }
        }
        
        # Get the appropriate responses for the current personality or default to 'default'
        personality_responses = responses.get(response_type, {}).get(self.personality)
        if not personality_responses:
            personality_responses = responses.get(response_type, {}).get('default')
        
        # If no personality-specific responses are found, use the default responses
        if not personality_responses:
            personality_responses = responses.get(response_type, {}).get('default', {})
            
        # Get response for current language or use English as fallback
        return personality_responses.get(self.language, personality_responses.get('english', "I'm here to help."))

if __name__ == "__main__":
    generator = ResponseGenerator()
    
    # Test with different personalities
    print("\nTesting different personalities:")
    personalities = ["default", "therapist", "friend", "coach", "teacher", "poet"]
    
    for personality in personalities:
        generator.change_personality(personality)
        print(f"\nPersonality: {personality}")
        
        # Test greeting in English
        generator.change_language("english")
        greeting = generator._get_default_response('greeting')
        print(f"English greeting: {greeting}")
        
        # Test greeting in Urdu
        generator.change_language("urdu")
        greeting = generator._get_default_response('greeting')
        print(f"Urdu greeting: {greeting}")
        
    # Test response generation with emotions
    print("\nTesting response generation:")
    generator.change_personality("default")
    generator.change_language("english")
    
    test_inputs = [
        ("I'm feeling really happy today!", [{'label': 'happy', 'score': 0.9}]),
        ("I'm so upset and angry right now.", [{'label': 'angry', 'score': 0.9}]),
        ("I feel sad and alone.", [{'label': 'sad', 'score': 0.9}])
    ]
    
    for user_input, emotions in test_inputs:
        print(f"\nUser: {user_input}")
        print(f"Emotions: {emotions}")
        
        # Test with different personalities
        for personality in personalities:
            generator.change_personality(personality)
            response = generator.generate_response(user_input, emotions)
            print(f"{personality.capitalize()}: {response}")
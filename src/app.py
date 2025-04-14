"""
Main application for multilingual emotion chatbot with speech capabilities.
Supports both text and speech interaction in multiple languages.
Works offline on both Windows and Linux platforms.
Specialized for Roman Urdu using Indian English voice model.
"""

import os
import sys
import time
import yaml
import platform
import json
import colorama
from datetime import datetime

# Initialize colorama for cross-platform colored terminal output
colorama.init()

# Add parent directory to path for importing modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import custom modules
from src.emotion_detection import EmotionDetector
from src.responce_generation import ResponseGenerator
from models.speech.text_to_speech import TextToSpeech
from models.speech.speech_to_text import SpeechToText
from src.database import Database
from src.reinforcement_learning import ReinforcementLearner
from utils.transliteration import detect_language, urdu_to_roman, roman_to_urdu

def load_config(config_path='config/config.yaml'):
    """Load configuration settings from a YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def clear_screen():
    """Clear terminal screen based on the operating system."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

class EmotionChatbotApp:
    def __init__(self):
        """Initialize the chatbot application with all components."""
        print("Initializing Multilingual Emotion Chatbot...")
        self.config = load_config()
        
        # Set initial language
        self.current_language = self.config['language']['default']
        print(f"Initial language set to: {self.current_language}")
        
        # Initialize components
        print("Loading components...")
        self.emotion_detector = EmotionDetector()
        self.response_generator = ResponseGenerator()
        self.tts = TextToSpeech()
        self.stt = SpeechToText()
        self.db = Database()
        self.rl = ReinforcementLearner()
        
        # Set input/output mode (text or speech)
        self.speech_input_enabled = False
        self.speech_output_enabled = True
        
        # Roman Urdu specific settings
        self.use_transliteration = True  # Enable transliteration for Urdu
        self.input_processor = self._process_input
        self.output_processor = self._process_output
        
        # Reinforcement learning settings
        self.use_rl = self.config['rl'].get('enabled', True)
        
        print("Initialization complete!")
    
    def _process_input(self, text):
        """
        Process input text before sending it to the emotion detection.
        For Roman Urdu mode, this ensures the text is in the correct format.
        
        Args:
            text: Input text from user
            
        Returns:
            Processed text ready for emotion detection
        """
        if not text:
            return text
            
        # Detect language and handle appropriately
        language = detect_language(text)
        
        if self.current_language == "urdu" and self.use_transliteration:
            if language == "urdu_script":
                # Convert from Urdu script to Roman Urdu
                return urdu_to_roman(text)
            else:
                # Assume it's already in Roman Urdu or another language
                return text
        else:
            # For other languages, no special processing
            return text
    
    def _process_output(self, text):
        """
        Process output text before displaying or speaking it.
        For Roman Urdu mode, this may convert between Roman and script forms.
        
        Args:
            text: Output text from response generator
            
        Returns:
            Processed text ready for display or speech
        """
        if not text:
            return text
            
        # For now, we're keeping output in the same format as generated
        # This could be extended to convert between scripts if needed
        return text
        
    def run(self):
        """Run the main chat loop."""
        clear_screen()
        welcome_message = self.get_localized_message("welcome")
        print(f"\n{colorama.Fore.CYAN}{welcome_message}{colorama.Style.RESET_ALL}")
        
        if self.speech_output_enabled:
            self.tts.speak(welcome_message)
        
        running = True
        
        # Track conversation state for RL
        previous_input = None
        previous_emotion = None
        
        while running:
            try:
                # Show prompt based on input mode
                if self.speech_input_enabled:
                    print(f"\n{colorama.Fore.YELLOW}{self.get_localized_message('speech_input_enabled')}{colorama.Style.RESET_ALL}")
                    time.sleep(0.5)  # Give user time to prepare
                    print("\007")  # ASCII bell (beep sound)
                    user_input = self.stt.transcribe_speech(duration=5)
                    # Process input (convert if necessary)
                    user_input = self.input_processor(user_input)
                    print(f"{colorama.Fore.GREEN}{self.get_localized_message('input_prompt')}{user_input}{colorama.Style.RESET_ALL}")
                else:
                    user_input = input(f"\n{colorama.Fore.GREEN}{self.get_localized_message('input_prompt')}{colorama.Style.RESET_ALL}")
                    # Process input (convert if necessary)
                    user_input = self.input_processor(user_input)
                
                # Check for special commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print(f"{colorama.Fore.CYAN}Goodbye!{colorama.Style.RESET_ALL}")
                    if self.speech_output_enabled:
                        self.tts.speak("Goodbye!")
                    break
                
                if user_input.lower() in ['options', 'menu', '/menu', '/options']:
                    self.show_options_menu()
                    continue
                
                if not user_input.strip():
                    continue
                
                # Process user input
                # Detect emotions
                emotions = self.emotion_detector.detect_emotion(user_input)
                emotion_labels = [e['label'] for e in emotions]
                primary_emotion = emotion_labels[0] if emotion_labels else 'neutral'
                
                print(f"{colorama.Fore.BLUE}Detected Emotions: {', '.join(emotion_labels)}{colorama.Style.RESET_ALL}")
                
                # If we have a previous input and RL is enabled, update the RL model
                if previous_input is not None and self.use_rl:
                    # Update RL model with new emotional state
                    self.rl.update(
                        previous_input,
                        previous_emotion,
                        primary_emotion,
                        self.current_language
                    )
                
                # Generate response
                response = self.response_generator.generate_response(user_input, emotions)
                
                # Process output (convert if necessary)
                processed_response = self.output_processor(response)
                
                print(f"{colorama.Fore.MAGENTA}{self.get_localized_message('bot_prefix')}{processed_response}{colorama.Style.RESET_ALL}")
                
                # Speak response if enabled
                if self.speech_output_enabled:
                    self.tts.speak(processed_response)
                
                # Log interaction
                log = {
                    'timestamp': datetime.now().isoformat(),
                    'language': self.current_language,
                    'original_input': user_input,
                    'emotions_detected': emotion_labels,
                    'response': response,
                    'speech_input': self.speech_input_enabled,
                    'speech_output': self.speech_output_enabled,
                    'transliteration_used': self.use_transliteration,
                    'rl_enabled': self.use_rl
                }
                self.db.insert_log(log)
                
                # Update conversation state for RL
                previous_input = user_input
                previous_emotion = primary_emotion
                
            except KeyboardInterrupt:
                print(f"\n{colorama.Fore.YELLOW}Interrupted{colorama.Style.RESET_ALL}")
                if self.show_options_menu():
                    running = False
            except Exception as e:
                print(f"{colorama.Fore.RED}Error: {str(e)}{colorama.Style.RESET_ALL}")
                continue
    
    def show_options_menu(self):
        """Show options menu and handle user selection."""
        speech_input_status = "enabled" if self.speech_input_enabled else "disabled"
        speech_output_status = "enabled" if self.speech_output_enabled else "disabled"
        transliteration_status = "enabled" if self.use_transliteration else "disabled"
        rl_status = "enabled" if self.use_rl else "disabled"
        
        # Display menu
        print(f"{colorama.Fore.YELLOW}")
        print("=" * 60)
        print("OPTIONS MENU")
        print("=" * 60)
        print(f"1. Change language (current: {self.current_language})")
        print(f"2. Toggle speech input (currently {speech_input_status})")
        print(f"3. Toggle speech output (currently {speech_output_status})")
        print(f"4. Toggle transliteration (currently {transliteration_status})")
        print(f"5. Toggle reinforcement learning (currently {rl_status})")
        print("6. View learning statistics")
        print("7. Reset learning data")
        print("8. Exit application")
        print("0. Return to chat")
        print("=" * 60)
        print(f"Your choice: {colorama.Style.RESET_ALL}", end="")
        
        try:
            choice = input()
            
            if choice == '0':
                return False  # Return to chat
            
            elif choice == '1':
                # Change language
                print(f"Available languages: {', '.join(self.config['language']['supported'])}")
                lang = input("Enter language: ").lower()
                if self.change_language(lang):
                    print(f"{colorama.Fore.GREEN}Language changed to {lang}{colorama.Style.RESET_ALL}")
                else:
                    print(f"{colorama.Fore.RED}Language {lang} not supported{colorama.Style.RESET_ALL}")
            
            elif choice == '2':
                # Toggle speech input
                self.speech_input_enabled = not self.speech_input_enabled
                status = "enabled" if self.speech_input_enabled else "disabled"
                print(f"{colorama.Fore.GREEN}Speech input {status}{colorama.Style.RESET_ALL}")
            
            elif choice == '3':
                # Toggle speech output
                self.speech_output_enabled = not self.speech_output_enabled
                status = "enabled" if self.speech_output_enabled else "disabled"
                print(f"{colorama.Fore.GREEN}Speech output {status}{colorama.Style.RESET_ALL}")
            
            elif choice == '4':
                # Toggle transliteration
                self.use_transliteration = not self.use_transliteration
                status = "enabled" if self.use_transliteration else "disabled"
                print(f"{colorama.Fore.GREEN}Transliteration {status}{colorama.Style.RESET_ALL}")
            
            elif choice == '5':
                # Toggle reinforcement learning
                self.use_rl = not self.use_rl
                self.response_generator.toggle_rl()
                status = "enabled" if self.use_rl else "disabled"
                print(f"{colorama.Fore.GREEN}Reinforcement learning {status}{colorama.Style.RESET_ALL}")
            
            elif choice == '6':
                # View learning statistics
                if self.use_rl:
                    stats = self.rl.get_statistics()
                    print(f"{colorama.Fore.CYAN}Learning Statistics:{colorama.Style.RESET_ALL}")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                    
                    # Show some example learned patterns
                    patterns = self.rl.memory.get_top_patterns(self.current_language, limit=3)
                    if patterns:
                        print(f"\n{colorama.Fore.CYAN}Top Learned Patterns:{colorama.Style.RESET_ALL}")
                        for pattern in patterns:
                            print(f"  {pattern['emotion_sequence']} (reward: {pattern['avg_reward']:.2f}, count: {pattern['count']})")
                            if pattern['successful_responses']:
                                responses = json.loads(pattern['successful_responses'])
                                for i, resp in enumerate(responses[:2]):
                                    print(f"    Response {i+1}: {resp[:50]}...")
                else:
                    print(f"{colorama.Fore.YELLOW}Reinforcement learning is currently disabled.{colorama.Style.RESET_ALL}")
            
            elif choice == '7':
                # Reset learning data
                if self.use_rl:
                    confirm = input(f"{colorama.Fore.RED}This will delete all learning data. Are you sure? (y/n): {colorama.Style.RESET_ALL}").lower()
                    if confirm == 'y':
                        self.rl.reset_memory()
                        print(f"{colorama.Fore.GREEN}Learning data has been reset.{colorama.Style.RESET_ALL}")
                else:
                    print(f"{colorama.Fore.YELLOW}Reinforcement learning is currently disabled.{colorama.Style.RESET_ALL}")
            
            elif choice == '8':
                # Exit
                print(f"{colorama.Fore.CYAN}Exiting application...{colorama.Style.RESET_ALL}")
                return True  # Exit the app
            
            else:
                print(f"{colorama.Fore.RED}Invalid choice{colorama.Style.RESET_ALL}")
            
            return False  # Don't exit the app
            
        except Exception as e:
            print(f"{colorama.Fore.RED}Error in menu: {str(e)}{colorama.Style.RESET_ALL}")
            return False
    
    def change_language(self, language):
        """Change the chatbot's language."""
        if language in self.config['language']['supported']:
            self.current_language = language
            print(f"Language changed to {language}")
            
            # Update language for speech components
            self.tts.change_language(language)
            self.stt.change_language(language)
            
            # For Urdu, ensure we're using Indian English model for TTS/STT
            if language == "urdu":
                self.tts.change_language("indian_english")
                self.stt.change_language("indian_english")
                self.use_transliteration = True
            else:
                self.use_transliteration = False
            
            message = self.get_localized_message("language_changed", language)
            print(message)
            if self.speech_output_enabled:
                self.tts.speak(message)
            
            return True
        else:
            print(f"Language {language} not supported")
            return False
    
    def get_localized_message(self, message_key, lang=None):
        """Get localized message based on the current language."""
        if not lang:
            lang = self.current_language
            
        # Messages for different languages
        messages = {
            "welcome": {
                "english": "Welcome to the multilingual emotion chatbot! How are you feeling today?",
                "urdu": "Multilingual emotion chatbot mein khush amdeed! Aaj aap kaisa mehsoos kar rahe hain?",
                "hindi": "बहुभाषी भावना चैटबॉट में आपका स्वागत है! आज आप कैसा महसूस कर रहे हैं?",
                "punjabi": "ਬਹੁਭਾਸ਼ੀ ਭਾਵਨਾ ਚੈਟਬੋਟ ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ! ਅੱਜ ਤੁਸੀਂ ਕਿਵੇਂ ਮਹਿਸੂਸ ਕਰ ਰਹੇ ਹੋ?"
            },
            "language_changed": {
                "english": f"Language changed to {lang}",
                "urdu": f"Language badal di gayi hai: {lang}",
                "hindi": f"भाषा बदली गई {lang}",
                "punjabi": f"ਭਾਸ਼ਾ ਬਦਲੀ ਗਈ {lang}"
            },
            "input_prompt": {
                "english": "You: ",
                "urdu": "Aap: ",
                "hindi": "आप: ",
                "punjabi": "ਤੁਸੀਂ: "
            },
            "bot_prefix": {
                "english": "Bot: ",
                "urdu": "Bot: ",
                "hindi": "बॉट: ",
                "punjabi": "ਬੋਟ: "
            },
            "speech_input_enabled": {
                "english": "Speech input enabled. Speak after the beep.",
                "urdu": "Awaaz input chalu hai. Beep ke baad bolein.",
                "hindi": "वाणी इनपुट सक्षम है। बीप के बाद बोलें।",
                "punjabi": "ਬੋਲੀ ਇਨਪੁਟ ਨੂੰ ਸਮਰੱਥ ਕੀਤਾ ਗਿਆ ਹੈ। ਬੀਪ ਤੋਂ ਬਾਅਦ ਬੋਲੋ।"
            },
            "options_menu": {
                "english": """
=== OPTIONS MENU ===
1. Change language
2. Toggle speech input (currently {})
3. Toggle speech output (currently {})
4. Toggle transliteration (used for Urdu)
5. Exit
0. Return to chat

Your choice: """,
                "urdu": """
=== OPTIONS MENU ===
1. Language badlein
2. Speech input toggle karein (is waqt {})
3. Speech output toggle karein (is waqt {})
4. Transliteration toggle karein (Urdu ke liye)
5. Exit
0. Chat par wapas jayen

Aap ka choice: """,
                "hindi": """
=== विकल्प मेनू ===
1. भाषा बदलें
2. वाणी इनपुट टॉगल करें (वर्तमान में {})
3. वाणी आउटपुट टॉगल करें (वर्तमान में {})
4. लिप्यंतरण टॉगल करें (उर्दू के लिए)
5. बाहर निकलें
0. चैट पर वापस जाएं

आपका विकल्प: """,
                "punjabi": """
=== ਵਿਕਲਪ ਮੇਨੂ ===
1. ਭਾਸ਼ਾ ਬਦਲੋ
2. ਬੋਲੀ ਇਨਪੁਟ ਟੌਗਲ ਕਰੋ (ਮੌਜੂਦਾ ਤੌਰ 'ਤੇ {})
3. ਬੋਲੀ ਆਉਟਪੁਟ ਟੌਗਲ ਕਰੋ (ਮੌਜੂਦਾ ਤੌਰ 'ਤੇ {})
4. ਲਿਪੀਅੰਤਰਣ ਟੌਗਲ ਕਰੋ (ਉਰਦੂ ਲਈ)
5. ਬਾਹਰ ਨਿਕਲੋ
0. ਚੈਟ 'ਤੇ ਵਾਪਸ ਜਾਓ

ਤੁਹਾਡੀ ਚੋਣ: """
            }
        }
        
        # Get the appropriate message for the current language or use English as fallback
        language_messages = messages.get(message_key, {})
        return language_messages.get(lang, language_messages.get('english', f"Message not found: {message_key}"))


def main():
    """Main function to run the application."""
    try:
        app = EmotionChatbotApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up colorama
        colorama.deinit()
        print("Goodbye!")

if __name__ == "__main__":
    main()
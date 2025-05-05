# """
# Text-to-Speech module for multilingual offline speech synthesis
# using pyttsx3 for cross-platform compatibility.
# """

# import os
# import yaml
# import pyttsx3
# import platform
# import subprocess

# def load_config(config_path='config/config.yaml'):
#     """Load configuration settings from a YAML file."""
#     with open(config_path, 'r') as file:
#         return yaml.safe_load(file)

# class TextToSpeech:
#     def __init__(self):
#         """Initialize the TextToSpeech with the configured engine."""
#         self.config = load_config()
#         self.engine_name = self.config['speech']['tts']['engine']
#         self.output_path = self.config['speech']['tts']['output_path']
#         self.language = self.config['language']['default']
        
#         # Create output directory if it doesn't exist
#         os.makedirs(self.output_path, exist_ok=True)
        
#         # Initialize the TTS engine
#         if self.engine_name == "pyttsx3":
#             self.engine = pyttsx3.init()
#             self.setup_pyttsx3_voice()
#         else:
#             print(f"Warning: Unsupported TTS engine '{self.engine_name}', falling back to pyttsx3")
#             self.engine_name = "pyttsx3"
#             self.engine = pyttsx3.init()
#             self.setup_pyttsx3_voice()
    
#     def setup_pyttsx3_voice(self):
#         """Setup pyttsx3 voice properties based on configuration."""
#         # Set speech rate and volume
#         self.engine.setProperty('rate', self.config['speech']['tts'].get('rate', 150))
#         self.engine.setProperty('volume', self.config['speech']['tts'].get('volume', 1.0))
        
#         # Try to set language-specific voice if available
#         voices = self.engine.getProperty('voices')
#         selected_voice = None
        
#         # Language codes mapping (adjust based on your system's available voices)
#         language_codes = {
#             'english': ['en', 'english'],
#             'urdu': ['ur', 'urdu'],
#             'hindi': ['hi', 'hindi'],
#             'punjabi': ['pa', 'punjabi']
#         }
        
#         # Get the codes for the current language
#         target_codes = language_codes.get(self.language.lower(), ['en'])
        
#         # Try to find a voice that matches the language
#         for voice in voices:
#             voice_id = voice.id.lower()
#             voice_name = voice.name.lower()
            
#             # Check if any of the target codes are in the voice ID or name
#             if any(code in voice_id or code in voice_name for code in target_codes):
#                 selected_voice = voice.id
#                 break
        
#         # If a matching voice was found, set it
#         if selected_voice:
#             self.engine.setProperty('voice', selected_voice)
#             print(f"Set voice to {selected_voice} for {self.language}")
#         else:
#             print(f"No specific voice found for {self.language}, using default voice")
    
#     def change_language(self, language):
#         """Change the current language for speech synthesis."""
#         if language in self.config['language']['supported']:
#             self.language = language
#             if self.engine_name == "pyttsx3":
#                 self.setup_pyttsx3_voice()
#             return True
#         else:
#             print(f"Language {language} not supported")
#             return False
    
#     def speak(self, text, filename=None):
#         """
#         Convert text to speech and either play it or save to file.
        
#         Args:
#             text: Text to convert to speech
#             filename: Optional filename to save the audio (without extension)
            
#         Returns:
#             Path to the saved audio file if filename is provided, None otherwise
#         """
#         if not text:
#             print("Warning: Empty text provided to speak()")
#             return None
        
#         # With pyttsx3
#         if self.engine_name == "pyttsx3":
#             if filename:
#                 # Save to file
#                 output_file = os.path.join(self.output_path, f"{filename}.wav")
#                 self.engine.save_to_file(text, output_file)
#                 self.engine.runAndWait()
#                 print(f"Speech saved to {output_file}")
#                 return output_file
#             else:
#                 # Speak immediately
#                 self.engine.say(text)
#                 self.engine.runAndWait()
#                 return None
    
#     def list_available_voices(self):
#         """List all available voices in the system."""
#         if self.engine_name == "pyttsx3":
#             voices = self.engine.getProperty('voices')
#             print(f"Found {len(voices)} voices:")
#             for i, voice in enumerate(voices):
#                 print(f"{i+1}. ID: {voice.id}")
#                 print(f"   Name: {voice.name}")
#                 print(f"   Languages: {voice.languages}")
#                 print(f"   Gender: {voice.gender}")
#                 print(f"   Age: {voice.age}")
#                 print()
#             return voices
#         return []

# if __name__ == "__main__":
#     tts = TextToSpeech()
    
#     # List available voices
#     print("Available voices:")
#     tts.list_available_voices()
    
#     # Test with different languages
#     for lang in ['english', 'urdu']:
#         if lang in tts.config['language']['supported']:
#             print(f"\nTesting {lang} speech synthesis:")
#             tts.change_language(lang)
            
#             # Sample texts in different languages
#             test_texts = {
#                 'english': "Hello, this is a test of the speech synthesis system.",
#                 'urdu': "السلام علیکم، یہ ایک ٹیسٹ ہے۔",
#                 'hindi': "नमस्ते, यह एक परीक्षण है।",
#                 'punjabi': "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਇਹ ਇੱਕ ਟੈਸਟ ਹੈ।"
#             }
            
#             # Get text for current language or use English as fallback
#             text = test_texts.get(lang, test_texts['english'])
            
#             # Speak and save to file
#             print(f"Speaking: {text}")
#             file_path = tts.speak(text, f"test_{lang}")
            
#             # Speak directly
#             tts.speak(f"Test completed for {lang}")



"""
Enhanced Text-to-Speech module with configurable human-like speech patterns
"""

import os
import yaml
import pyttsx3
import random
import time
import logging
from typing import Optional, Dict, List
import re
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/tts.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str = 'config/config.yaml') -> Dict:
    """Load configuration settings from YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info("Configuration loaded successfully")
            return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise

class TextToSpeech:
    def __init__(self, role: str = "default"):
        """
        Initialize TTS engine with configurable human-like speech patterns.
        
        Args:
            role: Voice role/profile to use (must exist in config)
        """
        self.config = load_config()
        self.engine_name = self.config['speech']['tts']['engine']
        self.output_path = self.config['speech']['tts']['output_path']
        self.language = self.config['language']['default']
        self.role = role
        
        # Load all TTS parameters from config
        tts_config = self.config['speech']['tts']
        
        self.base_rate = tts_config.get('base_rate', 150)
        self.base_volume = tts_config.get('base_volume', 1.0)
        self.default_gender = tts_config.get('default_gender', 'female')
        
        # Human-like speech parameters
        human_like = tts_config.get('human_like', {})
        self.human_like_enabled = human_like.get('enabled', True)
        self.pause_durations = human_like.get('pause_durations', {
            'comma': 0.3,
            'period': 0.7,
            'question': 0.5,
            'exclamation': 0.4
        })
        self.variation_range = human_like.get('variation_range', 0.2)
        self.emphasis_prob = human_like.get('emphasis', {}).get('probability', 0.6)
        self.min_word_len = human_like.get('emphasis', {}).get('min_word_length', 5)
        self.emphasis_level = human_like.get('emphasis', {}).get('level', 'moderate')
        
        # Conversation state parameters
        state_adj = tts_config.get('state_adjustments', {})
        self.rate_modifiers = state_adj.get('rate_modifiers', {
            'neutral': 1.0,
            'question': 0.9,
            'emphasis': 0.85,
            'explaining': 0.8,
            'excited': 1.2
        })
        self.volume_modifiers = state_adj.get('volume_modifiers', {
            'neutral': 1.0,
            'emphasis': 1.2,
            'question': 1.1,
            'explaining': 1.0,
            'excited': 1.15
        })
        
        # Initialize voice parameters
        self.conversation_state = "neutral"
        self._load_voice_profile()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_path, exist_ok=True)
        
        # Initialize the TTS engine
        self._init_engine()
        
        logger.info(f"Initialized TTS engine for {self.role} role in {self.language}")

    def _load_voice_profile(self):
        """Load voice profile settings based on current role."""
        try:
            voice_profiles = self.config['speech']['tts'].get('voice_profiles', {})
            profile = voice_profiles.get(self.role, voice_profiles.get('default', {}))
            
            # Set voice parameters (with fallbacks)
            self.voice_gender = profile.get('gender', self.default_gender)
            self.rate_modifier = profile.get('rate_modifier', 1.0)
            self.pitch_modifier = profile.get('pitch_modifier', 1.0)
            
            logger.info(f"Voice profile loaded - Gender: {self.voice_gender}, "
                      f"Rate Mod: {self.rate_modifier}, Pitch Mod: {self.pitch_modifier}")
        except Exception as e:
            logger.error(f"Error loading voice profile: {e}")
            # Fallback to defaults
            self.voice_gender = self.default_gender
            self.rate_modifier = 1.0
            self.pitch_modifier = 1.0

    def _init_engine(self):
        """Initialize the TTS engine with configured settings."""
        try:
            if self.engine_name == "pyttsx3":
                self.engine = pyttsx3.init()
                self._setup_pyttsx3_voice()
            else:
                logger.warning(f"Unsupported engine '{self.engine_name}', using pyttsx3")
                self.engine = pyttsx3.init()
                self._setup_pyttsx3_voice()
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise

    # def _setup_pyttsx3_voice(self):
    #     """Configure pyttsx3 voice properties."""
    #     # Set base properties
    #     self.engine.setProperty('rate', self.base_rate * self.rate_modifier)
    #     self.engine.setProperty('volume', self.base_volume)
        
    #     # Try to find matching voice
    #     voices = self.engine.getProperty('voices')
    #     selected_voice = None
        
    #     # Language codes mapping
    #     language_codes = {
    #         'english': ['en', 'english'],
    #         'urdu': ['ur', 'urdu'],
    #         'hindi': ['hi', 'hindi'],
    #         'punjabi': ['pa', 'punjabi']
    #     }
        
    #     target_codes = language_codes.get(self.language.lower(), ['en'])
        
    #     # Voice selection logic
    #     for voice in voices:
    #         voice_id = voice.id.lower()
    #         voice_name = voice.name.lower()
            
    #         # Check language and gender
    #         lang_match = any(code in voice_id or code in voice_name for code in target_codes)
    #         gender_match = self.voice_gender.lower() in voice_id or self.voice_gender.lower() in voice_name
            
    #         if lang_match and gender_match:
    #             selected_voice = voice.id
    #             break
        
    #     # Fallback to language match only
    #     if not selected_voice:
    #         for voice in voices:
    #             voice_id = voice.id.lower()
    #             if any(code in voice_id for code in target_codes):
    #                 selected_voice = voice.id
    #                 break
        
    #     # Set voice if found
    #     if selected_voice:
    #         self.engine.setProperty('voice', selected_voice)
    #         logger.info(f"Selected voice: {selected_voice}")
    #     else:
    #         logger.warning("No matching voice found, using default")
    def _setup_pyttsx3_voice(self):
        """
        Configure pyttsx3 voice properties with enhanced gender selection.
        This version ensures the voice matches the configured gender.
        """
        # Set base speech properties
        self.engine.setProperty('rate', self.base_rate * self.rate_modifier)
        self.engine.setProperty('volume', self.base_volume)
        
        # Get all available voices
        voices = self.engine.getProperty('voices')
        if not voices:
            logger.error("No voices available in the TTS engine!")
            return

        # Language codes mapping
        language_codes = {
            'english': ['en', 'english'],
            'urdu': ['ur', 'urdu'],
            'hindi': ['hi', 'hindi'],
            'punjabi': ['pa', 'punjabi']
        }
        
        target_codes = language_codes.get(self.language.lower(), ['en'])
        target_gender = self.voice_gender.lower()
        
        # Try preferred voices first (if specified in config)
        preferred_voices = self.config['speech']['tts'].get('voice_preferences', {})
        preferred_voice_id = preferred_voices.get(f"{self.language}_{target_gender}")
        
        if preferred_voice_id:
            for voice in voices:
                if voice.id == preferred_voice_id:
                    self.engine.setProperty('voice', voice.id)
                    logger.info(f"Using preferred voice: {voice.id}")
                    self._verify_voice_gender()
                    return

        # Voice selection logic with priority:
        # 1. Perfect match (language + gender)
        # 2. Language match only
        # 3. First female voice (if target is female)
        # 4. System default
        
        # Try to find perfect match first
        selected_voice = None
        for voice in voices:
            voice_id = voice.id.lower()
            voice_name = voice.name.lower()
            
            # Check language match
            lang_match = any(code in voice_id or code in voice_name for code in target_codes)
            
            # Check gender match (with multiple possible indicators)
            gender_keywords = {
                'female': ['female', 'woman', 'zira', 'hazel', 'eva'],
                'male': ['male', 'man', 'david', 'george', 'pavel']
            }
            gender_match = any(kw in voice_id or kw in voice_name 
                            for kw in gender_keywords.get(target_gender, []))
            
            if lang_match and gender_match:
                selected_voice = voice.id
                logger.debug(f"Found perfect match: {voice.id}")
                break
        
        # If no perfect match, try language only
        if not selected_voice:
            for voice in voices:
                voice_id = voice.id.lower()
                if any(code in voice_id for code in target_codes):
                    selected_voice = voice.id
                    logger.debug(f"Found language match: {voice.id}")
                    break
        
        # If still no match and we want female, try any female voice
        if not selected_voice and target_gender == 'female':
            for voice in voices:
                voice_id = voice.id.lower()
                if any(kw in voice_id for kw in ['female', 'woman', 'zira']):
                    selected_voice = voice.id
                    logger.debug(f"Found female voice: {voice.id}")
                    break
        
        # Set the selected voice
        if selected_voice:
            self.engine.setProperty('voice', selected_voice)
            logger.info(f"Selected voice: {selected_voice}")
        else:
            logger.warning("No matching voice found, using default")
        
        # Verify and enforce gender if needed
        self._verify_voice_gender()

    def _verify_voice_gender(self):
        """Verify and correct the voice gender if needed."""
        current_voice = self.engine.getProperty('voice').lower()
        target_gender = self.voice_gender.lower()
        
        # Define gender indicators
        female_indicators = ['female', 'woman', 'zira']
        male_indicators = ['male', 'man', 'david']
        
        # Check if current voice matches target gender
        if target_gender == 'female':
            if not any(indicator in current_voice for indicator in female_indicators):
                logger.warning(f"Voice gender mismatch! Expected female, got: {current_voice}")
                self._force_voice_gender()
        elif target_gender == 'male':
            if not any(indicator in current_voice for indicator in male_indicators):
                logger.warning(f"Voice gender mismatch! Expected male, got: {current_voice}")
                self._force_voice_gender()

    def _force_voice_gender(self):
        """Forcefully set a voice matching the configured gender."""
        voices = self.engine.getProperty('voices')
        if not voices:
            return
        
        target_gender = self.voice_gender.lower()
        gender_keywords = {
            'female': ['female', 'woman', 'zira'],
            'male': ['male', 'man', 'david']
        }.get(target_gender, [])
        
        # Try to find any voice matching gender keywords
        for voice in voices:
            voice_id = voice.id.lower()
            if any(kw in voice_id for kw in gender_keywords):
                self.engine.setProperty('voice', voice.id)
                logger.info(f"Forcefully set {target_gender} voice: {voice.id}")
                return
        
        # If no gendered voice found, try to find by language
        language_codes = {
            'english': ['en', 'english'],
            'urdu': ['ur', 'urdu'],
            'hindi': ['hi', 'hindi'],
            'punjabi': ['pa', 'punjabi']
        }
        target_codes = language_codes.get(self.language.lower(), ['en'])
        
        for voice in voices:
            voice_id = voice.id.lower()
            if any(code in voice_id for code in target_codes):
                self.engine.setProperty('voice', voice.id)
                logger.info(f"Fallback to language match: {voice.id}")
                return
        
        # Ultimate fallback - first available voice
        self.engine.setProperty('voice', voices[0].id)
        logger.warning(f"Using default voice: {voices[0].id}")
    def _add_speech_variations(self, text: str) -> str:
        """Add human-like variations to the text."""
        if not self.human_like_enabled:
            return text
            
        # Add pauses for punctuation
        processed_text = []
        for char in text:
            processed_text.append(char)
            if char in [',', '.', '?', '!']:
                pause_type = {
                    ',': 'comma',
                    '.': 'period',
                    '?': 'question',
                    '!': 'exclamation'
                }[char]
                base_pause = self.pause_durations[pause_type]
                varied_pause = base_pause * random.uniform(1 - self.variation_range, 1 + self.variation_range)
                processed_text.append(f'<break time="{int(varied_pause * 1000)}ms"/>')
        
        # Add word emphasis
        if random.random() < self.emphasis_prob:
            words = text.split()
            long_words = [w for w in words if len(w) >= self.min_word_len]
            if long_words:
                word_to_emphasize = random.choice(long_words)
                processed_text = [t.replace(word_to_emphasize, 
                                          f'<emphasis level="{self.emphasis_level}">{word_to_emphasize}</emphasis>') 
                                for t in processed_text]
        
        return ''.join(processed_text)

    def set_conversation_state(self, state: str):
        """Adjust speech parameters based on conversation state."""
        if state in self.rate_modifiers:
            self.conversation_state = state
            new_rate = self.base_rate * self.rate_modifier * self.rate_modifiers[state]
            new_volume = self.base_volume * self.volume_modifiers.get(state, 1.0)
            self.engine.setProperty('rate', new_rate)
            self.engine.setProperty('volume', new_volume)
            logger.info(f"Adjusted speech for state '{state}': rate={new_rate}, volume={new_volume}")
        else:
            logger.warning(f"Invalid conversation state: {state}")

    # def speak(self, text: str, filename: Optional[str] = None) -> Optional[str]:
    #     """Convert text to speech with human-like patterns."""
    #     if not text:
    #         logger.warning("Empty text provided")
    #         return None
            
    #     try:
    #         processed_text = self._add_speech_variations(text)
            
    #         if self.engine_name == "pyttsx3":
    #             if filename:
    #                 output_file = os.path.join(self.output_path, f"{filename}.wav")
    #                 self.engine.save_to_file(processed_text, output_file)
    #                 self.engine.runAndWait()
    #                 logger.info(f"Saved speech to {output_file}")
    #                 return output_file
    #             else:
    #                 # Split into chunks for natural pacing
    #                 chunks = self._split_into_chunks(processed_text)
    #                 for chunk in chunks:
    #                     self.engine.say(chunk)
    #                     self.engine.runAndWait()
    #                     time.sleep(random.uniform(0.1, 0.3))
    #                 return None
    #     except Exception as e:
    #         logger.error(f"Speech synthesis failed: {e}")
    #         return None
    def _sanitize_text(self, text: str) -> str:
        """
        Clean and prepare text for TTS by removing problematic characters
        and normalizing punctuation.
        """
        import re
        
        # Replace problematic characters with spaces
        text = re.sub(r"['\"`]", ' ', text)
        
        # Replace other special characters (keep basic punctuation)
        text = re.sub(r"[^\w\s.,!?;:-]", ' ', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove trailing punctuation
        text = text.rstrip('.,!?;:-')
        
        return text

    def _add_speech_variations(self, text: str) -> str:
        """Add human-like variations to sanitized text."""
        if not self.human_like_enabled:
            return self._sanitize_text(text)
        
        # First sanitize the text
        clean_text = self._sanitize_text(text)
        processed_text = []
        
        # Track if we're in an XML tag (like <break> or <emphasis>)
        in_tag = False
        tag_buffer = ""
        
        for char in clean_text:
            if char == '<':
                in_tag = True
                tag_buffer = "<"
                continue
            
            if in_tag:
                tag_buffer += char
                if char == '>':
                    processed_text.append(tag_buffer)
                    in_tag = False
                continue
            
            processed_text.append(char)
            
            # Add pauses for punctuation (only when not in tag)
            if char in [',', '.', '?', '!']:
                pause_type = {
                    ',': 'comma',
                    '.': 'period',
                    '?': 'question',
                    '!': 'exclamation'
                }[char]
                base_pause = self.pause_durations[pause_type]
                varied_pause = base_pause * random.uniform(1 - self.variation_range, 1 + self.variation_range)
                processed_text.append(f'<break time="{int(varied_pause * 1000)}ms"/>')
        
        # Convert back to string
        result = ''.join(processed_text)
        
        # Add word emphasis (only if text is long enough)
        if len(clean_text.split()) > 3 and random.random() < self.emphasis_prob:
            words = [w for w in clean_text.split() if len(w) >= self.min_word_len and not any(c in w for c in '<>')]
            if words:
                word_to_emphasize = random.choice(words)
                result = result.replace(word_to_emphasize, f'<emphasis level="{self.emphasis_level}">{word_to_emphasize}</emphasis>')
        
        return result

    # def speak(self, text: str, filename: Optional[str] = None) -> Optional[str]:
    #     """Convert sanitized text to speech with human-like patterns."""
    #     if not text:
    #         logger.warning("Empty text provided")
    #         return None
            
    #     try:
    #         # First sanitize the text, then add variations
    #         processed_text = self._add_speech_variations(text)
            
    #         if self.engine_name == "pyttsx3":
    #             if filename:
    #                 output_file = os.path.join(self.output_path, f"{filename}.wav")
    #                 self.engine.save_to_file(processed_text, output_file)
    #                 self.engine.runAndWait()
    #                 logger.info(f"Saved speech to {output_file}")
    #                 return output_file
    #             else:
    #                 # Split into chunks for natural pacing
    #                 chunks = self._split_into_chunks(processed_text)
    #                 for chunk in chunks:
    #                     self.engine.say(chunk)
    #                     self.engine.runAndWait()
    #                     time.sleep(random.uniform(0.1, 0.3))
    #                 return None
    #     except Exception as e:
    #         logger.error(f"Speech synthesis failed: {e}")
    #         return None
    # def _split_into_chunks(self, text: str, max_length: int = 150) -> List[str]:
    #     """Split text into natural sounding chunks."""
    #     if len(text) <= max_length:
    #         return [text]
            
    #     # Try to split at punctuation first
    #     for punct in ['.', '?', '!', ';']:
    #         if punct in text:
    #             parts = [p + punct for p in text.split(punct) if p.strip()]
    #             if all(len(p) <= max_length for p in parts):
    #                 return parts
        
    #     # Fallback to space splitting
    #     words = text.split()
    #     chunks = []
    #     current_chunk = []
    #     current_len = 0
        
    #     for word in words:
    #         if current_len + len(word) + 1 <= max_length:
    #             current_chunk.append(word)
    #             current_len += len(word) + 1
    #         else:
    #             chunks.append(' '.join(current_chunk))
    #             current_chunk = [word]
    #             current_len = len(word)
        
    #     if current_chunk:
    #         chunks.append(' '.join(current_chunk))
        
    #     return chunks
    def _sanitize_text(self, text: str) -> str:
        """Clean text by removing problematic characters."""
        # Remove special chars but keep basic punctuation
        text = re.sub(r"[^\w\s,.!?\-]", ' ', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text

    def _split_with_pauses(self, text: str) -> List[tuple[str, float]]:
        """Split text into (sentence, pause_time) pairs."""
        parts = re.split(r'([,.!?])', text)
        sentences = []
        current_sentence = ""
        
        for i, part in enumerate(parts):
            if part in [',', '.', '!', '?']:
                current_sentence += part
                pause_type = {
                    ',': 'comma',
                    '.': 'period',
                    '!': 'exclamation',
                    '?': 'question'
                }[part]
                base_pause = self.pause_durations[pause_type]
                varied_pause = base_pause * random.uniform(1 - self.variation_range, 1 + self.variation_range)
                sentences.append((current_sentence, varied_pause))
                current_sentence = ""
            else:
                current_sentence += part
        
        if current_sentence:
            sentences.append((current_sentence, 0))
        
        return sentences

    def speak(self, text: str, filename: Optional[str] = None) -> Optional[str]:
        """Convert text to speech with natural pauses."""
        if not text:
            logging.warning("Empty text provided")
            return None
            
        try:
            clean_text = self._sanitize_text(text)
            
            if filename:
                output_file = os.path.join(self.output_path, f"{filename}.wav")
                self.engine.save_to_file(clean_text, output_file)
                self.engine.runAndWait()
                return output_file
            else:
                if self.human_like_enabled:
                    sentences = self._split_with_pauses(clean_text)
                    for sentence, pause_duration in sentences:
                        if sentence.strip():
                            self.engine.say(sentence.strip())
                            self.engine.runAndWait()
                        if pause_duration > 0:
                            time.sleep(pause_duration)
                else:
                    self.engine.say(clean_text)
                    self.engine.runAndWait()
                return None
        except Exception as e:
            logging.error(f"Speech synthesis failed: {e}")
            return None
    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks, handling our custom pause markers."""
        # First split by our pause markers
        parts = re.split(r'(\|\|PAUSE_\d+\|\|)', text)
        chunks = []
        current_chunk = []
        
        for part in parts:
            if part.startswith('||PAUSE_'):
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                    current_chunk = []
                chunks.append(part)  # Add pause as separate chunk
            else:
                current_chunk.append(part)
        
        if current_chunk:
            chunks.append(''.join(current_chunk))
        
        return chunks
    def list_available_voices(self) -> List:
        """List all available voices in the system."""
        if self.engine_name == "pyttsx3":
            voices = self.engine.getProperty('voices')
            logger.info("Available voices:")
            for i, voice in enumerate(voices):
                logger.info(f"{i+1}. ID: {voice.id}")
                logger.info(f"   Name: {voice.name}")
                logger.info(f"   Languages: {voice.languages}")
                logger.info(f"   Gender: {voice.gender}")
            return voices
        return []

if __name__ == "__main__":
    # Example usage
    tts = TextToSpeech(role="call_center")
    tts.list_available_voices()
    
    # Test different states
    test_text = "Hello, this is a test of the human-like speech system. " \
                "Notice how the pacing and emphasis change based on context?"
    
    for state in ['neutral', 'question', 'emphasis', 'explaining']:
        print(f"\nTesting '{state}' state:")
        tts.set_conversation_state(state)
        tts.speak(test_text)
    
    # Save to file
    tts.speak("This will be saved to a file.", "test_output")
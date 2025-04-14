"""
Speech-to-Text module for multilingual offline speech recognition
using Vosk for offline recognition.
"""

import os
import yaml
import json
import wave
import sounddevice as sd
import soundfile as sf
import numpy as np
from vosk import Model, KaldiRecognizer, SetLogLevel

def load_config(config_path='config/config.yaml'):
    """Load configuration settings from a YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class SpeechToText:
    def __init__(self):
        """Initialize the SpeechToText with the configured engine."""
        self.config = load_config()
        self.engine = self.config['speech']['stt']['engine']
        self.model_path = self.config['speech']['stt']['model_path']
        self.language = self.config['language']['default']
        
        # Set Vosk logging to errors only
        SetLogLevel(-1)
        
        # Initialize the language model
        self.load_language_model(self.language)
        
        # Audio recording settings
        self.sample_rate = 16000
        self.channels = 1
    
    def load_language_model(self, language):
        """Load a specific language model."""
        if self.engine == "vosk":
            # Get model path for the selected language
            lang_model = self.config['language']['models'].get(language)
            if not lang_model:
                # Fall back to English if the requested language model isn't configured
                lang_model = self.config['language']['models']['english']
                print(f"Warning: Model for {language} not found, falling back to English")
            
            # Construct full model path
            model_dir = os.path.join(self.model_path, lang_model.replace("vosk-model-", ""))
            
            # Check if model exists
            if not os.path.exists(model_dir):
                raise FileNotFoundError(f"Language model not found at {model_dir}")
            
            # Load the Vosk model
            self.model = Model(model_dir)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            
            print(f"Loaded {language} speech recognition model")
            self.language = language
    
    def change_language(self, language):
        """Change the current language for speech recognition."""
        if language in self.config['language']['supported']:
            self.load_language_model(language)
            return True
        else:
            print(f"Language {language} not supported")
            return False
    
    def record_audio(self, duration=5, filename=None):
        """
        Record audio for a specified duration.
        
        Args:
            duration: Recording duration in seconds
            filename: Optional filename to save the recorded audio
            
        Returns:
            Audio data as numpy array if filename is None, otherwise saves to file
        """
        print(f"Recording for {duration} seconds...")
        
        # Record audio
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16'
        )
        sd.wait()  # Wait until recording is finished
        
        # Save audio to file if filename is provided
        if filename:
            output_path = os.path.join(self.config['speech']['tts']['output_path'], filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            sf.write(output_path, audio_data, self.sample_rate)
            print(f"Audio saved to {output_path}")
            return output_path
        
        return audio_data
    
    def transcribe_audio_file(self, audio_file):
        """
        Transcribe speech from an audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        # Process with Vosk
        if self.engine == "vosk":
            wf = wave.open(audio_file, "rb")
            
            # Check if the audio format is compatible with Vosk
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                raise ValueError("Audio file must be WAV format mono PCM.")
            
            # Process the audio file in chunks
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if 'text' in result and result['text']:
                        results.append(result['text'])
            
            # Get final result
            final_result = json.loads(self.recognizer.FinalResult())
            if 'text' in final_result and final_result['text']:
                results.append(final_result['text'])
            
            return " ".join(results)
    
    def transcribe_speech(self, duration=5):
        """
        Record and transcribe speech.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text
        """
        # Record audio to temporary file
        temp_file = os.path.join(self.config['speech']['tts']['output_path'], "temp_recording.wav")
        self.record_audio(duration, temp_file)
        
        # Transcribe the recorded audio
        transcription = self.transcribe_audio_file(temp_file)
        
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return transcription

if __name__ == "__main__":
    stt = SpeechToText()
    
    # Test with different languages
    for lang in ['english', 'urdu']:
        if lang in stt.config['language']['supported']:
            print(f"\nTesting {lang} speech recognition:")
            stt.change_language(lang)
            
            # Record and transcribe
            print("Say something...")
            result = stt.transcribe_speech(duration=5)
            print(f"Transcription: {result}")
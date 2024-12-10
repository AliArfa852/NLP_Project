import yaml
from dataprocessing import preprocess_data
from emotion_detection import EmotionDetector
from responce_generation import ResponseGenerator
# from models.speach.speach_synthasis import SpeechSynthesizer
from database import Database

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    config = load_config()
    
    # Preprocess data
    preprocess_data()
    
    # Initialize components
    detector = EmotionDetector()
    generator = ResponseGenerator()
    # synthesizer = SpeechSynthesizer()
    db = Database()
    
    while True:
        user_input = input("Enter a Roman Urdu sentence (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        
        # Detect emotions
        emotions = detector.detect_emotion(user_input)
        emotion_labels = [e['label'] for e in emotions]
        print(f"Detected Emotions: {', '.join(emotion_labels)}")
        
        # Generate response
        response = generator.generate_response(user_input, emotions)
        print(f"Bot Response: {response}")
        
        # Synthesize speech
        # speech_file = synthesizer.synthesize_speech(response, "response")
        # print(f"Speech synthesized at: {speech_file}")
        
        # Log interaction
        log = {
            'user_input': user_input,
            'emotions_detected': emotion_labels,
            'response': response
            # ,'speech_file': speech_file
        }
        db.insert_log(log)
        
        # Reinforcement Learning could be integrated here based on user feedback
        # For simplicity, it's omitted in this pipeline

if __name__ == "__main__":
    main()

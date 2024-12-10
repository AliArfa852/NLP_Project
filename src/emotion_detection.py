import yaml
from pymongo import MongoClient
from transformers import pipeline

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class EmotionDetector:
    def __init__(self):
        config = load_config()
        self.client = MongoClient(config['mongodb']['uri'])
        self.db = self.client[config['mongodb']['database']]
        self.collection = self.db[config['mongodb']['collection']]
        # Initialize emotion detection pipeline
        self.emotion_classifier = pipeline('text-classification', model='nateraw/bert-base-uncased-emotion')

    def detect_emotion(self, text):
        emotions = self.emotion_classifier(text)
        # Filter emotions to keep only the required ones
        filtered_emotions = [e for e in emotions if e['label'].lower() in ['happy', 'sad', 'neutral', 'angry']]
        return filtered_emotions

    def log_interaction(self, user_input, emotions, response):
        log = {
            'user_input': user_input,
            'emotions_detected': emotions,
            'response': response
        }
        self.collection.insert_one(log)

if __name__ == "__main__":
    detector = EmotionDetector()
    sample_text = "Yeh fair game nai thi I don’t like it"
    emotions = detector.detect_emotion(sample_text)
    print(emotions)

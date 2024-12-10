import yaml
import openai

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class ResponseGenerator:
    def __init__(self):
        config = load_config()
        self.model_name = config['llm']['model_name']
        self.api_endpoint = config['llm']['api_endpoint']
        # Initialize LLM connection (assuming Ollama has an API)
        # Example using OpenAI's API; replace with Ollama's API calls
        openai.api_key = 'your_openai_api_key'

    def generate_response(self, user_input, emotions):
        # Create a prompt based on detected emotions
        emotion_labels = [e['label'] for e in emotions]
        prompt = f"User said: '{user_input}'. Detected emotions: {', '.join(emotion_labels)}. Generate a considerate and appropriate response in Roman Urdu reflecting the detected emotions."

        response = openai.Completion.create(
            engine="text-davinci-003",  # Replace with Ollama's endpoint if available
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()

if __name__ == "__main__":
    generator = ResponseGenerator()
    sample_input = "Yeh fair game nai thi I don’t like it"
    sample_emotions = [{'label': 'angry', 'score': 0.99}]
    response = generator.generate_response(sample_input, sample_emotions)
    print(response)

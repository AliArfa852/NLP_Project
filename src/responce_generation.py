import requests
import yaml
import json

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

    def generate_response(self, user_input, emotions):
        """Generate a response using the Ollama API based on user input and detected emotions."""
        # Create a prompt based on detected emotions
        emotion_labels = [e['label'] for e in emotions]
        prompt = (
            f"User said: '{user_input}'.\n"
            f"Detected emotions: {', '.join(emotion_labels)}.\n"
            f"Generate a considerate and appropriate response in Roman_Urdu reflecting the detected emotions."
        )

        # Payload for the Ollama API
        payload = {
            "model": self.model_name,
            "prompt": prompt
        }

        # Send request to the Ollama API
        response = requests.post(self.api_endpoint, json=payload, stream=True)
        
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
                    raise Exception(f"Failed to parse JSON line: {line}\nError: {e}")

        return complete_response.strip()

if __name__ == "__main__":
    # Example usage
    generator = ResponseGenerator()
    sample_input = "Yeh fair game nai thi I don’t like it"
    sample_emotions = [{'label': 'angry', 'score': 0.99}]
    response = generator.generate_response(sample_input, sample_emotions)
    print(f"Generated Response: {response}")

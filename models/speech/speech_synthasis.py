import yaml
import subprocess
import os

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class SpeechSynthesizer:
    def __init__(self):
        config = load_config()
        self.method = config['speech']['method']
        self.output_path = config['speech']['output_path']
        os.makedirs(self.output_path, exist_ok=True)

    def synthesize_speech(self, text, filename):
        output_file = os.path.join(self.output_path, f"{filename}.wav")
        if self.method == "StyleTTS2":
            # Example command for StyleTTS2
            subprocess.run(["styletts2", "--text", text, "--output", output_file])
        elif self.method == "Whisper Turbo":
            # Example command for Whisper Turbo
            subprocess.run(["whisper-turbo", "--text", text, "--output", output_file])
        else:
            raise ValueError("Unsupported speech synthesis method.")
        return output_file

if __name__ == "__main__":
    synthesizer = SpeechSynthesizer()
    sample_text = "Mujhe afsos hai ke aap ko yeh pasand nahi aaya."
    synthesizer.synthesize_speech(sample_text, "response1")

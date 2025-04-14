"""
Configuration settings for the Flask web application.
This file reads from config.yaml and makes the settings available to the Flask app.
"""

import os
import yaml

# Read the YAML config file
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, 'r') as file:
    yaml_config = yaml.safe_load(file)

# Make the config available in a more Python-friendly format
mongodb = yaml_config.get('mongodb', {})
llm = yaml_config.get('llm', {})
ollama = yaml_config.get('ollama', {})
speech = yaml_config.get('speech', {})
language = yaml_config.get('language', {})
personality = yaml_config.get('personality', {})
rl = yaml_config.get('rl', {})
data = yaml_config.get('data', {})

# Set up some default values if not in config
if 'default' not in personality:
    personality['default'] = 'default'

if 'default' not in language:
    language['default'] = 'english'

if 'supported' not in language:
    language['supported'] = ['english', 'urdu', 'hindi', 'punjabi']

if 'enabled' not in rl:
    rl['enabled'] = True

# Web app specific settings (not in yaml config)
flask_settings = {
    'debug': True,
    'host': '0.0.0.0',
    'port': 5000,
    'secret_key': 'emotion_chatbot_secret_key'
}
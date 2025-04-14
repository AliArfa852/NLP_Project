"""
Web frontend for the multilingual emotion chatbot using Flask.
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import chatbot components
from src.emotion_detection import EmotionDetector
# Import the enhanced version with personality support
from src.responce_generation_v1 import ResponseGenerator
from src.reinforcement_learning import ReinforcementLearner
from utils.personalities import get_available_personalities, get_personality_name, get_personality_description
from utils.transliteration import detect_language, urdu_to_roman, roman_to_urdu
import config.config as config

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'emotion_chatbot_secret_key'  # Required for session

# Initialize chatbot components
emotion_detector = EmotionDetector()
response_generator = ResponseGenerator()
reinforcement_learner = ReinforcementLearner()

# Track the conversation history
conversations = {}

# Get available languages and personalities
def get_available_languages():
    """Get list of available languages from config."""
    return config.language['supported']

def get_language_name(language_code):
    """Get the display name for a language code."""
    language_names = {
        'english': 'English',
        'urdu': 'Roman Urdu',
        'hindi': 'Hindi',
        'punjabi': 'Punjabi'
    }
    return language_names.get(language_code, language_code.capitalize())

@app.route('/')
def index():
    """Render the main chat interface."""
    # Initialize session if needed
    if 'user_id' not in session:
        session['user_id'] = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        conversations[session['user_id']] = []
    
    # Get available options for dropdowns
    languages = get_available_languages()
    personalities = get_available_personalities()
    
    # Format the personality options for the template
    personality_options = [
        {'id': pid, 'name': pdata['name'], 'description': pdata['description']}
        for pid, pdata in personalities.items()
    ]
    
    return render_template(
        'index.html', 
        languages=languages,
        language_names={code: get_language_name(code) for code in languages},
        personalities=personality_options,
        default_language=config.language['default'],
        default_personality=config.personality['default'],
        rl_enabled=config.rl['enabled']
    )

@app.route('/send_message', methods=['POST'])
def send_message():
    """Process a message from the user and return the chatbot's response."""
    data = request.json
    user_input = data.get('message', '')
    language = data.get('language', 'english')
    personality = data.get('personality', 'default')
    use_rl = data.get('use_rl', True)
    
    # Update component settings
    emotion_detector.change_language(language)
    response_generator.change_language(language)
    response_generator.change_personality(personality)
    
    # Process for Roman Urdu if needed
    if language == "urdu":
        lang_type = detect_language(user_input)
        if lang_type == "urdu_script":
            user_input = urdu_to_roman(user_input)
    
    # Get user ID from session
    user_id = session.get('user_id', f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    # Detect emotions
    emotions = emotion_detector.detect_emotion(user_input)
    emotion_labels = [e['label'] for e in emotions]
    primary_emotion = emotion_labels[0] if emotion_labels else 'neutral'
    
    # Get the most recent conversation for this user
    user_history = conversations.get(user_id, [])
    previous_message = user_history[-1] if user_history else None
    
    # Update RL if there's a previous message
    if previous_message and use_rl:
        previous_input = previous_message.get('user_input', '')
        previous_emotion = previous_message.get('emotion', 'neutral')
        
        reinforcement_learner.update(
            previous_input,
            previous_emotion,
            primary_emotion,
            language
        )
    
    # Generate response
    bot_response = response_generator.generate_response(user_input, emotions)
    
    # Store the current interaction
    current_interaction = {
        'timestamp': datetime.now().isoformat(),
        'user_input': user_input,
        'emotion': primary_emotion,
        'response': bot_response,
        'language': language,
        'personality': personality
    }
    
    # Update conversation history
    if user_id not in conversations:
        conversations[user_id] = []
    conversations[user_id].append(current_interaction)
    
    # Trim conversation history to last 50 messages to prevent memory issues
    if len(conversations[user_id]) > 50:
        conversations[user_id] = conversations[user_id][-50:]
    
    return jsonify({
        'response': bot_response,
        'emotions': emotion_labels,
        'language': language,
        'personality': personality,
        'personality_name': get_personality_name(personality)
    })

@app.route('/get_learning_stats', methods=['GET'])
def get_learning_stats():
    """Get statistics from the reinforcement learning system."""
    try:
        stats = reinforcement_learner.get_statistics()
        
        # Format stats for display
        formatted_stats = {
            'total_interactions': stats.get('total_interactions', 0),
            'average_reward': round(stats.get('average_reward', 0), 2),
            'patterns_learned': stats.get('patterns_learned', 0),
            'success_rate': round(stats.get('success_rate', 0), 2),
            'top_transitions': stats.get('top_transitions', [])
        }
        
        return jsonify({'success': True, 'stats': formatted_stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/reset_learning', methods=['POST'])
def reset_learning():
    """Reset the reinforcement learning data."""
    try:
        reinforcement_learner.reset_memory()
        return jsonify({'success': True, 'message': 'Learning data has been reset.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    """Clear the chat history for the current user."""
    user_id = session.get('user_id')
    if user_id and user_id in conversations:
        conversations[user_id] = []
    
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
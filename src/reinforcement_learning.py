"""
Reinforcement Learning module for the chatbot.
This module implements a learning system that improves responses based on user interactions.
"""

import os
import yaml
import json
import numpy as np
import random
from datetime import datetime
import time
from pymongo import MongoClient
import sqlite3
from pathlib import Path

def load_config(config_path='config/config.yaml'):
    """Load configuration settings from a YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class EmotionReward:
    """
    Compute rewards for emotional responses based on user reactions.
    """
    def __init__(self):
        # Define base rewards for different emotions and transitions
        self.reward_matrix = {
            'neutral': {
                'neutral': 0.1,  # Staying neutral is slightly positive
                'happy': 0.5,    # Making someone happy from neutral is good
                'sad': -0.2,     # Making someone sad from neutral is negative
                'angry': -0.5    # Making someone angry from neutral is very negative
            },
            'happy': {
                'neutral': -0.1,  # Going from happy to neutral is slightly negative
                'happy': 0.3,     # Keeping someone happy is good
                'sad': -0.7,      # Making someone sad from happy is very negative
                'angry': -0.8     # Making someone angry from happy is extremely negative
            },
            'sad': {
                'neutral': 0.3,   # Going from sad to neutral is good
                'happy': 0.8,     # Making someone happy from sad is very good
                'sad': -0.2,      # Keeping someone sad is negative
                'angry': -0.5     # Making someone angry from sad is very negative
            },
            'angry': {
                'neutral': 0.5,   # Calming someone down is very good
                'happy': 0.9,     # Making someone happy from angry is excellent
                'sad': -0.1,      # Going from angry to sad is slightly negative
                'angry': -0.5     # Keeping someone angry is very negative
            }
        }
        
        # Decay factor for rewards over time
        self.decay_factor = 0.9
        
    def calculate_reward(self, previous_emotion, current_emotion):
        """
        Calculate reward based on emotional transition.
        
        Args:
            previous_emotion: The user's previous emotional state
            current_emotion: The user's current emotional state
            
        Returns:
            Float representing the reward value
        """
        # Default previous emotion to neutral if not provided
        if not previous_emotion:
            previous_emotion = 'neutral'
            
        # If we don't have the emotion in our matrix, default to neutral
        if previous_emotion not in self.reward_matrix:
            previous_emotion = 'neutral'
        if current_emotion not in self.reward_matrix[previous_emotion]:
            current_emotion = 'neutral'
            
        # Get the reward from the matrix
        reward = self.reward_matrix[previous_emotion][current_emotion]
        
        return reward

class RAGMemory:
    """
    Retrieval-Augmented Generation memory system.
    Stores and retrieves conversation patterns for improved responses.
    """
    def __init__(self, db_path='data/rag_memory.db'):
        """Initialize the RAG memory system with a database."""
        self.db_path = db_path
        self.ensure_db_exists()
        
    def ensure_db_exists(self):
        """Create the database if it doesn't exist."""
        # Make sure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            emotion TEXT,
            response TEXT, 
            next_emotion TEXT,
            reward REAL,
            language TEXT,
            timestamp TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emotion_sequence TEXT,
            successful_responses TEXT,
            avg_reward REAL,
            count INTEGER,
            language TEXT
        )
        ''')
        
        # Create indexes for faster searches
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_emotion ON conversations (emotion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_input ON conversations (user_input)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_language ON conversations (language)')
        
        conn.commit()
        conn.close()
        
    def store_interaction(self, user_input, emotion, response, next_emotion, reward, language):
        """
        Store an interaction in the database.
        
        Args:
            user_input: The user's input text
            emotion: The detected emotion in the input
            response: The chatbot's response
            next_emotion: The emotion detected in the next user input
            reward: The calculated reward value
            language: The language of the interaction
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store the interaction
        cursor.execute('''
        INSERT INTO conversations 
        (user_input, emotion, response, next_emotion, reward, language, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_input, 
            emotion, 
            response, 
            next_emotion, 
            reward, 
            language, 
            datetime.now().isoformat()
        ))
        
        # Update emotion patterns
        self._update_emotion_patterns(cursor, emotion, next_emotion, response, reward, language)
        
        conn.commit()
        conn.close()
    
    def reset(self):
        """Reset the memory database by deleting all records."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete all data from tables
            cursor.execute('DELETE FROM conversations')
            cursor.execute('DELETE FROM emotion_patterns')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error resetting memory: {str(e)}")
            return False
    
    def get_statistics(self):
        """Get statistics about the learned data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total interactions
        cursor.execute('SELECT COUNT(*) FROM conversations')
        stats['total_interactions'] = cursor.fetchone()[0]
        
        # Average reward
        cursor.execute('SELECT AVG(reward) FROM conversations')
        avg_reward = cursor.fetchone()[0]
        stats['average_reward'] = avg_reward if avg_reward else 0
        
        # Number of patterns learned
        cursor.execute('SELECT COUNT(*) FROM emotion_patterns')
        stats['patterns_learned'] = cursor.fetchone()[0]
        
        # Most common emotion transitions
        cursor.execute('''
        SELECT emotion_sequence, COUNT(*) as count 
        FROM emotion_patterns 
        GROUP BY emotion_sequence 
        ORDER BY count DESC 
        LIMIT 5
        ''')
        top_transitions = cursor.fetchall()
        stats['top_transitions'] = [
            {'transition': t[0], 'count': t[1]} 
            for t in top_transitions
        ]
        
        # Success rate (percentage of positive rewards)
        cursor.execute('''
        SELECT 
            (SELECT COUNT(*) FROM conversations WHERE reward > 0) * 100.0 / 
            (SELECT COUNT(*) FROM conversations WHERE COUNT(*) > 0)
        ''')
        result = cursor.fetchone()
        success_rate = result[0] if result else 0
        stats['success_rate'] = success_rate if success_rate else 0
        
        conn.close()
        return stats
    
    def get_top_patterns(self, language, limit=5):
        """Get the top emotion transition patterns for a language."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT emotion_sequence, successful_responses, avg_reward, count 
        FROM emotion_patterns 
        WHERE language = ? 
        ORDER BY count DESC, avg_reward DESC 
        LIMIT ?
        ''', (language, limit))
        
        patterns = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return patterns
        
    def _update_emotion_patterns(self, cursor, emotion, next_emotion, response, reward, language):
        """Update the emotion patterns table with new information."""
        # Create an emotion sequence
        emotion_sequence = f"{emotion}->{next_emotion}"
        
        # Check if this pattern exists
        cursor.execute('''
        SELECT id, successful_responses, avg_reward, count 
        FROM emotion_patterns 
        WHERE emotion_sequence = ? AND language = ?
        ''', (emotion_sequence, language))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing pattern
            pattern_id, successful_responses, avg_reward, count = result
            
            # Parse the successful responses
            responses = json.loads(successful_responses)
            
            # Add this response if the reward is positive
            if reward > 0:
                # Avoid duplicates
                if response not in responses:
                    responses.append(response)
                
                # Keep only the top 5 responses
                if len(responses) > 5:
                    responses = responses[-5:]
            
            # Update the average reward using incremental average formula
            new_avg_reward = ((avg_reward * count) + reward) / (count + 1)
            
            # Update the database
            cursor.execute('''
            UPDATE emotion_patterns 
            SET successful_responses = ?, avg_reward = ?, count = ? 
            WHERE id = ?
            ''', (json.dumps(responses), new_avg_reward, count + 1, pattern_id))
        else:
            # Create a new pattern
            responses = [response] if reward > 0 else []
            
            cursor.execute('''
            INSERT INTO emotion_patterns 
            (emotion_sequence, successful_responses, avg_reward, count, language) 
            VALUES (?, ?, ?, ?, ?)
            ''', (
                emotion_sequence, 
                json.dumps(responses), 
                reward, 
                1, 
                language
            ))
    
    def retrieve_similar_interactions(self, user_input, emotion, language, limit=5):
        """
        Retrieve similar past interactions.
        
        Args:
            user_input: The current user input
            emotion: The current detected emotion
            language: The current language
            limit: Maximum number of interactions to retrieve
            
        Returns:
            List of similar interactions
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get interactions with the same emotion and language
        cursor.execute('''
        SELECT * FROM conversations 
        WHERE emotion = ? AND language = ? 
        ORDER BY reward DESC, timestamp DESC 
        LIMIT ?
        ''', (emotion, language, limit))
        
        interactions = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return interactions
    
    def get_suggested_responses(self, emotion, target_emotion, language, limit=3):
        """
        Get suggested responses for transitioning from one emotion to another.
        
        Args:
            emotion: The current emotion
            target_emotion: The target emotion to reach
            language: The current language
            limit: Maximum number of responses to retrieve
            
        Returns:
            List of suggested responses
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Create the emotion sequence
        emotion_sequence = f"{emotion}->{target_emotion}"
        
        # Get the pattern
        cursor.execute('''
        SELECT successful_responses, avg_reward 
        FROM emotion_patterns 
        WHERE emotion_sequence = ? AND language = ?
        ''', (emotion_sequence, language))
        
        result = cursor.fetchone()
        
        if result and result['successful_responses']:
            responses = json.loads(result['successful_responses'])
            
            # Return up to 'limit' responses
            suggested = responses[:limit]
            
            conn.close()
            return suggested
        
        # If no direct pattern exists, look for similar transitions
        if not result or not result['successful_responses']:
            cursor.execute('''
            SELECT response 
            FROM conversations 
            WHERE emotion = ? AND next_emotion = ? AND language = ? AND reward > 0 
            ORDER BY reward DESC 
            LIMIT ?
            ''', (emotion, target_emotion, language, limit))
            
            rows = cursor.fetchall()
            suggested = [row['response'] for row in rows]
            
            conn.close()
            return suggested
        
        conn.close()
        return []

class ReinforcementLearner:
    """
    Reinforcement Learning module for improving chatbot responses.
    """
    def __init__(self):
        """Initialize the Reinforcement Learning module."""
        self.config = load_config()
        
        # Load RL parameters from config
        self.learning_rate = self.config['rl'].get('learning_rate', 0.001)
        self.gamma = self.config['rl'].get('gamma', 0.95)  # Discount factor for future rewards
        self.epsilon = self.config['rl'].get('epsilon', 0.1)  # Exploration rate
        
        # Initialize reward calculator
        self.reward_calculator = EmotionReward()
        
        # Initialize RAG memory
        self.memory = RAGMemory(db_path=self.config.get('data', {}).get('rag_db_path', 'data/rag_memory.db'))
        
        # Track the conversation state
        self.previous_state = None
        self.previous_action = None
        self.previous_emotion = None
        
        # Learning state
        self.total_rewards = 0
        self.interaction_count = 0
        
        # Log directory
        self.log_dir = "logs/rl"
        os.makedirs(self.log_dir, exist_ok=True)
    
    def log_training(self, message):
        """Log training information to a file."""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(self.log_dir, f"training_{timestamp}.log")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    
    def get_state_representation(self, user_input, emotion, language):
        """
        Create a state representation from the user input and emotion.
        
        Args:
            user_input: The user's input text
            emotion: The detected emotion
            language: The current language
            
        Returns:
            Dictionary representing the state
        """
        return {
            'user_input': user_input,
            'emotion': emotion,
            'language': language,
            'timestamp': time.time()
        }
    
    def get_statistics(self):
        """Get statistics about the learning progress."""
        # Get statistics from the memory
        memory_stats = self.memory.get_statistics()
        
        # Add RL-specific statistics
        stats = {
            'epsilon': self.epsilon,
            'learning_rate': self.learning_rate,
            'gamma': self.gamma,
            'total_interactions': self.interaction_count,
            'average_reward': self.total_rewards / max(1, self.interaction_count)
        }
        
        # Combine with memory stats
        stats.update(memory_stats)
        
        return stats
    
    def reset_memory(self):
        """Reset the memory database."""
        result = self.memory.reset()
        
        # Reset counters
        self.total_rewards = 0
        self.interaction_count = 0
        self.previous_state = None
        self.previous_action = None
        self.previous_emotion = None
        
        return result
        
    def update(self, user_input, current_emotion, next_emotion, language):
        """
        Update the model with a new emotional transition.
        
        Args:
            user_input: The user's input text
            current_emotion: The current detected emotion
            next_emotion: The next detected emotion after the response
            language: The current language
            
        Returns:
            Float representing the calculated reward
        """
        # Calculate reward based on emotional transition
        reward = self.reward_calculator.calculate_reward(
            current_emotion, 
            next_emotion
        )
        
        # Update counters
        self.total_rewards += reward
        self.interaction_count += 1
        
        # Log the update
        self.log_training(
            f"Emotional transition: {current_emotion} -> {next_emotion}, "
            f"Reward: {reward:.2f}, "
            f"Input: {user_input[:30]}..."
        )
        
        return reward
    
    def update_with_response(self, user_input, emotion, response, next_emotion, language):
        """
        Update the model with a full interaction including response.
        
        Args:
            user_input: The user's input text
            emotion: The detected emotion
            response: The chatbot's response
            next_emotion: The emotion after the response
            language: The current language
            
        Returns:
            Float representing the calculated reward
        """
        # Calculate reward
        reward = self.reward_calculator.calculate_reward(
            emotion, 
            next_emotion
        )
        
        # Store the interaction in memory
        self.memory.store_interaction(
            user_input,
            emotion,
            response,
            next_emotion,
            reward,
            language
        )
        
        # Update counters
        self.total_rewards += reward
        self.interaction_count += 1
        
        # Log the update
        self.log_training(
            f"Update: {emotion} -> {next_emotion}, "
            f"Reward: {reward:.2f}, "
            f"Response: {response[:30]}..."
        )
        
        return reward
    
    def enhance_prompt(self, user_input, emotion, language):
        """
        Enhance the prompt with RAG information.
        
        Args:
            user_input: The user's input text
            emotion: The detected emotion
            language: The current language
            
        Returns:
            String containing the enhanced prompt
        """
        # Get similar past interactions
        similar_interactions = self.memory.retrieve_similar_interactions(
            user_input, 
            emotion, 
            language
        )
        
        # Determine target emotion (what we want to achieve)
        target_emotion = self._determine_target_emotion(emotion)
        
        # Get suggested responses for this transition
        suggested_responses = self.memory.get_suggested_responses(
            emotion, 
            target_emotion, 
            language
        )
        
        # Create the enhanced prompt
        prompt_additions = []
        
        if similar_interactions:
            examples = []
            for i, interaction in enumerate(similar_interactions[:3]):
                examples.append(
                    f"User input: \"{interaction['user_input']}\"\n"
                    f"Response: \"{interaction['response']}\"\n"
                    f"Result: User went from {interaction['emotion']} to {interaction['next_emotion']}"
                )
            
            prompt_additions.append(
                "Here are some similar past interactions:\n" + 
                "\n".join(examples)
            )
        
        if suggested_responses:
            prompt_additions.append(
                "These response patterns have worked well in the past for this emotional transition:\n" +
                "\n".join([f"- \"{resp}\"" for resp in suggested_responses])
            )
        
        # Add a target emotion suggestion
        prompt_additions.append(
            f"The ideal target emotion for this interaction is: {target_emotion}"
        )
        
        # Combine all additions
        if prompt_additions:
            enhanced_prompt = "\n\n".join(prompt_additions)
            return enhanced_prompt
        
        return ""
    
    def _determine_target_emotion(self, current_emotion):
        """
        Determine the target emotion based on the current emotion.
        
        Args:
            current_emotion: The current detected emotion
            
        Returns:
            String representing the target emotion
        """
        if current_emotion == 'happy':
            return 'happy'  # If they're happy, keep them happy
        elif current_emotion == 'sad':
            return 'neutral' if random.random() < 0.3 else 'happy'  # Usually try to make them happy
        elif current_emotion == 'angry':
            return 'neutral'  # Try to calm them down first
        else:  # neutral
            return 'happy'  # Try to make them happy

    def get_suggested_response(self, user_input, emotion, language):
        """
        Get a suggested response based on past interactions.
        
        Args:
            user_input: The user's input text
            emotion: The detected emotion
            language: The current language
            
        Returns:
            String containing a suggested response, or None if no good suggestion is found
        """
        # Apply exploration-exploitation strategy
        if random.random() < self.epsilon:
            # Exploration: don't use a suggested response
            return None
            
        # Determine target emotion
        target_emotion = self._determine_target_emotion(emotion)
        
        # Get suggested responses
        suggestions = self.memory.get_suggested_responses(
            emotion, 
            target_emotion, 
            language
        )
        
        if suggestions:
            # Choose one of the suggestions (exploitation)
            return random.choice(suggestions)
        
        # No good suggestion found
        return None

# Test the module
if __name__ == "__main__":
    rl = ReinforcementLearner()
    
    # Simulate some interactions
    interactions = [
        ("I'm feeling very happy today!", "happy", "That's wonderful to hear! What made your day so good?", "english"),
        ("I just got a promotion at work", "happy", "Congratulations on your promotion! That's fantastic news.", "english"),
        ("I'm really angry about what happened", "angry", "I understand your frustration. Let's talk about what happened and see if we can find a way to address it.", "english"),
        ("I feel so sad and lonely", "sad", "I'm sorry you're feeling that way. Is there something specific that's making you feel sad?", "english")
    ]
    
    for user_input, emotion, response, language in interactions:
        # For testing, we'll use update_with_response which captures both the user input and the response
        rl.update_with_response(
            user_input,
            emotion,
            response,
            "happy",  # Assume the user becomes happy after our response
            language
        )
        
        # Print the enhanced prompt for the next interaction
        print(f"\nUser: {user_input}")
        print(f"Emotion: {emotion}")
        print(f"Response: {response}")
        print("\nEnhanced prompt for next interaction:")
        print(rl.enhance_prompt(user_input, emotion, language))
        print("-" * 50)
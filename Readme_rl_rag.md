# Multilingual Emotion Chatbot with Reinforcement Learning and RAG

This project implements a cross-platform, offline-capable chatbot that detects emotions in user input, generates appropriate responses, and progressively learns to improve its responses using Reinforcement Learning (RL) and Retrieval-Augmented Generation (RAG).

## Key Features

- **Multilingual Support**: Works with English, Roman Urdu, Hindi, and Punjabi
- **Emotion Detection**: Identifies emotions (happy, sad, neutral, angry) in user input
- **Reinforcement Learning**: Learns from interactions to improve emotional responses over time
- **Retrieval-Augmented Generation (RAG)**: Stores and retrieves successful conversation patterns
- **Cross-Platform**: Works on both Windows and Linux
- **Speech Recognition & Synthesis**: Voice interaction with offline capabilities

## Reinforcement Learning Features

This chatbot uses a custom reinforcement learning system to improve its ability to manage user emotions:

### Emotion-Based Rewards

The system uses a reward mechanism based on emotional transitions:
- Positive rewards for improving emotional states (e.g., sad→happy)
- Small rewards for maintaining positive emotions (e.g., happy→happy)
- Negative rewards for worsening emotional states (e.g., happy→sad)

### Learning Memory

The chatbot stores conversation patterns in a SQLite database:
- Tracks emotional transitions and their outcomes
- Records successful responses for different emotional states
- Builds a database of effective conversation strategies

### Response Improvement

As the chatbot interacts with users:
1. It tracks emotional transitions and outcomes
2. It learns which responses lead to improved emotional states
3. It reuses successful conversational patterns 
4. It explores new response strategies to find better approaches

## How the RL and RAG Work Together

1. **Emotion Detection**: The system detects the user's current emotional state
2. **Pattern Matching**: It searches for similar past interactions and successful patterns
3. **Response Enhancement**: The LLM gets enhanced prompts with successful conversation patterns
4. **Exploration vs. Exploitation**: The system balances using known successful responses with exploring new approaches
5. **Reward Calculation**: After each interaction, the system calculates a reward based on emotional transitions
6. **Memory Update**: The RAG database is updated with new interactions and rewards

## Monitoring and Managing Learning

The application includes features to monitor and manage its learning:

- **Learning Statistics**: View success rates and pattern recognition through the options menu
- **Toggle Learning**: Enable/disable the reinforcement learning system
- **Reset Learning Data**: Clear the learning database to start fresh

## Usage

### Using the Reinforcement Learning Features

1. **Enable Learning**: Make sure reinforcement learning is enabled in the options menu
2. **Regular Use**: Simply chat with the bot as normal - it will learn from your interactions
3. **View Progress**: Check learning statistics in the options menu to see improvements
4. **Reset if Needed**: If you want to start learning from scratch, reset the data through the options menu

### Options Menu (Enhanced)

Access the options menu by typing `options` or pressing Ctrl+C:

1. Change language
2. Toggle speech input
3. Toggle speech output
4. Toggle transliteration (for Roman Urdu)
5. Toggle reinforcement learning
6. View learning statistics
7. Reset learning data
8. Exit application
0. Return to chat

## How the Learning System Works

### 1. Reward Mechanism

The system defines rewards for different emotional transitions:

| From → To | Happy | Neutral | Sad | Angry |
|-----------|-------|---------|-----|-------|
| Happy     | +0.5  | 0.0     | -0.7 | -0.8  |
| Neutral   | +0.7  | +0.1    | -0.3 | -0.5  |
| Sad       | +0.8  | +0.5    | -0.2 | -0.5  |
| Angry     | +0.9  | +0.7    | -0.1 | -0.6  |

This reward structure incentivizes the chatbot to:
- Maintain positive emotional states (keep happy users happy)
- Improve negative emotional states (help sad or angry users feel better)
- Avoid responses that worsen emotional states

### 2. Learning Database Structure

The system uses two main tables to store learning data:

**Conversations Table:**
- Records full interactions including user input, emotions, responses, and rewards
- Provides raw data for analysis and retrieval

**Emotion Patterns Table:**
- Organizes successful patterns for emotional transitions (e.g., sad→happy)
- Stores successful responses for each transition pattern
- Tracks average rewards and usage counts for patterns

### 3. RAG Enhancement Process

When generating responses, the system:

1. Retrieves similar past interactions from memory
2. Identifies the target emotion (based on current emotion and goals)
3. Retrieves successful responses for the desired emotional transition
4. Enhances the prompt to the LLM with this information:
   - Examples of similar past interactions
   - Successful response patterns
   - Target emotional state
5. The LLM then generates a response informed by past successful strategies

### 4. Exploration vs. Exploitation

To prevent getting stuck in suboptimal strategies, the system:
- Uses an exploration rate (epsilon) to occasionally try new approaches
- Gradually decreases exploration as it finds successful strategies
- Maintains a diverse set of successful responses for each emotional transition

## Implementation Details

### Reinforcement Learning Module

The `ReinforcementLearner` class implements the RL system with these key methods:
- `update()`: Updates the model with new emotional transitions
- `enhance_prompt()`: Enhances the LLM prompt with RAG information
- `get_suggested_response()`: Retrieves successful responses from memory
- `get_statistics()`: Provides learning statistics for monitoring

### RAG Memory System

The `RAGMemory` class implements the database interactions:
- `store_interaction()`: Records interactions and updates patterns
- `retrieve_similar_interactions()`: Finds similar past conversations
- `get_suggested_responses()`: Retrieves successful responses for transitions
- `reset()`: Clears the learning database

## Configuration

The reinforcement learning system can be configured in `config/config.yaml`:

```yaml
# Reinforcement Learning Configuration
rl:
  learning_rate: 0.001
  gamma: 0.95  # Discount factor for future rewards
  epsilon: 0.2  # Exploration rate (probability of trying new responses)
  enabled: true  # Whether RL is enabled by default
  
  # Emotion Reward Settings
  rewards:
    # Rewards for emotional transitions (from -> to)
    transitions:
      # From neutral
      neutral_to_neutral: 0.1
      neutral_to_happy: 0.7
      neutral_to_sad: -0.3
      neutral_to_angry: -0.5
      
      # From happy
      happy_to_happy: 0.5
      happy_to_neutral: 0.0
      happy_to_sad: -0.7
      happy_to_angry: -0.8
      
      # From sad
      sad_to_happy: 0.8
      sad_to_neutral: 0.5
      sad_to_sad: -0.2
      sad_to_angry: -0.5
      
      # From angry
      angry_to_happy: 0.9
      angry_to_neutral: 0.7
      angry_to_sad: -0.1
      angry_to_angry: -0.6
```

## Acknowledgments

- This reinforcement learning implementation is based on emotionally-guided reward mechanisms
- The RAG system is implemented using SQLite for lightweight, offline database capability
- The reward structure is designed based on psychological models of emotional transitions



Error:
idk what is happening but there is a path error

C:\Users\aliar\Documents\sem8\GenAi\project\NLP_Project\outputs\speech\outputs\speech

saves the temp audio file here insted 
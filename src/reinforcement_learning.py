import yaml
from stable_baselines3 import PPO
from stable_baselines3.common.envs import DummyVecEnv
import gym

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class EmotionEnv(gym.Env):
    """Custom Environment for Emotion-based Chatbot"""
    def __init__(self, config):
        super(EmotionEnv, self).__init__()
        self.action_space = gym.spaces.Discrete(4)  # Actions: happy, sad, neutral, angry
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(10,), dtype=float)
        self.config = config

    def reset(self):
        # Reset the state of the environment to an initial state
        return self.observation_space.sample()

    def step(self, action):
        # Execute one step within the environment
        reward = 0
        done = False
        info = {}
        
        # Define reward logic based on action
        # For example, positive response to happy, etc.
        if action == 0:  # happy
            reward = 1
        elif action == 1:  # sad
            reward = -1
        elif action == 2:  # neutral
            reward = 0
        elif action == 3:  # angry
            reward = -2
        
        # Define when to end the episode
        done = True
        return self.observation_space.sample(), reward, done, info

def train_rl_model():
    config = load_config()
    env = DummyVecEnv([lambda: EmotionEnv(config)])
    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=10000)
    model.save("models/rl_model")

if __name__ == "__main__":
    train_rl_model()

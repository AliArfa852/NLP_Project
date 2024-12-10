import yaml
from pymongo import MongoClient

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class Database:
    def __init__(self):
        config = load_config()
        self.client = MongoClient(config['mongodb']['uri'])
        self.db = self.client[config['mongodb']['database']]
        self.collection = self.db[config['mongodb']['collection']]

    def insert_log(self, log):
        self.collection.insert_one(log)

    def fetch_logs(self, query={}):
        return list(self.collection.find(query))

if __name__ == "__main__":
    db = Database()
    sample_log = {
        'user_input': "Yeh fair game nai thi I don’t like it",
        'emotions_detected': ['angry'],
        'response': "Mujhe afsos hai ke aap ko yeh pasand nahi aaya."
    }
    db.insert_log(sample_log)
    logs = db.fetch_logs()
    print(logs)

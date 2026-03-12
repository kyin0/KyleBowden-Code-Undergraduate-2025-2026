from pymongo import MongoClient
import time
from dotenv import load_dotenv
import os

from src.utils.config import load_config

class Database:
    
    def __init__(self):

        config = load_config()
        store_config = config["store"]
        db_name = store_config["DB_NAME"]

        load_dotenv()

        db_key = os.getenv("DATABASE_KEY")
        if db_key is None:
            raise ValueError("Missing environment variable: 'DATABASE_KEY'")
        try:
            self.client = MongoClient(db_key)
            self.db = self.client[db_name]

            self.runs = self.db["runs"]
            self.tasks = self.db["tasks"]
            self.experiments = self.db["experiments"]
        except Exception as e:
            raise Exception("Error connecting to database") from e
    
    # tasks
    
    def does_task_exist(self, task_id : str):
        return self.tasks.count_documents({"_id": task_id}) > 0
    
    def get_task(self, task_id : str) -> dict:
        if not self.does_task_exist(task_id):
            raise ValueError("Task ID does not exist!")

        return self.tasks.find_one({"_id": task_id})

    def insert_task(self, task_id : str, task_spec : dict):

        if self.does_task_exist(task_id):
            raise ValueError(f"An entry with task ID {task_id} already exists on the database")
        
        task_spec["_id"] = task_id
        task_spec["created_at"] = time.time()

        self.tasks.insert_one(task_spec)
    
    # run results
from pymongo import MongoClient
import time
from dotenv import load_dotenv
import os
from typing import Literal

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

    def insert_results(self, task_id : str, prompt : str, rag_enabled : bool, rag_n : int, model : str, temperature : float, top_k : int, top_p : float, seed : int, llm_timeout_seconds : int, repeat_penalty : int, repeat_last_n : int, num_predict : int, runner_timeout_seconds : int, code_length : int, percepts : int, runtime : float, passed : bool, static_repair_loops_taken : int, timed_out : bool, generated_code : str, code_output : dict, experiment_type : Literal["create", "modify"], failure_reason_category : Literal["timeout", "static checker", "runtime error", None], exit_code : int):

        if not self.does_task_exist(task_id):
            raise ValueError(f"An entry with task ID {task_id} already exists on the database")

        result_data = {
            "task_id": task_id,
            "prompt": prompt,
            "rag_enabled": rag_enabled,
            "rag_n": rag_n,
            "model": model,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "seed": seed,
            "llm_timeout_seconds": llm_timeout_seconds,
            "repeat_penalty": repeat_penalty,
            "repeat_last_n": repeat_last_n,
            "num_predict": num_predict,
            "runner_timeout_seconds": runner_timeout_seconds,
            "code_length": code_length,
            "percepts": percepts,
            "runtime": runtime,
            "passed": passed,
            "static_repair_loops_taken": static_repair_loops_taken,
            "timed_out": timed_out,
            "generated_code": generated_code,
            "code_output": code_output,
            "timestamp": round(time.time()),
            "experiment_type": experiment_type,
            "failure_reason_category": failure_reason_category,
            "exit_code": exit_code
        }

        self.experiments.insert_one(result_data)
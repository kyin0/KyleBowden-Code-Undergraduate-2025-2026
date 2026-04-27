from src.store.database import Database

if __name__ == "__main__":

    db = Database()

    task_id = "your task ID here"
    task_spec = {
        "v": 1,
        "description": """
           Your description here
        """
    }

    db.insert_task(task_id, task_spec)

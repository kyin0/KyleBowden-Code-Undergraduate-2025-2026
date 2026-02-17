import requests
from dotenv import load_dotenv
import os

class LLM:

    def __init__(self):
        pass

    def generate(self, prompt : str, model : str = "llama3", seed = 42, temperature : float = 0, top_k : int = 1, top_p : int = 1):

        url = "http://localhost:11434/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "seed": seed,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p
            }
        }

        response = requests.post(url, json=payload)

        data = response.json()

        print(data["response"])

if __name__ == "__main__":
    llm = LLM()
    llm.generate("Say something random and spontaneous!")
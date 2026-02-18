import requests

from utils.config import load_config

class LLM:

    def __init__(self):

        config = load_config()
        llm_config = config["llm"]

        self.temperature = llm_config["TEMPERATURE"]
        self.seed = llm_config["SEED"]
        self.top_k = llm_config["TOP_K"]
        self.top_p = llm_config["TOP_P"]
        self.model = llm_config["MODEL"]
        self.timeout_seconds = llm_config["TIMEOUT_SECONDS"]
        self.llm_endpoint = llm_config["LLM_ENDPOINT"]

    def generate(self, prompt : str) -> dict:

        url = self.llm_endpoint

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "seed": self.seed,
                "temperature": self.temperature,
                "top_k": self.top_k,
                "top_p": self.top_p
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout_seconds)
            response.raise_for_status()
        except requests.Timeout:
            raise RuntimeError("LLM request timed out")
        except requests.RequestException as e:
            raise RuntimeError(f"LLM request failed: {e}")

        return response.json()
from pathlib import Path
import json

from src.llm.llm import LLM
from src.rag.loader import load_corpus
from src.utils.config import load_config
from src.rag.prompt_builder import build_prompt

from src.checks.static_checker import StaticChecker

class Orchestrator:

    def __init__(self):
        self.llm = LLM()
        self.static_checker = StaticChecker()

        self.project_root = Path(__file__).resolve().parents[2]

        config = load_config()
        rag_config = config["rag"]
        runner_config = config["runner"]

        self.rag_enabled = rag_config["ENABLED"]
        self.rag_n = rag_config["RAG_N"]
        self.repair_max_iterations = runner_config["MAX_REPAIR_ITERATIONS"]
    
    def run_experiment(self, experiment_file : str):

        task_path = self.project_root / "planning" / "scenario_ideas" / f"{experiment_file}.json"
        results_path = self.project_root / "src" / "results" / f"{experiment_file}.py"

        with open(task_path, "r", encoding="UTF-8") as f:
            task_specification = json.load(f)

        chunks = None

        if self.rag_enabled:
            corpus_path = self.project_root / "knowledge" / "maspy"
            chunks = load_corpus(corpus_path)

        issues = "" # empty first. when issues arise in static checker or runtime env, report here and re-generate.
        
        for i in range(self.repair_max_iterations):
            prompt = build_prompt(task_specification, self.rag_enabled, chunks, self.rag_n, issues)

            generated_code = self.llm.generate(prompt)

            response_text = generated_code["response"] if isinstance(generated_code, dict) else str(generated_code)
            cleaned_code = response_text.strip()

            if cleaned_code.startswith("```"):
                lines = cleaned_code.splitlines()
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned_code = "\n".join(lines).strip()

            cleaned_code = cleaned_code.replace("```python", "").replace("```", "").replace("`", "")
            results = self.static_checker.validate(cleaned_code)

            if results["pass"]:
                break
            else:
                print(f"Failed! Reason: {results}. Iteration: {i}")

                issues = results
            
        results_path.write_text(cleaned_code, encoding="UTF-8")

        print(results)
from pathlib import Path

from src.llm.llm import LLM
from src.rag.loader import load_corpus
from src.utils.config import load_config
from src.rag.prompt_builder import build_prompt

from src.store.database import Database

from src.checks.static_checker import StaticChecker

from src.sandbox.runner import run_file

class Orchestrator:

    def __init__(self):
        self.llm = LLM()
        self.static_checker = StaticChecker()
        self.db = Database()

        self.project_root = Path(__file__).resolve().parents[2]

        config = load_config()
        rag_config = config["rag"]
        runner_config = config["runner"]

        self.rag_enabled = rag_config["ENABLED"]
        self.rag_n = rag_config["RAG_N"]
        self.repair_max_iterations = runner_config["MAX_REPAIR_ITERATIONS"]
    
    def run_experiment(self, task_id : str):
        task_specification = self.db.get_task(task_id)
        results_path = self.project_root / "src" / "results" / f"{task_id}.py"

        print("Loaded task specification")

        chunks = None

        if self.rag_enabled:
            corpus_path = self.project_root / "knowledge" / "maspy"
            chunks = load_corpus(corpus_path)
            print("Loaded CORPUS")

        issues = "" # empty first. when issues arise in static checker or runtime env, report here and re-generate.

        valid = False
        counter = 0
        
        while not valid:
            print(f"Attempting to build code. Attempt: {counter}")
            prompt = build_prompt(task_specification, self.rag_enabled, chunks, self.rag_n, issues)

            print(prompt)

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
                valid = True
            else:
                print(f"Failed! Reason: {results}. Iteration: {counter}")

                issues = f"{issues}Issue {counter}: {results}\n"

                if counter >= self.repair_max_iterations:
                    print(f"Maximum number of repairs reached ({counter}). Terminating...")
                    return
            
        results_path.write_text(cleaned_code, encoding="UTF-8")

        print("Code passed static tests.")

        print("Running file...")

        runtime_results = run_file(results_path)

        print(runtime_results)
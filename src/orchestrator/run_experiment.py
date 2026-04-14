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
        llm_config = config["llm"]

        self.rag_enabled = rag_config["ENABLED"]
        self.rag_n = rag_config["RAG_N"]
        self.repair_max_iterations = runner_config["MAX_REPAIR_ITERATIONS"]
        self.runner_timeout = runner_config["TIMEOUT"]
        self.model = llm_config["MODEL"]
        self.temperature = llm_config["TEMPERATURE"]
        self.top_k = llm_config["TOP_K"]
        self.top_p = llm_config["TOP_P"]
        self.seed = llm_config["SEED"]
        self.timeoutseconds = llm_config["TIMEOUT_SECONDS"]
        self.repeat_penalty = llm_config["REPEAT_PENALTY"]
        self.repeat_last_n = llm_config["REPEAT_LAST_N"]
        self.num_predict = llm_config["NUM_PREDICT"]

    def _extract_code(self, generated_code):
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
        return cleaned_code
    
    def run_experiment(self, task_id : str):
        task_specification = self.db.get_task(task_id)
        results_path = self.project_root / "src" / "results" / f"{task_id}.py"

        print("Loaded task specification")

        chunks = None

        if self.rag_enabled:
            corpus_path = self.project_root / "knowledge" / "maspy"
            chunks = load_corpus(corpus_path)
            print("Loaded CORPUS")

        repair_context = None
        counter = 0

        passed = False
        cleaned_code = ""
        prompt = ""
        failure_reason_category = None

        runtime = 0
        success = False
        timed_out = False
        code_output = {}
        exit_code = None
        
        while True:
            counter += 1
            print(f"Attempting pipeline. Attempt: {counter}")
            prompt = build_prompt(task_specification, self.rag_enabled, chunks, self.rag_n, repair_context)

            generated_code = self.llm.generate(prompt)

            if isinstance(generated_code, dict) and "response" in generated_code:
                print(generated_code["response"])
            else:
                print(generated_code)

            cleaned_code = self._extract_code(generated_code)

            if cleaned_code.strip() == "FAIL":
                failure_reason_category = "static checker"
                print("Model returned FAIL. Terminating...")
                break

            results = self.static_checker.validate(cleaned_code, task_specification)

            if not results["pass"]:
                print(f"Failed! Reason: {results}. Iteration: {counter}")

                failure_reason_category = "static checker"
                repair_context = {
                    "type": "static",
                    "findings": results["findings"],
                    "previous_code": cleaned_code,
                }

                if counter >= self.repair_max_iterations:
                    print(f"Maximum number of repairs reached ({counter}). Terminating...")
                    break

                continue

            results_path.write_text(cleaned_code, encoding="UTF-8")

            print("Code passed static tests.")
            print("Running file...")

            runtime_results = run_file(results_path)

            runtime = runtime_results["runtime"]
            exit_code = runtime_results["exit_code"]
            code_output = runtime_results

            if runtime_results["exit_code"] == 0:
                success = True
                passed = True
                break

            if runtime_results["runtime"] == self.runner_timeout:
                timed_out = True
                failure_reason_category = "timeout"
                print(f"Timeout! Reason: {runtime_results['stderr'] or runtime_results['stdout']}. Iteration: {counter}")
            else:
                failure_reason_category = "runtime error"
                print(f"Runtime error! Reason: {runtime_results['stderr'] or runtime_results['stdout']}. Iteration: {counter}")

            repair_context = {
                "type": "runtime",
                "previous_code": cleaned_code,
                "stdout": runtime_results["stdout"],
                "stderr": runtime_results["stderr"],
                "exit_code": runtime_results["exit_code"],
                "timed_out": runtime_results["runtime"] == self.runner_timeout,
            }

            if counter >= self.repair_max_iterations:
                print(f"Maximum number of repairs reached ({counter}). Terminating...")
                break

        line_count = sum(1 for line in cleaned_code.splitlines() if line.strip())

        percept_count = cleaned_code.count("Percept(")

        self.db.insert_results(task_id, prompt, self.rag_enabled, self.rag_n, self.model, self.temperature, self.top_k, self.top_p, self.seed, self.timeoutseconds, self.repeat_penalty, self.repeat_last_n, self.num_predict, self.runner_timeout, line_count, percept_count, runtime, success, counter, timed_out, cleaned_code, code_output, "create", failure_reason_category, exit_code)
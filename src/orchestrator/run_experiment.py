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
    
    def run_file_change_experiment(self):

        results_path = self.project_root / "src" / "results" / f"test.py"

        task = """
            You are editing an existing MASPY Python file.

            EXISTING FILE
            from maspy import *

            class DummyAgent(Agent):
                def __init__(self, name,  beliefs, goals):
                    super().__init__(name, beliefs, goals, show_exec=False)
                    self.add(Belief("Box",(5,10)))
                    
                @pl(gain,Goal("move_boxes"), Belief("Box",(Any,Any)))
                def move_to_pos(self, src, position):
                    x, y = position
                    my_pos = self.get(Belief("my_pos",(Any,Any)))
                    self.move(my_pos.values, (x,y))
                    self.print(f"Picking up Box in {x,y}")
                    target_pos = self.get(Belief("target_pos",(Any,Any)))
                    self.move((x,y), target_pos.values)
                    self.print(f"Putting Box in {target_pos.values}")
                    self.stop_cycle()
            
                def move(self, my_pos, target_pos):
                    self.print(f"Moving from {my_pos} to target {target_pos} position")

            if __name__ == "__main__":
                agent_1 = DummyAgent("Dummy_1", [Belief("my_pos",(0,0)),Belief("target_pos",(7,7))], Goal("move_boxes"))

                agent_2 = DummyAgent("Dummy_2", [Belief("my_pos",(3,3)),Belief("target_pos",(3,3))], Goal("move_boxes"))

                Admin().start_system()

            TASK
            - Edit the existing file.
            - Preserve the current structure and existing behaviour unless a change is required for the task.
            - Add one additional agent instance named Dummy_3.
            - Dummy_3 must be instantiated with:
            - Belief("my_pos",(10,10))
            - Belief("target_pos",(1,1))
            - Goal("move_boxes")

            NEW REQUIRED BEHAVIOUR
            - Add a new plan inside DummyAgent with this exact trigger:
            @pl(gain, Goal("return_home"), Belief("start_pos",(Any,Any)))
            - This plan must:
            - get the start_pos belief
            - get the current my_pos belief
            - call self.move(current_position, start_position)
            - print that the agent is returning home
            - stop the cycle

            REQUIRED CHANGES TO EXISTING FLOW
            - In __init__, every agent must store its initial starting position as:
            Belief("start_pos", (x,y))
            where (x,y) matches the initial my_pos passed into the constructor
            - In the existing move_to_pos plan:
            - after putting the box in the target position
            - add the goal Goal("return_home")
            - remove the direct stop_cycle() from move_to_pos
            - The new return_home plan must be the place that calls stop_cycle()

            OUTPUT
            - Output the FULL final file content.
            - Do not output a diff.
            - Do not output partial snippets.
        """


        issues = ""

        valid = False
        counter = 0

        while not valid:
            counter += 1

            print(f"Attempting to build code. Attempt: {counter}")
            prompt = f"""
                Generate valid MASPY Python code by editing an existing file.

                OUTPUT RULES
                - Output ONLY Python code.
                - First line must be exactly: from maspy import *
                - No prose, comments, markdown fences, headings, notes, or explanations.
                - No text before the first line.
                - No text after the final line of code.
                - Output the FULL final file content.
                - If the task cannot be completed using only valid MASPY patterns already present in the file/task, output exactly: FAIL

                CORE RULES
                - Preserve the existing file unless a change is required by the task.
                - Make the smallest valid edit that completes the task.
                - Do not rewrite the whole program unnecessarily.
                - Follow the BDI paradigm already used in the file.
                - Do not invent helper methods, attributes, or alternate API names.
                - Do not invent framework shortcuts.

                PLAN RULES
                - Define plans only inside Agent subclasses.
                - Only use @pl(gain, ...)
                - @pl(...) may contain only Goal(...) and/or Belief(...)
                - Never use Percept(...) inside @pl(...)
                - No keyword arguments inside @pl(...)

                BELIEF / STATE RULES
                - Use only Belief(...) / Goal(...) patterns already demonstrated in the file/task.
                - Do not invent belief helper methods.

                FORBIDDEN
                - get_percepts
                - self.get_percepts
                - update_belief
                - get_belief
                - set_belief
                - delete_belief
                - has_belief
                - self.world
                - world.
                - Admin().get_environment()
                - self.update(
                - self.delete(
                - delete(
                - wait(
                - sleep(
                - log(
                - comments using #

                PLAN SIGNATURE RULE
                - If @pl(...) includes Belief(...) or Goal(...) with values,
                the function MUST include parameters to receive:
                    (self, src, <values...>)
                - The number of parameters must match the trigger/context arguments

                TASK
                {task}

                REPAIR NOTES
                - Previous validation issues:
                {issues}
            """

            generated_code = self.llm.generate(prompt)

            print(generated_code["response"])
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
            counter += 1
            print(f"Attempting to build code. Attempt: {counter}")
            prompt = build_prompt(task_specification, self.rag_enabled, chunks, self.rag_n, issues)

            generated_code = self.llm.generate(prompt)

            print(generated_code["response"])

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
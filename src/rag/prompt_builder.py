import json

from src.rag.retriever import retrieve

def build_prompt(task_specification : dict, rag_enabled : bool, chunks : list[dict] = None, rag_n : int = 0, issues : str = "") -> str:

    """
    Builds a prompt to be submitted to the LLM. Apologies for this functions poor aesthetic.
    
    :param task_specification: .json file of the scenario
    :type task_specification: dict
    :param chunks: list of each chunk from the knowledge
    :type chunks: list[dict]
    :return: A prompt to submit to the LLM
    :rtype: str
    """

    if rag_enabled and (rag_n == 0 or not chunks):
        raise ValueError("Please specify chunks if rag is enabled.")
    
    if rag_n < 0:
        raise ValueError("rag_n must be an integer greater or equal to 0.")
    
    context = ""
    
    if rag_enabled:
        query = f"{task_specification['id']},{task_specification['title']},{task_specification['domain']},{task_specification['desc']}" 
        retrieved_chunks = retrieve(chunks, query, rag_n)

        context = f"""
            == CONTEXT ==
            BEGIN CONTEXT
            {retrieved_chunks}
            END CONTEXT
        """

    issues_block = ""

    if issues:
        findings_for_prompt = []

        raw_findings = []
        if isinstance(issues, dict):
            raw_findings = issues.get("findings", [])
        elif isinstance(issues, list):
            raw_findings = issues

        for finding in raw_findings:
            if isinstance(finding, dict):
                rule = str(finding.get("rule", "validation_rule"))
                message = str(finding.get("message", finding))
            else:
                rule = str(getattr(finding, "rule", "validation_rule"))
                message = str(getattr(finding, "message", finding))

            findings_for_prompt.append((rule, message))

        if findings_for_prompt:
            formatted_findings = "\n".join(
                [f"- [{rule}] {message}" for rule, message in findings_for_prompt]
            )
        elif isinstance(issues, dict):
            formatted_findings = f"- {json.dumps(issues, default=str)}"
        else:
            formatted_findings = f"- {str(issues).strip()}"

        issues_block = f"""
        == VALIDATION FEEDBACK FROM LAST GENERATION ==
        Your previous output failed static validation. You MUST fix every item below in this retry.

        Issues to fix:
        {formatted_findings}

        Retry requirements:
        - Address ALL listed issues.
        - Output ONLY corrected Python code.
        - Do NOT include explanations, markdown, or any non-code text.
        """

    task_json = json.dumps(task_specification, indent=2, sort_keys=True)

    prompt = f"""
        == ROLE ==
        Generate a MASPY program in Python.

        == OUTPUT ==
        - Output ONLY Python code (no prose).
        - First token must be: from maspy import *
        - If any rule cannot be satisfied, output exactly: FAIL
        - After the final line of Python code, output nothing. Do not add summaries. Add zero text that isn't Python code.
        - You must follow the Belief-Desire-Intention paradigm when implementing code. Agents MUST adopt goals in response to beliefs.

        == ABSOLUTE RULES ==
        A) Plans:
        - Only @pl(gain, ...) is allowed.
        - @pl(...) may reference ONLY Goal(...) and/or Belief(...). Never Percept(...).
        - No keyword args in @pl (no "=" in decorator).
        - Your must include an Environment.

        B) Percepts:
        - Percept(...) may appear ONLY inside Environment methods and ONLY in: create/get/change/remove.
        - Percept payload must be: Percept("name", values_tuple=(...))
        - Never use dict payloads. Never use Any inside Percept(...).

        C) Agents:
        - Agent code must NEVER contain Percept(...).
        - Agent code must NEVER call: has(, get(, update(, delete(, wait(, sleep(, log(
        - Agent counters/progress MUST use Python attributes (e.g. self.coins_collected). Do NOT use beliefs for counters.

        D) Connect:
        - Must call exactly: Admin().connect_to([agents...], env_instance)
        - Then: Admin().start_system()
        
        E) Output:
        - You must NOT output any backticks at the start or end of your output.
        - You must NOT send any non-code English text to your output.
        - You must NOT include ANY descriptions or introductions explaining the code. You must output the plain Python code as if your entire output was going to be placed into a Python file directly.

        F) Task completion:
        - The agent must continue acting until the goal condition is satisified.
        - The plan must re-trigger itself (e.g., by re-adding a Goal) if the task requires multiple steps.
        - The program must only terminate after the success condition is reached.

        == FORBIDDEN TOKENS (MUST NOT APPEAR ANYWHERE) ==
        has(
        get(
        update
        delete(
        wait(
        sleep(
        log(

        == TASK ==
        BEGIN TASK
        {task_json}
        END TASK

        {issues_block}

        {context}
        """

    return prompt

# The following is AI generated. It will be removed when I get closer to being done, it just lets me test for now.

if __name__ == "__main__":
    import json
    from pathlib import Path
    from src.rag.loader import load_corpus
    from src.llm.llm import LLM

    project_root = Path(__file__).resolve().parents[2]

    task_path = project_root / "planning" / "scenario_ideas" / "coin_collector.json"
    corpus_path = project_root / "knowledge" / "maspy"
    results_path = project_root / "src" / "results"
    generated_output_path = results_path / "warehouse_generated.py"

    with open(task_path, "r", encoding="utf-8") as tf:
        task_specification = json.load(tf)

    chunks = load_corpus(corpus_path)
    prompt = build_prompt(task_specification, chunks)

    llm = LLM()
    generated_code = llm.generate(prompt)

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
    generated_output_path.write_text(cleaned_code, encoding="utf-8")
    print(prompt)
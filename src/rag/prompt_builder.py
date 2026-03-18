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
        Generate a MASPY program in Python.

        OUTPUT RULES
        - Output ONLY Python code.
        - First line must be exactly: from maspy import *
        - No prose, comments, markdown fences, headings, notes, or explanations.
        - No text before the first line.
        - No text after the final line of code.
        - If the task cannot be completed using only valid MASPY patterns from CONTEXT, output exactly: FAIL

        CORE RULES
        - Use only MASPY API patterns shown in CONTEXT.
        - Do not invent helper methods, attributes, or alternate API names.
        - Do not invent framework shortcuts.
        - Follow the BDI paradigm: beliefs/goals trigger plans, and plans perform actions.

        PLAN RULES
        - Define plans only inside Agent subclasses.
        - Only use @pl(gain, ...)
        - @pl(...) may contain only Goal(...) and/or Belief(...)
        - Never use Percept(...) inside @pl(...)
        - No keyword arguments inside @pl(...)

        PERCEPT RULES
        - Percept syntax must be exactly: Percept("name", (...))
        - Never use values_tuple=
        - Percept(...) may appear only inside Environment methods
        - Agent code must never contain Percept(...)
        - Never use Any inside Percept(...)

        BELIEF / STATE RULES
        - Use Python attributes for counters/progress
        - When updating a belief, remove the old belief with rm(...) and add the new belief with add(...)
        - Do not use invented belief helpers

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

        RUNTIME RULES
        - Define exactly one Environment subclass named CoinWorld
        - Define exactly one Agent subclass named Collector
        - Instantiate the environment
        - Instantiate the agent
        - Pass env into the agent constructor and store it as self.env
        - Include exactly one line: Admin().connect_to([collector], env)
        - Include exactly one line: Admin().start_system()
        - Do not use if __name__ == "__main__":

        TASK SPEC
        - Environment name: CoinWorld
        - Agent name: Collector
        - One Collector agent
        - Target: collect 3 coins
        - Initial belief: Belief("coin_count", (0,))
        - Initial goal: Goal("collect", (3,))
        - The environment manages coin state
        - The agent must collect coins until count reaches 3
        - After collecting a coin:
        - the agent gains Belief("has_coin", (coin_id,))
        - the old coin_count belief is removed
        - the new coin_count belief is added
        - the Python counter is incremented
        - If target not yet reached, re-add the collect goal
        - Stop only after the target is reached

        IMPLEMENTATION CONSTRAINTS
        - Do not scan percept lists unless CONTEXT shows an exact valid MASPY pattern for doing so
        - Do not invent environment removal/update APIs unless CONTEXT shows them
        - If an operation is required, implement it only using syntax demonstrated in CONTEXT
        - Prefer the simplest valid implementation that satisfies the task
        - Do not add extra features, metrics, printing, logging, randomisation, or assumptions not required by the task

        REPAIR NOTES
        {issues_block}

        CONTEXT
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
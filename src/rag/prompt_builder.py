from retriever import retrieve

def build_prompt(task_specification : dict, chunks : list[dict]) -> str:

    """
    Builds a prompt to be submitted to the LLM. Apologies for this functions poor aesthetic.
    
    :param task_specification: .json file of the scenario
    :type task_specification: dict
    :param chunks: list of each chunk from the knowledge
    :type chunks: list[dict]
    :return: A prompt to submit to the LLM
    :rtype: str
    """

    agents = []

    for i in range(len(task_specification["agents"])):
        agents.append(task_specification["agents"][i]["id"])

    prompt = "You are an expert Python developer generating MASPY BDI multi-agent code. TASK SPECIFICATION (JSON): "

    prompt = f"{prompt}{task_specification}"

    prompt = f"{prompt} You must implement THIS EXACT task specification, not any unrelated MASPY example. DO NOT output placeholder demo agents (e.g., Hello World, DummyAgent, MASPYAgent). If you cannot comply using CONTEXT only, output exactly: FAIL. HARD CONSTRAINTS: Use only MASPY APIs and patterns shown in the context section below. Do not invent MASPY decorators, classes, functions, or parameters that are not present in CONTEXT. Output ONLY Python code (no markdown, no explanations). "

    prompt = f"{prompt} OUTPUT REQUIREMENTS: Provide a minimal runnable MASPY program. Define the environment (if applicable in MASPY patterns show CONTEXT)."

    prompt = f"{prompt} SYSTEM START REQUIRMENT: If the task spec includes an environment, toy MUST define an Environment sublass, instanitate it, and call: Admin().connect_to(agent_list, env_instance). NEVER call Admin().connect_to(..., None). connect_to expects an Environment or Channel. Then call Admin().start_system()."

    if len(agents) > 0:
        prompt = f"{prompt} Define the following agents: {agents}."

    prompt = f"{prompt}Use appropriate plan triggers for belief/goal/percept changes as demonstrated in CONTEXT. Start the system using the pattern shown in CONTEXT. Keep code concise and aligned with examples."

    query = f"{task_specification['task_id']},{task_specification['title']},{task_specification['domain']},{task_specification['description']}"

    retrieved_chunks = retrieve(chunks, query)

    prompt = f"{prompt}CONTEXT (retrieved MASPY docs/examples): Below are trusted snippets from MASPY documentation and official examples. Follow these to understand how MASPY works: {retrieved_chunks}"

    prompt = f"{prompt} Using the task specification and provided context, generate MASPY agent code now. Remember: ONLY Python code, no invented APIs. Ensure your entire response is ONLY the Python code. Do NOT include any plain English. Your response will go directly into a .py file. Do NOT include any backticks before or after your response. Ensure every library you use is properly imported at the start of your code. ENSURE THAT YOU FOLLOW THE TASK SPECIFICATION. DEFINE ALL AGENTS SPECIFIED. DEFINE THE EXACT ENVIRONMENT SPECIFIED. DEFINE EVERY ACTION SPECIFIED. ETC."

    return prompt

# The following is AI generated. It will be removed when I get closer to being done, it just lets me test for now.

if __name__ == "__main__":
    import sys
    import json
    from pathlib import Path
    from loader import load_corpus

    project_root = Path(__file__).resolve().parents[2]
    src_root = project_root / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from llm.llm import LLM

    task_path = project_root / "planning" / "scenario_ideas" / "warehouse.json"
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
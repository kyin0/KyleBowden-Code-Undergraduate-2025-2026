import json

from src.rag.retriever import retrieve


def _format_task_description(description: str) -> str:
    lines = []

    for raw_line in description.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("-"):
            line = line[1:].strip()

        lines.append(f"- {line}")

    return "\n".join(lines)


def _format_chunk(chunk: dict) -> str:
    chunk_lines = chunk["text"].strip().splitlines()
    preview = "\n".join(chunk_lines[:40]).strip()

    return (
        f"SOURCE: {chunk['source']}\n"
        f"TITLE: {chunk['title']}\n"
        f"CONTENT:\n{preview}"
    )


def _select_context_chunks(task_specification: dict, chunks: list[dict], rag_n: int) -> list[dict]:
    description = task_specification.get("description", "").lower()
    indexed_chunks = {chunk["id"]: chunk for chunk in chunks}
    selected_chunks = []
    selected_ids = set()
    context_budget = max(rag_n, 4)

    preferred_ids = [
        "wiki_05_managing_beliefs_goals",
        "wiki_06_defining_plans",
        "ex_06_hello_world",
    ]

    if "environment" in description:
        preferred_ids.append("wiki_09_environment")

    if any(token in description for token in ["send", "message", "communicat", "buyer", "seller"]):
        preferred_ids.append("wiki_08_agent_communication")

    for chunk_id in preferred_ids:
        chunk = indexed_chunks.get(chunk_id)

        if chunk and chunk_id not in selected_ids and len(selected_chunks) < context_budget:
            selected_chunks.append(chunk)
            selected_ids.add(chunk_id)

    for chunk in retrieve(chunks, task_specification.get("description", ""), max(rag_n, 6)):
        if chunk["id"] in selected_ids:
            continue

        selected_chunks.append(chunk)
        selected_ids.add(chunk["id"])

        if len(selected_chunks) >= context_budget:
            break

    return selected_chunks


def _format_repair_block(repair_context: dict | None) -> str:
    if not repair_context:
        return ""

    previous_code = repair_context.get("previous_code", "").strip()
    previous_code_block = previous_code if previous_code else "<empty>"

    if repair_context["type"] == "static":
        findings = repair_context.get("findings", [])
        formatted_findings = "\n".join(
            f"- [{finding.rule}] {finding.message}" for finding in findings
        ) or "- Unknown static validation failure"

        return f"""
        RETRY INSTRUCTIONS
        - The previous attempt failed static validation.
        - Keep any working structure from the previous attempt.
        - Fix every issue below before changing anything else.
        - Do not output FAIL just because the previous attempt had errors.
        - Output the full corrected file only.

        STATIC FAILURES
        {formatted_findings}

        PREVIOUS ATTEMPT
        ```python
        {previous_code_block}
        ```
        """

    stdout = repair_context.get("stdout", "").strip()
    stderr = repair_context.get("stderr", "").strip()
    exit_code = repair_context.get("exit_code")
    timed_out = repair_context.get("timed_out", False)
    failure_header = "The previous attempt timed out." if timed_out else "The previous attempt failed at runtime."

    runtime_lines = [
        f"- Exit code: {exit_code}",
    ]

    if stdout:
        runtime_lines.append(f"- Stdout: {stdout}")

    if stderr:
        runtime_lines.append(f"- Stderr: {stderr}")

    formatted_runtime = "\n".join(runtime_lines)

    return f"""
        RETRY INSTRUCTIONS
        - {failure_header}
        - Preserve the valid MASPY structure from the previous attempt.
        - Fix the runtime failure without rewriting the whole file unless necessary.
        - Do not output FAIL just because the previous attempt had errors.
        - Output the full corrected file only.

        RUNTIME FAILURE
        {formatted_runtime}

        PREVIOUS ATTEMPT
        ```python
        {previous_code_block}
        ```
        """


def build_prompt(task_specification : dict, rag_enabled : bool, chunks : list[dict] = None, rag_n : int = 0, repair_context : dict | None = None) -> str:

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
        selected_chunks = _select_context_chunks(task_specification, chunks, rag_n)
        formatted_chunks = "\n\n".join(_format_chunk(chunk) for chunk in selected_chunks)
        context = f"""
        REFERENCE CONTEXT
        {formatted_chunks}
        """

    issues_block = _format_repair_block(repair_context)
    formatted_task = _format_task_description(task_specification["description"])

    prompt = f"""
        Generate one complete MASPY Python program from the task description.

        OUTPUT
        - ONLY Python code
        - First line: from maspy import *
        - No comments, prose, markdown, or extra text
        - Include a normal Python entrypoint using if __name__ == "__main__":
        - Only output FAIL if the task is fundamentally impossible or self-contradictory under the MASPY subset below
        - If a previous attempt failed, repair it instead of outputting FAIL

        CORE
        - Use the MASPY subset shown in REFERENCE CONTEXT
        - Do NOT invent APIs, helpers, or shortcuts
        - Follow BDI: goals/beliefs trigger plans
        - Favor the smallest runnable implementation that satisfies the task

        PLANS
        - Only inside Agent classes
        - Only use: @pl(gain, ...)
        - Allowed in @pl: Goal(...), Belief(...) ONLY
        - NEVER use Percept(...) in @pl
        - NO keyword arguments in @pl
        - Plan body may call Environment helper methods through self.env
        - MASPY plan decorator shape is: @pl(change, changed_data, context)
        - After gain, use one trigger term and at most one context argument
        - If more than one context condition is needed, wrap them in a list as the third argument
        - Never write a fourth positional argument in @pl(...); MASPY will ignore it and the plan signature will break
        - If a plan is intended to run repeatedly while values change over time, never hardcode those changing values in Goal(...) or Belief(...) inside the decorator
        - For changing Goal/Belief values, use wildcard matching with Any, for example Goal("collect", (Any,)) and Belief("coin_count", (Any,))
        - Any is allowed in Goal(...) and Belief(...), but never in Percept(...)

        SIGNATURE RULE (CRITICAL)
        - Plan must be: def name(self, src, ...)
        - Include ONE parameter per value contained in changed_data and context Goal/Belief terms
        - Goal values come before Belief context values
        - Goal/Belief terms with no values contribute no parameter
        - If context is a list, count values across every item in the list

        Examples:
        @pl(gain, Goal("turn_on"), Belief("light_state", ("off",)))
        → def turn_light_on(self, src, light_state)

        @pl(gain, Goal("collect", (3,)), Belief("coin", (1,)))
        → def collect_coin(self, src, target, coin_value)

        @pl(gain, Goal("patrol"), [Belief("patrol_point", (Any,)), Belief("alert_state", ("pending",))])
        → def patrol(self, src, patrol_point, alert_state)

        - NEVER mismatch parameters

        PERCEPTS
        - Environment owns percept creation and percept mutation
        - Inside Environment classes, self.create(...), self.add(...), self.rm(...), self.get(...), and self.change(...) must operate on Percept(...), not Belief(...) or Goal(...)
        - Agents should not create or change Percept objects directly
        - NEVER use Any
        - NEVER use values_tuple=
        - Do NOT use True or False inside Percept values; encode state with strings instead

        BELIEFS
        - Use add(...) and rm(...)
        - Remove old belief before adding updated one
        - Use Python variables for counters
        - If a looping goal still has work left, re-add that goal
        - If the current looping goal has finished, stop, terminate, or return without calling self.rm(Goal(...)) on the same trigger goal
        - If the task says to stop or terminate after success, the success branch must explicitly call self.stop_cycle()
        - Do NOT rely on a goal being cleared automatically to stop the program
        - Do NOT use True or False inside Belief or Goal values; encode state with strings like "pending", "sent", "locked", "unlocked", "detected"

        FORBIDDEN
        get_percepts, self.get_percepts, update_belief, get_belief,
        set_belief, delete_belief, has_belief,
        self.world, world., Admin().get_environment(),
        self.update(, self.delete(, delete(,
        wait(, sleep(, log(, self.change(

        RUNTIME
        - Exactly ONE Environment class
        - At least ONE Agent class
        - Instantiate the environment in the entrypoint
        - Instantiate each agent with the environment and store it as self.env
        - Use Admin().connect_to([...agents...], env) before Admin().start_system()

        CONSTRAINTS
        - Do NOT scan percepts unless shown in CONTEXT
        - Do NOT invent environment APIs
        - Use ONLY demonstrated patterns
        - Keep implementation minimal and correct
        - NO extra features, logging, randomness

        IMPLEMENTATION PATTERN
        - Put task state owned by the world into the Environment as plain Python attributes.
        - Expose one small Environment method for each state-changing action the agent must perform.
        - Let plans trigger from Goal(...) and Belief(...) updates, not percept decorators.
        - For counter tasks: read the current belief value, call the environment helper, rm the old belief, add the new belief, then either re-add the goal or stop.
        - Re-add a goal only when more work is still required.
        - When a plan updates a belief that appears in its decorator context, that decorator context should usually use Any rather than a hardcoded literal.
        - When the final success state is reached, call self.stop_cycle() in that success path so the run finishes before timeout.
        - Represent boolean-like state symbolically using strings, not Python booleans inside MASPY terms.

        CRITICAL SIGNATURE LAW
        - MASPY uses @pl(change, changed_data, context).
        - The plan function must be:
        def plan_name(self, src, <changed_data values>, <context values>)
        - If there are multiple context conditions, they must be provided inside a list in the third decorator argument.
        - Every value inside the trigger and context terms contributes one positional argument.
        - If a Goal or Belief has no values, it contributes no extra argument.

        TASK
        {formatted_task}

        REPAIR
        {issues_block}

        CONTEXT
        {context}
    """

    return prompt

def _clean_generated_code(response_text: str) -> str:
    cleaned_code = response_text.strip()

    if cleaned_code.startswith("```"):
        lines = cleaned_code.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        cleaned_code = "\n".join(lines).strip()

    return cleaned_code.replace("```python", "").replace("```", "").replace("`", "")
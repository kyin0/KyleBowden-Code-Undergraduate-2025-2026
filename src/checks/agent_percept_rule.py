from src.checks.types import Finding

class AgentPerceptRule:

    def check(self, code : str):
        
        if "class" in code and "Agent" in code and "Percept(" in code:

            if "Environment" not in code:
                return Finding("agent_percept", "Percept used outside Environment")

        return None
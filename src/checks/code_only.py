from src.checks.types import Finding

class CodeOnlyRule:

    def check(self, code : str):
        if not code.startswith("from maspy import *"):
            return Finding("code_only", "Code must start with 'from maspy import *")
        
        forbidden_phrases = [
            "Here is",
            "Explanation",
            "The following code",
            "```"
        ]

        for phrase in forbidden_phrases:
            if phrase in code:
                return Finding("code_only", "Output contains non-code text.")

        return None
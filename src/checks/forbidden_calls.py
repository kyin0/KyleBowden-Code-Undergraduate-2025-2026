from src.checks.types import Finding
import re

class ForbiddenCallsRule:

    def check(self, code : str):

        if re.search(r"Percept\s*\([^\)]*\bAny\b[^\)]*\)", code):
            return Finding(
                "forbidden_calls",
                "Percept cannot contain Any. Use explicit concrete values_tuple entries instead."
            )
        
        hallucinations = [
            "get_belief(",
            "set_belief(",
            "update_belief(",
            "delete_belief(",
            "has_belief(",
            "self.delete(",
            "self.remove(",
            "self.world"
        ]

        for hallucination in hallucinations:
            if hallucination in code:
                return Finding("forbidden_calls", f"Forbidden MASPY API call used: {hallucination}")
            
        return None
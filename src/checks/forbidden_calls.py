from src.checks.types import Finding
from src.checks.text_utils import extract_call_inners, contains_token

class ForbiddenCallsRule:

    def check(self, code : str):

        if self._percept_contains_any(code):
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
            "self.world",
            "Admin().cycle()",
            "self.env_instance",
            "request_percept",
            "create_percept",
            "get_belief_value"
        ]

        for hallucination in hallucinations:
            if hallucination in code:
                return Finding("forbidden_calls", f"Forbidden MASPY API call used: {hallucination}")
            
        return None

    def _percept_contains_any(self, code: str) -> bool:
        for inner in extract_call_inners(code, "Percept"):
            if contains_token(inner, "Any"):
                return True

        return False
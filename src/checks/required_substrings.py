from src.checks.types import Finding

class RequiredSubstringsRule:

    def check(self, code : str):
        
        required = [
            "class",
            "@pl(",
            "Admin().connect_to"
        ]

        for component in required:
            if component not in code:
                return Finding("required_substrings", f"Required component missing: {component}")
            
        return None
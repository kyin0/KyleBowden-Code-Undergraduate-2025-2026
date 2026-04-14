from src.checks.types import Finding
from src.checks.text_utils import find_matching_paren, split_top_level

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

        if not self._has_admin_connect_agents_list(code):
            return Finding("required_substrings", "Admin().connect_to(...) must receive the agents as a list")

        if "if __name__ == \"__main__\":" not in code:
            return Finding("required_substrings", "Code must include a standard __main__ entrypoint")
            
        return None

    def _has_admin_connect_agents_list(self, code: str) -> bool:
        token = "Admin().connect_to("
        start = 0

        while True:
            marker = code.find(token, start)

            if marker == -1:
                return False

            open_paren = marker + len("Admin().connect_to")
            close_paren = find_matching_paren(code, open_paren)

            if close_paren == -1:
                return False

            inner = code[open_paren + 1:close_paren]
            args = split_top_level(inner)

            if args:
                first = args[0].strip()

                if first.startswith("[") and first.endswith("]") and first[1:-1].strip():
                    return True

            start = close_paren + 1

        return False
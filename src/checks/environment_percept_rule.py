from src.checks.types import Finding
from src.checks.text_utils import find_matching_paren


class EnvironmentPerceptRule:

    def check(self, code: str):
        lines = code.splitlines()

        in_environment_class = False
        environment_indent = 0

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            indent = len(line) - len(line.lstrip())

            if stripped.startswith("class "):
                in_environment_class = "(Environment)" in stripped
                environment_indent = indent
                continue

            if in_environment_class and indent <= environment_indent and not stripped.startswith("@"):
                in_environment_class = False

            if not in_environment_class:
                continue

            for method_name in ["create", "add", "rm", "get", "change"]:
                call_token = f"self.{method_name}("
                marker = stripped.find(call_token)

                if marker == -1:
                    continue

                open_paren = marker + len(f"self.{method_name}")
                close_paren = find_matching_paren(stripped, open_paren)

                if close_paren == -1:
                    continue

                call_text = stripped[open_paren + 1:close_paren]

                for term_name in ["Belief(", "Goal("]:
                    cleaned = call_text.lstrip()

                    if cleaned.startswith(term_name):
                        return Finding(
                            "environment_percept",
                            f"Environment method self.{method_name}(...) must use Percept terms, not {term_name[:-1]}."
                        )

        return None
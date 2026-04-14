from src.checks.types import Finding

class PlanRule:

    def _extract_decorators(self, code: str) -> list[str]:
        decorators = []
        start = 0

        while True:
            marker = code.find("@pl(", start)

            if marker == -1:
                break

            cursor = marker + len("@pl(")
            depth = 1

            while cursor < len(code) and depth > 0:
                char = code[cursor]

                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1

                cursor += 1

            decorators.append(code[marker + len("@pl("):cursor - 1])
            start = cursor

        return decorators

    def check(self, code : str):
        decorators = self._extract_decorators(code)

        for dec in decorators:
            normalized = dec.strip()

            if not normalized.startswith("gain"):
                return Finding("plan_rule", "@pl must use gain event")
            
            if "Percept(" in normalized:
                return Finding("plan_rule", "Percept cannot appear in @pl decorator")

            if "=" in normalized:
                return Finding("plan_rule", "Keyword arguments are not allowed inside @pl decorators")
        
        return None
from src.checks.types import Finding


class SyntaxRule:

    def check(self, code: str):
        try:
            compile(code, "<generated>", "exec")
        except SyntaxError as error:
            line = error.lineno or 0
            column = error.offset or 0
            message = error.msg or "invalid syntax"
            return Finding("syntax", f"Syntax error at line {line}, column {column}: {message}")

        return None
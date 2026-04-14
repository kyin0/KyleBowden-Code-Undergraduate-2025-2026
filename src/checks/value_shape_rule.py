from src.checks.types import Finding
from src.checks.text_utils import extract_call_inners, split_top_level, contains_token


class ValueShapeRule:

    def check(self, code: str):
        for term_name in ["Belief", "Goal", "Percept"]:
            calls = extract_call_inners(code, term_name)

            for call in calls:
                args = split_top_level(call)

                if len(args) < 2:
                    continue

                if self._contains_boolean_literal(args[1]):
                    return Finding(
                        "value_shape",
                        f"{term_name} values must not contain True/False literals. Encode state with strings or symbolic beliefs instead, for example ('sent',) or ('pending',)."
                    )

        return None

    def _contains_boolean_literal(self, text: str) -> bool:
        return contains_token(text, "True") or contains_token(text, "False")
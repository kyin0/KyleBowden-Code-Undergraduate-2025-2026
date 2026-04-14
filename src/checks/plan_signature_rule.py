from src.checks.types import Finding
from src.checks.text_utils import collect_plan_functions, split_top_level


class PlanSignatureRule:

    def check(self, code: str):
        for plan in collect_plan_functions(code):
            decorator_args = split_top_level(plan["decorator"])

            if len(decorator_args) > 3:
                return Finding(
                    "plan_signature",
                    f"Plan '{plan['name']}' passes too many top-level arguments to @pl(...). MASPY expects @pl(change, changed_data, context). If you need multiple context conditions, wrap them in a list as the third argument."
                )

            expected_values = 0

            for argument in decorator_args[1:]:
                expected_values += self._count_bound_values(argument)

            actual_values = max(plan["parameter_count"] - 2, 0)

            if actual_values != expected_values:
                return Finding(
                    "plan_signature",
                    f"Plan '{plan['name']}' has the wrong signature. Expected def {plan['name']}(self, src, ...) with {expected_values} trigger/context value argument(s), but found {actual_values}."
                )

        return None

    def _count_bound_values(self, text: str) -> int:
        normalized = text.strip()

        for term_name in ["Goal", "Belief"]:
            token = f"{term_name}("

            if normalized.startswith(token) and normalized.endswith(")"):
                inner = normalized[len(token):-1]
                term_args = split_top_level(inner)

                if len(term_args) < 2:
                    return 0

                return self._count_values_in_term(term_args[1])

        if normalized.startswith("[") and normalized.endswith("]"):
            inner = normalized[1:-1]
            return sum(self._count_bound_values(part) for part in split_top_level(inner))

        if normalized.startswith("(") and normalized.endswith(")"):
            inner = normalized[1:-1]
            return sum(self._count_bound_values(part) for part in split_top_level(inner))

        if normalized.startswith("{") and normalized.endswith("}"):
            inner = normalized[1:-1]
            return sum(self._count_bound_values(part) for part in split_top_level(inner))

        return 0

    def _count_values_in_term(self, text: str) -> int:
        normalized = text.strip()

        if normalized.startswith("(") and normalized.endswith(")"):
            inner = normalized[1:-1]

            if not inner.strip():
                return 0

            return len(split_top_level(inner))

        return 1

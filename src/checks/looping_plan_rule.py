from src.checks.types import Finding
from src.checks.text_utils import collect_plan_functions, extract_call_inners, split_top_level, contains_token, literal_string, find_matching_paren


class LoopingPlanRule:

    def check(self, code: str):
        for plan in collect_plan_functions(code):
            decorator_calls = self._collect_goal_belief_calls(plan["decorator"])
            body_text = plan["body"]

            if not decorator_calls:
                continue

            trigger_goal_names = {
                entry["name"] for entry in decorator_calls if entry["kind"] == "Goal"
            }
            decorator_beliefs = {
                entry["name"]: entry for entry in decorator_calls if entry["kind"] == "Belief"
            }

            added_goals, removed_goals, mutated_beliefs = self._collect_body_updates(body_text)

            for goal_name in trigger_goal_names:
                if goal_name in removed_goals:
                    return Finding(
                        "looping_plan",
                        f"Plan '{plan['name']}' removes Goal(\"{goal_name}\") even though that goal is the current trigger. For looping goals, re-add it if work remains; otherwise stop or return without self.rm(Goal(...))."
                    )

            looping_goal_names = trigger_goal_names & added_goals

            for entry in decorator_calls:
                if entry["kind"] != "Goal":
                    continue

                if entry["name"] not in looping_goal_names:
                    continue

                if entry["has_values"] and not entry["uses_any"]:
                    return Finding(
                        "looping_plan",
                        f"Plan '{plan['name']}' re-adds Goal(\"{entry['name']}\") while it loops, so the decorator must use wildcard matching for dynamic values, for example Goal(\"{entry['name']}\", (Any,))."
                    )

            if looping_goal_names:
                for belief_name in mutated_beliefs:
                    entry = decorator_beliefs.get(belief_name)

                    if entry and entry["has_values"] and not entry["uses_any"]:
                        return Finding(
                            "looping_plan",
                            f"Plan '{plan['name']}' updates Belief(\"{belief_name}\") over time while re-adding the same goal, so the decorator must use wildcard matching, for example Belief(\"{belief_name}\", (Any,))."
                        )

        return None

    def _collect_goal_belief_calls(self, decorator_text: str) -> list[dict]:
        extracted = []

        decorator_args = split_top_level(decorator_text)

        for argument in decorator_args[1:]:
            extracted.extend(self._extract_calls_from_text(argument))

        return extracted

    def _extract_calls_from_text(self, text: str) -> list[dict]:
        extracted = []

        for term_name in ["Goal", "Belief"]:
            for inner in extract_call_inners(text, term_name):
                args = split_top_level(inner)
                name = literal_string(args[0]) if args else None

                if name is not None:
                    extracted.append(
                        {
                            "kind": term_name,
                            "name": name,
                            "uses_any": contains_token(inner, "Any"),
                            "has_values": len(args) > 1,
                        }
                    )

        return extracted

    def _collect_body_updates(self, body_text: str):
        added_goals = set()
        removed_goals = set()
        mutated_beliefs = set()

        for method in ["add", "rm"]:
            method_token = f"self.{method}("
            start = 0

            while True:
                marker = body_text.find(method_token, start)

                if marker == -1:
                    break

                close_index = find_matching_paren(body_text, marker + len(f"self.{method}"))

                if close_index == -1:
                    break

                inner = body_text[marker + len(method_token):close_index]
                target_name, target_term = self._extract_first_term(inner)

                if target_name is not None and target_term == "Goal":
                    if method == "add":
                        added_goals.add(target_name)
                    else:
                        removed_goals.add(target_name)

                if target_name is not None and target_term == "Belief":
                    mutated_beliefs.add(target_name)

                start = close_index + 1

        return added_goals, removed_goals, mutated_beliefs

    def _extract_first_term(self, text: str) -> tuple[str | None, str | None]:
        for term_name in ["Goal", "Belief"]:
            token = f"{term_name}("
            stripped = text.strip()

            if not stripped.startswith(token):
                continue

            close_index = find_matching_paren(stripped, len(term_name))

            if close_index == -1:
                continue

            inner = stripped[len(token):close_index]
            args = split_top_level(inner)

            if not args:
                return None, term_name

            return literal_string(args[0]), term_name

        return None, None

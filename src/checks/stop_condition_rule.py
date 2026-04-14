from src.checks.types import Finding


class StopConditionRule:

    def check(self, code: str, task_specification: dict | None = None):
        if not task_specification:
            return None

        description = str(task_specification.get("description", "")).lower()

        if not any(token in description for token in ["stop only after", "must stop", "terminate", "timeout"]):
            return None

        if "self.stop_cycle(" in code:
            return None

        return Finding(
            "stop_condition",
            "Task requires an explicit stopping condition. The success path must call self.stop_cycle(); do not rely on goal clearance alone to end execution."
        )
import inspect

from src.checks.agent_percept_rule import AgentPerceptRule
from src.checks.code_only import CodeOnlyRule
from src.checks.environment_percept_rule import EnvironmentPerceptRule
from src.checks.forbidden_calls import ForbiddenCallsRule
from src.checks.looping_plan_rule import LoopingPlanRule
from src.checks.plan_signature_rule import PlanSignatureRule
from src.checks.plan_rules import PlanRule
from src.checks.required_substrings import RequiredSubstringsRule
from src.checks.stop_condition_rule import StopConditionRule
from src.checks.syntax_rule import SyntaxRule
from src.checks.value_shape_rule import ValueShapeRule

class StaticChecker:

    def __init__(self):

        self.rules = [
            SyntaxRule(),
            AgentPerceptRule(),
            EnvironmentPerceptRule(),
            CodeOnlyRule(),
            ForbiddenCallsRule(),
            ValueShapeRule(),
            PlanRule(),
            PlanSignatureRule(),
            LoopingPlanRule(),
            StopConditionRule(),
            RequiredSubstringsRule(),
        ]
    
    def validate(self, code, task_specification=None):

        findings = []

        for rule in self.rules:
            parameters = inspect.signature(rule.check).parameters

            if len(parameters) > 1:
                result = rule.check(code, task_specification)
            else:
                result = rule.check(code)

            if result:
                findings.append(result)
        
        return {
            "pass": len(findings) == 0,
            "findings": findings
        }
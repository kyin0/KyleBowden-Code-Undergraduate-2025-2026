from src.checks.agent_percept_rule import AgentPerceptRule
from src.checks.code_only import CodeOnlyRule
from src.checks.forbidden_calls import ForbiddenCallsRule
from src.checks.plan_rules import PlanRule
from src.checks.required_substrings import RequiredSubstringsRule

class StaticChecker:

    def __init__(self):

        self.rules = [
            AgentPerceptRule(),
            CodeOnlyRule(),
            ForbiddenCallsRule(),
            PlanRule(),
            #RequiredSubstringsRule(),
        ]
    
    def validate(self, code):

        findings = []

        for rule in self.rules:
            result = rule.check(code)

            if result:
                findings.append(result)
        
        return {
            "pass": len(findings) == 0,
            "findings": findings
        }
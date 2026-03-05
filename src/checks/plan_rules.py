from src.checks.types import Finding
import re

class PlanRule:

    def check(self, code : str):
        
        decorators = re.findall(r"@pl\((.*?)\)", code)

        for dec in decorators:

            if not dec.startswith("gain"):
                return Finding("plan_rule", "@pl must use gain event")
            
            if "Percept(" in dec:
                return Finding("plan_rule", "Percept cannot appear in @pl decorator")
        
        return None
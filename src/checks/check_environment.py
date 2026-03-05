from src.checks.types import Finding

class EnvironmentRule:

    def check(self, code : str):
        
        if "Environment" not in code:
            return Finding("no_environment", "No environment was defined for this code. You must make sure to define one.")

        return None
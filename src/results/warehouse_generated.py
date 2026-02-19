from maspy import *

class Picker(Agent):
    def __init__(self, agent_name=None):
        super().__init__(agent_name)
        self.add(Belief("packages", [], adds_event=False))
        self.add(Goal("pick_package", (), source="self"))

    @pl(gain=Goal("pick_package"))
    def pick_package(self, src):
        if not self.get_belief("packages"):
            self.print("No packages to pick.")
            self.stop_cycle()
        else:
            package = self.get_belief("packages").pop(0)
            self.add(Belief("current_package", package))
            self.print(f"Picked package: {package}")
            self.rm(Goal("pick_package"))
            self.add(Goal("deliver_package", (), source="self"))

class Deliverer(Agent):
    def __init__(self, agent_name=None):
        super().__init__(agent_name)
        self.add(Belief("current_package", None, adds_event=False))
        self.add(Goal("deliver_package", (), source="self"))

    @pl(gain=Goal("deliver_package"))
    def deliver_package(self, src):
        if not self.get_belief("current_package"):
            self.print("No package to deliver.")
            self.stop_cycle()
        else:
            package = self.get_belief("current_package")
            self.print(f"Delivered package: {package}")
            self.rm(Goal("deliver_package"))
            self.add(Belief("current_package", None))

class PickerEnvironment(Environment):
    def __init__(self):
        super().__init__()
        self.packages = ["Package1", "Package2", "Package3"]

    def perceive(self, agent):
        if isinstance(agent, Picker) and not agent.get_belief("packages"):
            agent.add(Belief("packages", self.packages.copy(), source="environment"))

if __name__ == "__main__":
    picker_env = PickerEnvironment()
    picker1 = Picker("Picker1")
    deliverer1 = Deliverer("Deliverer1")

    Admin().connect_to([picker1, deliverer1], picker_env)
    Admin().start_system()
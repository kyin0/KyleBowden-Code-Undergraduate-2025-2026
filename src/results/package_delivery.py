from maspy import *

class DeliveryWorld(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.create(Percept("package", ("depot", "package1"), adds_event=False))
        self.create(Percept("package", ("depot", "package2"), adds_event=False))
        self.create(Percept("location", ("depot",), adds_event=False))
        self.create(Percept("location", ("delivery1",), adds_event=False))
        self.create(Percept("location", ("delivery2",), adds_event=False))

    def pick_up_package(self, agent, package_id):
        package = self.get(Percept("package", (agent.env.name, package_id)))
        if package and package.values[1] == "depot":
            self.change(package, (agent.env.name, "picked_up"))
            return True
        return False

    def deliver_package(self, agent, package_id, location):
        package = self.get(Percept("package", (agent.env.name, package_id)))
        if package and package.values[1] == "picked_up":
            self.change(package, (agent.env.name, "delivered"))
            self.create(Percept("package", (location, package_id), adds_event=False))
            return True
        return False

class Courier(Agent):
    def __init__(self, agent_name=None):
        super().__init__(agent_name)
        self.add(Belief("delivered_count", (0,), adds_event=False))
        self.add(Belief("at_location", ("depot",), adds_event=False))
        self.add(Goal("deliver_packages", (2,), source=self))

    @pl(gain, Goal("deliver_packages", (Any,)), Belief("delivered_count", (Any,)))
    def deliver_packages(self, src, target, delivered_count):
        if delivered_count < 2:
            package_id = f"package{delivered_count + 1}"
            if self.env.pick_up_package(self, package_id):
                self.rm(Belief("delivered_count", (delivered_count,), adds_event=False))
                self.add(Belief("delivered_count", (delivered_count + 1,), adds_event=False))
                self.add(Goal("deliver_packages", (target,), source=self))
            else:
                self.stop_cycle()
        else:
            self.stop_cycle()

if __name__ == "__main__":
    env = DeliveryWorld()
    courier = Courier("Courier")
    Admin().connect_to([courier], env)
    Admin().start_system()
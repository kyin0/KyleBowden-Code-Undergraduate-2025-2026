from maspy import *

class DeliveryWorld(Environment):
    def __init__(self):
        super().__init__()
        self.package_locations = {"depot": 2}
        self.delivery_locations = ["location1", "location2"]
        self.current_delivery_location = 0

    def pick_up_package(self):
        if self.package_locations["depot"] > 0:
            self.package_locations["depot"] -= 1
            return True
        return False

    def deliver_package(self, location):
        if location in self.delivery_locations:
            return True
        return False

class Courier(Agent):
    def __init__(self, env):
        super().__init__("Courier", env)
        self.add(Belief("delivered_count", (0,)))
        self.add(Belief("at_location", ("depot",)))
        self.add(Goal("deliver_packages", (2,)))

    @pl(gain, Goal("deliver_packages", (Any,)), Belief("at_location", ("depot",)))
    def go_to_delivery_location(self, src, target, current_location):
        next_location = self.env.delivery_locations[self.env.current_delivery_location]
        self.rm(Belief("at_location", (current_location,)))
        self.add(Belief("at_location", (next_location,)))
        self.env.current_delivery_location = (self.env.current_delivery_location + 1) % len(self.env.delivery_locations)

    @pl(gain, Goal("deliver_packages", (Any,)), Belief("at_location", (Any,)))
    def pick_up_package(self, src, target, current_location):
        if self.env.pick_up_package():
            self.add(Goal("travel_to_depot", ()))

    @pl(gain, Goal("travel_to_depot", ()), Belief("at_location", (Any,)))
    def return_to_depot(self, src, current_location):
        self.rm(Belief("at_location", (current_location,)))
        self.add(Belief("at_location", ("depot",)))
        self.add(Goal("deliver_packages", (2,)))

    @pl(gain, Goal("deliver_packages", (Any,)), [Belief("at_location", (Any,)), Belief("delivered_count", (Any,))])
    def deliver_package(self, src, target, current_location, delivered_count):
        if self.env.deliver_package(current_location):
            package_id = f"package_{delivered_count + 1}"
            self.add(Belief("delivered_package", (package_id,)))
            self.rm(Belief("delivered_count", (delivered_count,)))
            new_delivered_count = delivered_count + 1
            self.add(Belief("delivered_count", (new_delivered_count,)))
            if new_delivered_count < 2:
                self.add(Goal("deliver_packages", (2,)))
            else:
                self.stop_cycle()

if __name__ == "__main__":
    env = DeliveryWorld()
    courier = Courier(env)
    Admin().connect_to([courier], env)
    Admin().start_system()
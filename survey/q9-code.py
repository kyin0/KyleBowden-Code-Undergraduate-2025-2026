from maspy import *

class DeliveryEnv(Environment):

    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.package_status = "waiting"
        self.courier_location = "depot"

    def deliver_package(self, agt):
            if self.package_status == "waiting" and self.courier_location == "depot":
                self.package_status = "delivered"
                self.courier_location = "customer"
                return True
            return False
 
class Courier(Agent):
    def __init__(self, env, agent_name=None):
        super().__init__(agent_name)
        self.env = env
        self.add(Belief("package_status", ("waiting",)))
        self.add(Belief("courier_location", ("depot",)))
        self.add(Goal("deliver"))
 
    @pl(gain, Goal("deliver"), Belief("package_status", (Any,)))
    def deliver_package(self, src, package_status):
        if self.env.deliver_package(self):
            self.rm(Belief("package_status", (package_status,)))
            self.add(Belief("package_status", ("delivered",)))
            self.rm(Belief("courier_location", ("depot",)))
            self.add(Belief("courier_location", ("customer",)))
            self.stop_cycle()

if __name__ == "__main__":
    env = DeliveryEnv()
    agent = Courier(env)
    Admin().connect_to([agent], env)
    Admin().start_system()
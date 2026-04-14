from maspy import *

class DoorWorld(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.door_state = "locked"

    def unlock_door(self, agt):
        if self.door_state == "locked":
            self.door_state = "closed"
            return True
        return False

    def open_door(self, agt):
        if self.door_state == "closed":
            self.door_state = "open"
            return True
        return False

class DoorAgent(Agent):
    def __init__(self, env, agent_name=None):
        super().__init__(agent_name)
        self.env = env
        self.add(Belief("has_key", (True,)))
        self.add(Belief("door_state", ("locked",)))
        self.add(Goal("open_door", ()))

    @pl(gain, Goal("open_door", ()), Belief("door_state", ("locked",)), Belief("has_key", (True,)))
    def unlock_and_open_door(self, src):
        if self.env.unlock_door(self):
            self.rm(Belief("door_state", ("locked",)))
            self.add(Belief("door_state", ("closed",)))
            self.add(Goal("open_door", ()))

    @pl(gain, Goal("open_door", ()), Belief("door_state", ("closed",)))
    def open_locked_door(self, src):
        if self.env.open_door(self):
            self.rm(Belief("door_state", ("closed",)))
            self.add(Belief("door_state", ("open",)))
            self.rm(Goal("open_door", ()))
            self.stop_cycle()

if __name__ == "__main__":
    env = DoorWorld()
    agt = DoorAgent(env)
    Admin().connect_to([agt], env)
    Admin().start_system()
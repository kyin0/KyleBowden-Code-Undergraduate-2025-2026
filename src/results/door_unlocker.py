from maspy import *

class DoorWorld(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.door_state = "locked"

    def unlock_door(self):
        if self.door_state == "locked":
            self.door_state = "closed"
            return True
        return False

    def open_door(self):
        if self.door_state == "closed":
            self.door_state = "open"
            return True
        return False

class DoorAgent(Agent):
    def __init__(self, agent_name=None, env=None):
        super().__init__(agent_name)
        self.env = env
        self.add(Belief("has_key", ("True",)))
        self.add(Belief("door_state", ("locked",)))
        self.add(Goal("open_door", ()))

    @pl(gain, Goal("open_door"), Belief("door_state", (Any,)))
    def unlock_and_open(self, src, door_state):
        if self.env.unlock_door():
            self.rm(Belief("door_state", (door_state,)))
            self.add(Belief("door_state", ("closed",)))
            self.add(Goal("open_door", ()))

    @pl(gain, Goal("open_door"), Belief("door_state", (Any,)))
    def open_door_now(self, src, door_state):
        if self.env.open_door():
            self.rm(Belief("door_state", (door_state,)))
            self.add(Belief("door_state", ("open",)))
            self.stop_cycle()

if __name__ == "__main__":
    env = DoorWorld()
    agent = DoorAgent(env=env)
    Admin().connect_to([agent], env)
    Admin().start_system()
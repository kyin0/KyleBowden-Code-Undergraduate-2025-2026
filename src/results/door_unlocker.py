from maspy import *

class DoorWorld(Environment):
    def __init__(self):
        super().__init__()
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
    def __init__(self, env):
        super().__init__("DoorAgent", env)
        self.add(Belief("has_key", ("true",)))
        self.add(Belief("door_state", ("locked",)))
        self.add(Goal("open_door", ()))

    @pl(gain, Goal("open_door"), Belief("door_state", ("locked",)))
    def unlock_door(self, src, door_state):
        if self.env.unlock_door():
            self.rm(Belief("door_state", ("locked",)))
            self.add(Belief("door_state", ("closed",)))

    @pl(gain, Goal("open_door"), Belief("door_state", ("closed",)))
    def open_door(self, src, door_state):
        if self.env.open_door():
            self.rm(Belief("door_state", ("closed",)))
            self.add(Belief("door_state", ("open",)))
            self.stop_cycle()

if __name__ == "__main__":
    env = DoorWorld()
    agent = DoorAgent(env)
    Admin().connect_to([agent], env)
    Admin().start_system()
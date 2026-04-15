from maspy import *

class DoorEnv(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.door_state = "locked"
    
    def unlock_door(self, agt):
        if self.door_state == "locked":
            self.door_state = "unlocked"
            return True
        return False
    
    def lock_door(self, agt):
        if self.door_state == "unlocked":
            self.door_state = "locked"
            return True
        return False

class DoorAgent(Agent):
    def __init__(self, env, agent_name=None):
        super().__init__(agent_name)
        self.env = env
        self.add(Belief("door_state", ("locked",)))
        self.add(Goal("unlock"))
    
    @pl(gain, Goal("unlock"), Belief("door_state", (Any,)))
    def unlock_door(self, src, door_state):
        if self.env.unlock_door(self):
            self.rm(Belief("door_state", (door_state,)))
            self.add(Belief("door_state", ("unlocked",)))
            self.add(Goal("lock"))
    
    @pl(gain, Goal("lock"), Belief("door_state", (Any,)))
    def lock_door(self, src, door_state):
        if self.env.lock_door(self):
            self.rm(Belief("door_state", (door_state,)))
            self.add(Belief("door_state", ("locked",)))
            self.stop_cycle()

if __name__ == "__main__":
    env = DoorEnv()
    agent = DoorAgent(env)
    Admin().connect_to([agent], env)
    Admin().start_system()
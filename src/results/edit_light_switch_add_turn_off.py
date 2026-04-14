from maspy import *

class RoomEnv(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.light_state = "off"
    
    def turn_light_on(self, agt):
        if self.light_state == "off":
            self.light_state = "on"
            return True
        return False
    
    def turn_light_off(self, agt):
        if self.light_state == "on":
            self.light_state = "off"
            return True
        return False

class LightAgent(Agent):
    def __init__(self, env, agent_name=None):
        super().__init__(agent_name)
        self.env = env
        self.add(Belief("light_state", ("off",)))
        self.add(Goal("turn_on"))
    
    @pl(gain, Goal("turn_on"), Belief("light_state", (Any,)))
    def turn_light_on(self, src, light_state):
        if self.env.turn_light_on(self):
            self.rm(Belief("light_state", (light_state,)))
            self.add(Belief("light_state", ("on",)))
            self.add(Goal("turn_off"))
    
    @pl(gain, Goal("turn_off"), Belief("light_state", ("on",)))
    def turn_light_off(self, src, light_state):
        if self.env.turn_light_off(self):
            self.rm(Belief("light_state", (light_state,)))
            self.add(Belief("light_state", ("off",)))
            self.stop_cycle()

if __name__ == "__main__":
    env = RoomEnv()
    agent = LightAgent(env)
    Admin().connect_to([agent], env)
    Admin().start_system()
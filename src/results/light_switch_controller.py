from maspy import *

class RoomEnv(Environment):
    def __init__(self):
        super().__init__()
        self.light_state = "off"

    def turn_light_on(self):
        self.light_state = "on"

class LightAgent(Agent):
    def __init__(self, env):
        super().__init__("LightAgent", env)
        self.add(Belief("light_state", ("off",)))
        self.add(Goal("turn_on"))

    @pl(gain, Goal("turn_on"), Belief("light_state", ("off",)))
    def turn_light_on(self, src, light_state):
        self.env.turn_light_on()
        self.rm(Belief("light_state", ("off",)))
        self.add(Belief("light_state", ("on",)))
        self.stop_cycle()

if __name__ == "__main__":
    env = RoomEnv()
    agent = LightAgent(env)
    Admin().connect_to([agent], env)
    Admin().start_system()
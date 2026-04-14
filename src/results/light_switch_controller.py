from maspy import *

class RoomEnv(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.create(Percept("light_state", ("off",), adds_event=False))

    def turn_light_on(self):
        light = self.get(Percept("light_state", ("off",)))
        if light:
            self.change(light, ("on",))
            return True
        return False

class LightAgent(Agent):
    def __init__(self, agent_name=None, env=None):
        super().__init__(agent_name)
        self.env = env
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
    agent = LightAgent(agent_name="LightAgent", env=env)
    Admin().connect_to([agent], env)
    Admin().start_system()
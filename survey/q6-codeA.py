from maspy import *

class RoomEnv(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.light_state = "off"

    def is_light_on(self):
        return self.light_state == "on"

    def turn_light_on(self, agt):
        if self.light_state == "off":
            self.light_state = "on"
            return True
        return False


class LightAgent(Agent):
    def __init__(self, env, agent_name=None):
        super().__init__(agent_name)
        self.env = env

        self.add(Belief("light_state", (env.light_state,)))
        self.add(Goal("ensure_light_on"))

    def update_light_belief(self, old_state, new_state):
        self.rm(Belief("light_state", (old_state,)))
        self.add(Belief("light_state", (new_state,)))

    @pl(gain, Goal("ensure_light_on"), Belief("light_state", (Any,)))
    def ensure_light_on(self, src, current_state):
        if current_state == "on":
            self.stop_cycle()
            return

        if self.env.turn_light_on(self):
            self.update_light_belief(current_state, "on")
            self.stop_cycle()


if __name__ == "__main__":
    env = RoomEnv()
    agent = LightAgent(env)
    Admin().connect_to([agent], env)
    Admin().start_system()
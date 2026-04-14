from maspy import *

class TrafficEnv(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.light_state = "red"

    def turn_green(self, agt):
        if self.light_state == "red":
            self.light_state = "green"
            return True
        return False

    def turn_yellow(self, agt):
        if self.light_state == "green":
            self.light_state = "yellow"
            return True
        return False

    def turn_red(self, agt):
        if self.light_state == "yellow":
            self.light_state = "red"
            return True
        return False

class TrafficAgent(Agent):
    def __init__(self, env, agent_name=None):
        super().__init__(agent_name)
        self.add(Belief("light_state", ("red",), adds_event=False))
        self.add(Goal("change_light"))

    @pl(gain, Goal("change_light"), Belief("light_state", Any))
    def change_light(self, src, light_state):
        if light_state == "red":
            if self.env.turn_green(self):
                self.rm(Belief("light_state", ("red",), adds_event=False))
                self.add(Belief("light_state", ("green",), adds_event=False))
        elif light_state == "green":
            if self.env.turn_yellow(self):
                self.rm(Belief("light_state", ("green",), adds_event=False))
                self.add(Belief("light_state", ("yellow",), adds_event=False))
        elif light_state == "yellow":
            if self.env.turn_red(self):
                self.rm(Belief("light_state", ("yellow",), adds_event=False))
                self.add(Belief("light_state", ("red",), adds_event=False))
                self.stop_cycle()

if __name__ == "__main__":
    env = TrafficEnv()
    agent = TrafficAgent(env)
    Admin().connect_to([agent], env)
    Admin().start_system()
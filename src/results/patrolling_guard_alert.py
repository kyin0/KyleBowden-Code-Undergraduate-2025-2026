from maspy import *

class PatrolWorld(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.patrol_points = [0, 1, 2, 3, 4]
        self.current_patrol_point = 0
        self.intruder_detected = False

    def move_to_next_patrol_point(self):
        self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
        return self.current_patrol_point

    def detect_intruder(self):
        self.intruder_detected = True

class Guard(Agent):
    def __init__(self, agent_name=None, env=None):
        super().__init__(agent_name)
        self.env = env
        self.add(Belief("patrol_point", (0,)))
        self.add(Belief("alert_sent", ("False",)))
        self.add(Goal("patrol", ()))

    @pl(gain, Goal("patrol"), [Belief("patrol_point", (Any,)), Belief("alert_sent", ("False",))])
    def patrol(self, src, current_patrol_point, alert_sent):
        if self.env.intruder_detected:
            self.rm(Belief("patrol_point", (current_patrol_point,)))
            self.add(Belief("patrol_point", (self.env.current_patrol_point,)))
            self.add(Belief("alert_sent", ("True",)))
            self.stop_cycle()
        else:
            new_point = self.env.move_to_next_patrol_point()
            self.rm(Belief("patrol_point", (current_patrol_point,)))
            self.add(Belief("patrol_point", (new_point,)))

if __name__ == "__main__":
    env = PatrolWorld("PatrolWorld")
    guard = Guard("Guard", env)
    Admin().connect_to([guard], env)
    Admin().start_system()
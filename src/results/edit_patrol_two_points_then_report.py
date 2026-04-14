from maspy import *

class PatrolEnv(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.current_point = 0

    def move_to_point(self, agt, target_point):
        if self.current_point != target_point:
            self.current_point = target_point
            return True
        return False

class GuardAgent(Agent):
    def __init__(self, env, agent_name=None):
        super().__init__(agent_name)
        self.env = env
        self.add(Belief("patrol_point", (0,)))
        self.add(Goal("patrol_to", (1,)))

    @pl(gain, Goal("patrol_to", (Any,)), Belief("patrol_point", (Any,)))
    def patrol_to_point(self, src, target_point, patrol_point):
        if self.env.move_to_point(self, target_point):
            self.rm(Belief("patrol_point", (patrol_point,)))
            self.add(Belief("patrol_point", (target_point,)))
            if target_point == 1:
                self.add(Goal("patrol_to", (2,)))
            elif target_point == 2:
                self.add(Belief("report_state", ("pending",)))
                self.add(Goal("report"))

    @pl(gain, Goal("report"), Belief("report_state", (Any,)))
    def report(self, src, report_state):
        if report_state == "pending":
            self.rm(Belief("report_state", ("pending",)))
            self.add(Belief("report_state", ("sent",)))
            self.stop_cycle()

if __name__ == "__main__":
    env = PatrolEnv()
    agent = GuardAgent(env)
    Admin().connect_to([agent], env)
    Admin().start_system()
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

        self.route = [1, 2]
        self.route_index = 0

        self.add(Belief("position", (0,)))
        self.add(Belief("report_state", ("pending",)))
        self.add(Goal("continue_patrol"))

    def advance_route(self):
        self.route_index += 1

    def current_target(self):
        if self.route_index < len(self.route):
            return self.route[self.route_index]
        return None

    @pl(gain, Goal("continue_patrol"), Belief("position", (Any,)))
    def continue_patrol(self, src, current_position):
        target = self.current_target()

        if target is None:
            self.add(Goal("send_report"))
            return

        if self.env.move_to_point(self, target):
            self.rm(Belief("position", (current_position,)))
            self.add(Belief("position", (target,)))
            self.advance_route()
            self.add(Goal("continue_patrol"))

    @pl(gain, Goal("send_report"), Belief("report_state", (Any,)))
    def send_report(self, src, report_state):
        if report_state == "pending":
            self.rm(Belief("report_state", (report_state,)))
            self.add(Belief("report_state", ("sent",)))
        self.stop_cycle()


if __name__ == "__main__":
    env = PatrolEnv()
    agent = GuardAgent(env)
    Admin().connect_to([agent], env)
    Admin().start_system()

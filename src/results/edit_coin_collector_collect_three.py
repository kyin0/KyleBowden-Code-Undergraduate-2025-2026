from maspy import *

class CoinWorld(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.coins_collected = 0

    def collect_coin(self, agt):
        if self.coins_collected < 3:
            self.coins_collected += 1
            return self.coins_collected
        return None

class Collector(Agent):
    def __init__(self, env, agent_name=None):
        super().__init__(agent_name)
        self.env = env
        self.add(Belief("coin_count", (0,)))
        self.add(Goal("collect", (3,)))

    @pl(gain, Goal("collect", (Any,)), Belief("coin_count", (Any,)))
    def collect_coin(self, src, target, coin_count):
        coin_id = self.env.collect_coin(self)
        if coin_id is not None:
            self.rm(Belief("coin_count", (coin_count,)))
            self.add(Belief("coin_count", (coin_id,)))
            self.add(Belief("has_coin", (coin_id,)))
            if coin_id < target:
                self.add(Goal("collect", (target,)))
            else:
                self.stop_cycle()

if __name__ == "__main__":
    env = CoinWorld()
    agent = Collector(env)
    Admin().connect_to([agent], env)
    Admin().start_system()
from maspy import *

class CoinWorld(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.coins = 3

    def collect_coin(self, agt):
        if self.coins > 0:
            coin_id = self.coins
            self.coins -= 1
            return True, coin_id
        return False, None

class Collector(Agent):
    def __init__(self, env, agt_name=None):
        super().__init__(agt_name)
        self.env = env
        self.add(Belief("coin_count", (0,)))
        self.add(Goal("collect", (3,)))

    @pl(gain, Goal("collect", (3,)), Belief("coin_count", (Any,)))
    def collect_coins(self, src, target, current_count):
        success, coin_id = self.env.collect_coin(self)
        if success:
            new_count = current_count[0] + 1
            self.add(Belief("has_coin", (coin_id,)))
            self.add(Belief("coin_count", (new_count,)))
            if new_count < target[0]:
                self.add(Goal("collect", (target[0],)))

env = CoinWorld()
collector = Collector(env)
Admin().connect_to([collector], env)
Admin().start_system()
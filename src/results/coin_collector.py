from maspy import *

class CoinWorld(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.create(Belief("coin_count", (0,), adds_event=False))

    def collect_coin(self, coin_id):
        current_count = self.get(Belief("coin_count", (Any,))).values[0]
        new_count = current_count + 1
        self.rm(Belief("coin_count", (current_count,), adds_event=False))
        self.add(Belief("coin_count", (new_count,), adds_event=False))
        self.add(Belief("has_coin", (coin_id,), adds_event=False))

class Collector(Agent):
    def __init__(self, agent_name=None):
        super().__init__(agent_name)
        self.add(Goal("collect", (3,), source="self"))
        self.add(Belief("coin_count", (0,), source="self"))

    @pl(gain, Goal("collect", (3,)), Belief("coin_count", (Any,)))
    def collect_coins(self, src, target, coin_count):
        if coin_count < target:
            self.env.collect_coin(coin_id=coin_count + 1)
        else:
            self.stop_cycle()

if __name__ == "__main__":
    env = CoinWorld("CoinWorld")
    collector = Collector("Collector")
    Admin().connect_to([collector], env)
    Admin().start_system()
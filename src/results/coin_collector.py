from maspy import *

class CoinWorld(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.create(Percept("coin", None, "coins", False))
        self.coin_count = 0

    def add_coin(self, coin_id):
        self.create(Percept("coin", coin_id, "coins", True))
        self.coin_count += 1

    def remove_coin(self, coin_id):
        self.rm(Percept("coin", coin_id, "coins"))
        self.coin_count -= 1

class Collector(Agent):
    def __init__(self, agent_name=None):
        super().__init__(agent_name)
        self.add(Belief("coin_count", (0,)))
        self.add(Goal("collect"))

    @pl(gain, Goal("collect"), Belief("coin_count", (Any,)))
    def collect_coin(self, src, coin_count):
        if coin_count < 3:
            coins = self.env.get(Percept("coin", None, "coins"))
            if coins:
                for coin in coins:
                    self.env.rm(coin)
                    self.add(Belief("has_coin", (coin.values[0],)))
                    self.rm(Belief("coin_count"))
                    self.add(Belief("coin_count", (self.env.coin_count + 1,)))
            else:
                self.stop_cycle()
            self.add(Goal("collect"))

if __name__ == "__main__":
    env = CoinWorld("CoinWorld")
    collector = Collector("Collector")
    Admin().connect_to([collector], env)
    Admin().start_system()
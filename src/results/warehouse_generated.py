from maspy import *

class CoinCollector(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name)
        self.coins = 0
        self.add(Goal("collect_coins"))

    @pl(gain, Goal("collect_coins"))
    def collect_coins(self, src):
        # Simulate finding a coin
        self.coins += 1
        self.print(f"Collected a coin! Total coins: {self.coins}")
        if self.coins < 3:
            self.add(Goal("collect_coins"))
        else:
            self.print("Collected enough coins. Stopping.")
            self.stop_cycle()

class CoinEnvironment(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)

    def spawn_coin(self, agt):
        self.print(f"Spawning a coin for {agt.my_name}")
        agt.add(Goal("collect_coins"))

if __name__ == "__main__":
    env = CoinEnvironment("CoinEnv")
    collector = CoinCollector("CoinCollector")

    # Simulate coin spawning
    env.spawn_coin(collector)

    Admin().connect_to([collector], env)
    Admin().start_system()
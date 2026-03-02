from maspy import *

class CoinCollector(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name)
        self.coins_collected = 0
        self.add(Goal("collect_coins"))

    @pl(gain, Goal("collect_coins"))
    def collect_coin(self, src):
        if self.coins_collected < 3:
            self.coins_collected += 1
            self.print(f"Coin collected! Total coins: {self.coins_collected}")
            self.add(Goal("collect_coins"))  # Continue collecting until the goal is met
        else:
            self.print("Goal achieved: Collected 3 coins!")
            self.stop_cycle()

class CoinEnvironment(Environment):
    def __init__(self, agt_name=None):
        super().__init__(agt_name)

    def spawn_coin(self, agt):
        self.create(Percept("coin"))

if __name__ == "__main__":
    collector = CoinCollector()
    env = CoinEnvironment()

    # Simulate coin spawning
    for _ in range(4):  # Spawn more coins than needed to test stopping condition
        env.spawn_coin(collector)

    Admin().connect_to([collector], env)
    Admin().start_system()
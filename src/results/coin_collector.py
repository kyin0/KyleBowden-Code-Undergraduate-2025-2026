from maspy import *

class CoinCollector(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name)
        self.add(Goal("collect_coins"))
        self.coins_collected = 0

    @pl(gain, Goal("collect_coins"))
    def collect_coins(self, src):
        # Simulate finding a coin
        self.coins_collected += 1
        self.print(f"Coin collected! Total coins: {self.coins_collected}")

        # Check if the goal is achieved
        if self.coins_collected >= 3:
            self.print("Goal achieved: Collected 3 coins!")
            self.stop_cycle()
        else:
            # Re-add the goal to continue collecting
            self.add(Goal("collect_coins"))

class CoinEnvironment(Environment):
    def spawn_coin(self, agt):
        self.print(f"Coin spawned for {agt.my_name}")
        agt.add(Goal("collect_coins"))

if __name__ == "__main__":
    env = CoinEnvironment()
    collector = CoinCollector("CoinCollector")

    # Simulate coin spawning
    env.spawn_coin(collector)

    Admin().connect_to([collector], env)
    Admin().start_system()
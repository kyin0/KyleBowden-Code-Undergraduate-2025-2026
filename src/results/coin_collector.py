from maspy import *

class CoinCollector(Environment):
    def __init__(self):
        super().__init__()
        self.coins = 3  # Total coins available in the environment

    def collect_coin(self, agt, coin_id):
        if self.coins > 0:
            self.coins -= 1
            self.print(f"Coin {coin_id} collected by {agt}. Remaining coins: {self.coins}")
            self.create(Percept("coin_collected", {"collector": agt, "coin_id": coin_id}))
        else:
            self.print(f"No coins left for {agt} to collect.")

class CoinAgent(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name)
        self.coins_collected = 0
        self.add(Goal("collect_coins"))

    @pl(gain, Goal("collect_coins"))
    def collect_coins(self, src):
        if self.coins_collected < 3:  # Assuming each agent can collect up to 3 coins
            coin_id = self.coins_collected + 1
            self.print(f"{self.my_name} is trying to collect coin {coin_id}.")
            self.env.collect_coin(self.my_name, coin_id)
            self.coins_collected += 1
        else:
            self.print(f"{self.my_name} has collected all the coins.")
            self.stop_cycle()

if __name__ == "__main__":
    env = CoinCollector()
    agents = [CoinAgent(f"Agent_{i+1}") for i in range(2)]  # Creating two agents

    Admin().connect_to(agents, env)
    Admin().start_system()

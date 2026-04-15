from maspy import *

class StorageEnv(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.box_location = "floor"
    
    def pick_box(self, agt):
        if self.box_location == "floor":
            self.box_location = "carried"
            return True
        return False
    
    def place_box_on_shelf(self, agt):
        if self.box_location == "carried":
            self.box_location = "shelf"
            return True
        return False

class BoxAgent(Agent):
    def __init__(self, env, agent_name=None):
        super().__init__(agent_name)
        self.env = env
        self.add(Belief("box_location", ("floor",)))
        self.add(Goal("store_box"))
    
    @pl(gain, Goal("store_box"), Belief("box_location", (Any,)))
    def pick_box(self, src, box_location):
        if self.env.pick_box(self):
            self.rm(Belief("box_location", (box_location,)))
            self.add(Belief("box_location", ("carried",)))
            self.add(Goal("place_box"))
    
    @pl(gain, Goal("place_box"), Belief("box_location", ("carried",)))
    def place_box(self, src, box_location):
        if self.env.place_box_on_shelf(self):
            self.rm(Belief("box_location", (box_location,)))
            self.add(Belief("box_location", ("shelf",)))
            self.stop_cycle()

if __name__ == "__main__":
    env = StorageEnv()
    agent = BoxAgent(env)
    Admin().connect_to([agent], env)
    Admin().start_system()
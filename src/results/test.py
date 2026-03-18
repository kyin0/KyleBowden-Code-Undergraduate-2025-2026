from maspy import *

class DummyAgent(Agent):
    def __init__(self, name, beliefs, goals):
        super().__init__(name, beliefs, goals, show_exec=False)
        self.add(Belief("Box",(5,10)))
        start_pos = self.get(Belief("my_pos",(Any,Any))).values
        self.add(Belief("start_pos", start_pos))
        
    @pl(gain,Goal("move_boxes"), Belief("Box",(Any,Any)))
    def move_to_pos(self, src, position):
        x, y = position
        my_pos = self.get(Belief("my_pos",(Any,Any)))
        self.move(my_pos.values, (x,y))
        self.print(f"Picking up Box in {x,y}")
        target_pos = self.get(Belief("target_pos",(Any,Any)))
        self.move((x,y), target_pos.values)
        self.print(f"Putting Box in {target_pos.values}")
        self.add(Goal("return_home"))
        
    @pl(gain, Goal("return_home"), Belief("start_pos",(Any,Any)))
    def return_to_start(self, src, start_position):
        current_position = self.get(Belief("my_pos",(Any,Any))).values
        self.move(current_position, start_position)
        self.print("Returning home")
        self.stop_cycle()

    def move(self, my_pos, target_pos):
        self.print(f"Moving from {my_pos} to target {target_pos} position")

if __name__ == "__main__":
    agent_1 = DummyAgent("Dummy_1", [Belief("my_pos",(0,0)),Belief("target_pos",(7,7))], Goal("move_boxes"))

    agent_2 = DummyAgent("Dummy_2", [Belief("my_pos",(3,3)),Belief("target_pos",(3,3))], Goal("move_boxes"))

    agent_3 = DummyAgent("Dummy_3", [Belief("my_pos",(10,10)),Belief("target_pos",(1,1))], Goal("move_boxes"))

    Admin().start_system()
from src.store.database import Database

if __name__ == "__main__":

    db = Database()

    task_specs = {
        "edit_light_switch_add_turn_off": {
            "v": 1,
            "description": """
                - This is an EDIT task, not a from-scratch generation task
                - You are given working MASPY code below
                - Edit the code so that after turning the light on, the agent must also turn it off again
                - Keep the existing structure unless changes are required
                - Environment name must remain: RoomEnv
                - Agent name must remain: LightAgent
                - One LightAgent agent
                - Initial belief must remain: Belief("light_state", ("off",))
                - Initial goal must remain: Goal("turn_on")
                - Required code edits:
                - add a new RoomEnv.turn_light_off(self, agt) method that changes the environment state from "on" to "off"
                - replace the current self.stop_cycle() call in LightAgent.turn_light_on with self.add(Goal("turn_off"))
                - add a new plan triggered by Goal("turn_off") and the current light_state belief
                - after turning the light off, remove the old Belief("light_state", ("on",))
                - after turning the light off, add Belief("light_state", ("off",))
                - Stop only after the light has been turned on and then off
                - Output only the edited MASPY code

                Existing working MASPY code:
                ```python
                from maspy import *

                class RoomEnv(Environment):
                    def __init__(self, env_name=None):
                        super().__init__(env_name)
                        self.light_state = "off"

                    def turn_light_on(self, agt):
                        if self.light_state == "off":
                            self.light_state = "on"
                            return True
                        return False

                class LightAgent(Agent):
                    def __init__(self, env, agent_name=None):
                        super().__init__(agent_name)
                        self.env = env
                        self.add(Belief("light_state", ("off",)))
                        self.add(Goal("turn_on"))

                    @pl(gain, Goal("turn_on"), Belief("light_state", (Any,)))
                    def turn_light_on(self, src, light_state):
                        if self.env.turn_light_on(self):
                            self.rm(Belief("light_state", (light_state,)))
                            self.add(Belief("light_state", ("on",)))
                            self.stop_cycle()

                if __name__ == "__main__":
                    env = RoomEnv()
                    agent = LightAgent(env)
                    Admin().connect_to([agent], env)
                    Admin().start_system()
                ```
            """
        },
        "edit_door_unlock_then_lock": {
            "v": 1,
            "description": """
                - This is an EDIT task, not a from-scratch generation task
                - You are given working MASPY code below
                - Edit the code so the agent must unlock the door and then lock it again
                - Keep the existing structure unless changes are required
                - Environment name must remain: DoorEnv
                - Agent name must remain: DoorAgent
                - One DoorAgent agent
                - Initial belief must remain: Belief("door_state", ("locked",))
                - Initial goal must remain: Goal("unlock")
                - Required code edits:
                - add a new DoorEnv.lock_door(self, agt) method that changes the environment state from "unlocked" to "locked"
                - replace the current self.stop_cycle() call in DoorAgent.unlock_door with self.add(Goal("lock"))
                - add a new plan triggered by Goal("lock") and the current door_state belief
                - after locking the door, remove the old Belief("door_state", ("unlocked",))
                - after locking the door, add Belief("door_state", ("locked",))
                - Stop only after the door has been unlocked and then locked again
                - Output only the edited MASPY code

                Existing working MASPY code:
                ```python
                from maspy import *

                class DoorEnv(Environment):
                    def __init__(self, env_name=None):
                        super().__init__(env_name)
                        self.door_state = "locked"

                    def unlock_door(self, agt):
                        if self.door_state == "locked":
                            self.door_state = "unlocked"
                            return True
                        return False

                class DoorAgent(Agent):
                    def __init__(self, env, agent_name=None):
                        super().__init__(agent_name)
                        self.env = env
                        self.add(Belief("door_state", ("locked",)))
                        self.add(Goal("unlock"))

                    @pl(gain, Goal("unlock"), Belief("door_state", (Any,)))
                    def unlock_door(self, src, door_state):
                        if self.env.unlock_door(self):
                            self.rm(Belief("door_state", (door_state,)))
                            self.add(Belief("door_state", ("unlocked",)))
                            self.stop_cycle()

                if __name__ == "__main__":
                    env = DoorEnv()
                    agent = DoorAgent(env)
                    Admin().connect_to([agent], env)
                    Admin().start_system()
                ```
            """
        },
        "edit_coin_collector_collect_three": {
            "v": 1,
            "description": """
                - This is an EDIT task, not a from-scratch generation task
                - You are given working MASPY code below
                - Edit the code so the agent collects three coins instead of one
                - Keep the existing structure unless changes are required
                - Environment name must remain: CoinWorld
                - Agent name must remain: Collector
                - One Collector agent
                - Initial belief must remain: Belief("coin_count", (0,))
                - Required code edits:
                - change the initial goal from Goal("collect", (1,)) to Goal("collect", (3,))
                - keep using the existing CoinWorld.collect_coin(self, agt) environment method
                - remove the current one-shot stopping behaviour after the first collected coin
                - after updating coin_count, if the count is still below the target, add Goal("collect", (target,)) again
                - keep adding Belief("has_coin", (coin_id,)) for each collected coin
                - Stop only after three coins have been collected
                - Output only the edited MASPY code

                Existing working MASPY code:
                ```python
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
                        self.add(Goal("collect", (1,)))

                    @pl(gain, Goal("collect", (Any,)), Belief("coin_count", (Any,)))
                    def collect_coin(self, src, target, coin_count):
                        coin_id = self.env.collect_coin(self)
                        if coin_id is not None:
                            self.rm(Belief("coin_count", (coin_count,)))
                            self.add(Belief("coin_count", (coin_id,)))
                            self.add(Belief("has_coin", (coin_id,)))
                            self.stop_cycle()

                if __name__ == "__main__":
                    env = CoinWorld()
                    agent = Collector(env)
                    Admin().connect_to([agent], env)
                    Admin().start_system()
                ```
            """
        },
        "edit_box_pickup_then_place": {
            "v": 1,
            "description": """
                - This is an EDIT task, not a from-scratch generation task
                - You are given working MASPY code below
                - Edit the code so the agent picks up the box and then places it on a shelf
                - Keep the existing structure unless changes are required
                - Environment name must remain: StorageEnv
                - Agent name must remain: BoxAgent
                - One BoxAgent agent
                - Initial belief must remain: Belief("box_location", ("floor",))
                - Initial goal must remain: Goal("store_box")
                - Required code edits:
                - add a new StorageEnv.place_box_on_shelf(self, agt) method that changes the environment state from "carried" to "shelf"
                - replace the current self.stop_cycle() call in BoxAgent.pick_box with self.add(Goal("place_box"))
                - add a new plan triggered by Goal("place_box") and the current box_location belief
                - after placing the box, remove the old Belief("box_location", ("carried",))
                - after placing the box, add Belief("box_location", ("shelf",))
                - Stop only after the box has been picked up and then placed on the shelf
                - Output only the edited MASPY code

                Existing working MASPY code:
                ```python
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
                            self.stop_cycle()

                if __name__ == "__main__":
                    env = StorageEnv()
                    agent = BoxAgent(env)
                    Admin().connect_to([agent], env)
                    Admin().start_system()
                ```
            """
        },
        "edit_traffic_light_add_yellow_phase": {
            "v": 1,
            "description": """
                - This is an EDIT task, not a from-scratch generation task
                - You are given working MASPY code below
                - Edit the code so the traffic light completes a full cycle: red to green to yellow to red
                - Keep the existing structure unless changes are required
                - Environment name must remain: TrafficEnv
                - Agent name must remain: TrafficAgent
                - One TrafficAgent agent
                - Initial belief must remain: Belief("light_state", ("red",))
                - Initial goal must remain: Goal("advance")
                - Required code edits:
                - add a new TrafficEnv.turn_yellow(self, agt) method that changes the environment state from "green" to "yellow"
                - add a new TrafficEnv.turn_red(self, agt) method that changes the environment state from "yellow" to "red"
                - replace the current one-step plan body so it no longer stops after reaching green
                - reuse the same Goal("advance") to keep the cycle moving through the remaining states
                - each transition must remove the old Belief("light_state", (...,)) before adding the new one
                - Stop only after the complete cycle red to green to yellow to red is finished
                - Output only the edited MASPY code

                Existing working MASPY code:
                ```python
                from maspy import *

                class TrafficEnv(Environment):
                    def __init__(self, env_name=None):
                        super().__init__(env_name)
                        self.light_state = "red"

                    def turn_green(self, agt):
                        if self.light_state == "red":
                            self.light_state = "green"
                            return True
                        return False

                class TrafficAgent(Agent):
                    def __init__(self, env, agent_name=None):
                        super().__init__(agent_name)
                        self.env = env
                        self.add(Belief("light_state", ("red",)))
                        self.add(Goal("advance"))

                    @pl(gain, Goal("advance"), Belief("light_state", (Any,)))
                    def advance_light(self, src, light_state):
                        if self.env.turn_green(self):
                            self.rm(Belief("light_state", (light_state,)))
                            self.add(Belief("light_state", ("green",)))
                            self.stop_cycle()

                if __name__ == "__main__":
                    env = TrafficEnv()
                    agent = TrafficAgent(env)
                    Admin().connect_to([agent], env)
                    Admin().start_system()
                ```
            """
        },
        "edit_courier_deliver_then_return": {
            "v": 1,
            "description": """
                - This is an EDIT task, not a from-scratch generation task
                - You are given working MASPY code below
                - Edit the code so the courier delivers the package and then returns to the depot
                - Keep the existing structure unless changes are required
                - Environment name must remain: DeliveryEnv
                - Agent name must remain: Courier
                - One Courier agent
                - Initial beliefs must remain: Belief("package_status", ("waiting",)) and Belief("courier_location", ("depot",))
                - Initial goal must remain: Goal("deliver")
                - Required code edits:
                - add a new DeliveryEnv.return_to_depot(self, agt) method that changes the environment location from "customer" to "depot"
                - replace the current self.stop_cycle() call in Courier.deliver_package with self.add(Goal("return_to_depot"))
                - add a new plan triggered by Goal("return_to_depot") and the current courier_location belief
                - after returning, remove the old Belief("courier_location", ("customer",))
                - after returning, add Belief("courier_location", ("depot",))
                - keep Belief("package_status", ("delivered",)) after the return trip
                - Stop only after the package has been delivered and the courier is back at the depot
                - Output only the edited MASPY code

                Existing working MASPY code:
                ```python
                from maspy import *

                class DeliveryEnv(Environment):
                    def __init__(self, env_name=None):
                        super().__init__(env_name)
                        self.package_status = "waiting"
                        self.courier_location = "depot"

                    def deliver_package(self, agt):
                        if self.package_status == "waiting" and self.courier_location == "depot":
                            self.package_status = "delivered"
                            self.courier_location = "customer"
                            return True
                        return False

                class Courier(Agent):
                    def __init__(self, env, agent_name=None):
                        super().__init__(agent_name)
                        self.env = env
                        self.add(Belief("package_status", ("waiting",)))
                        self.add(Belief("courier_location", ("depot",)))
                        self.add(Goal("deliver"))

                    @pl(gain, Goal("deliver"), Belief("package_status", (Any,)))
                    def deliver_package(self, src, package_status):
                        if self.env.deliver_package(self):
                            self.rm(Belief("package_status", (package_status,)))
                            self.add(Belief("package_status", ("delivered",)))
                            self.rm(Belief("courier_location", ("depot",)))
                            self.add(Belief("courier_location", ("customer",)))
                            self.stop_cycle()

                if __name__ == "__main__":
                    env = DeliveryEnv()
                    agent = Courier(env)
                    Admin().connect_to([agent], env)
                    Admin().start_system()
                ```
            """
        },
        "edit_sender_receiver_add_ack": {
            "v": 1,
            "description": """
                - This is an EDIT task, not a from-scratch generation task
                - You are given working MASPY code below
                - Edit the code so the sender waits for an acknowledgement from the receiver before stopping
                - Keep the existing structure unless changes are required
                - Environment name must remain: MessageEnv
                - Agent class names must remain: SenderAgent and ReceiverAgent
                - Use exactly two agents: one sender and one receiver
                - The receiver agent instance name must remain "Receiver" because the sender already targets that name
                - Required code edits:
                - in SenderAgent.send_notice, add Belief("last_notice", (message,)) after the message is sent
                - remove the immediate self.stop_cycle() from SenderAgent.send_notice
                - in ReceiverAgent.receive_notice, keep adding Belief("received_notice", (message,))
                - in ReceiverAgent.receive_notice, add self.send(src, tell, Belief("acknowledged", (message,)))
                - add a new SenderAgent plan triggered by gaining Belief("acknowledged", (Any,)) with context Belief("last_notice", (Any,))
                - in that new sender plan, stop only when the acknowledged message matches the last sent notice
                - Output only the edited MASPY code

                Existing working MASPY code:
                ```python
                from maspy import *

                class MessageEnv(Environment):
                    def __init__(self, env_name=None):
                        super().__init__(env_name)

                class SenderAgent(Agent):
                    def __init__(self, env, agent_name=None):
                        super().__init__(agent_name or "Sender")
                        self.env = env
                        self.add(Goal("send_notice", ("status update",)))

                    @pl(gain, Goal("send_notice", (Any,)))
                    def send_notice(self, src, message):
                        self.send("Receiver", achieve, Goal("receive_notice", (message,)))
                        self.stop_cycle()

                class ReceiverAgent(Agent):
                    def __init__(self, env, agent_name=None):
                        super().__init__(agent_name or "Receiver")
                        self.env = env
                        self.add(Belief("ready", ("yes",)))

                    @pl(gain, Goal("receive_notice", (Any,)), Belief("ready", (Any,)))
                    def receive_notice(self, src, message, ready_state):
                        self.add(Belief("received_notice", (message,)))
                        self.stop_cycle()

                if __name__ == "__main__":
                    env = MessageEnv()
                    sender = SenderAgent(env)
                    receiver = ReceiverAgent(env)
                    Admin().connect_to([sender, receiver], env)
                    Admin().start_system()
                ```
            """
        },
        "edit_patrol_two_points_then_report": {
            "v": 1,
            "description": """
                - This is an EDIT task, not a from-scratch generation task
                - You are given working MASPY code below
                - Edit the code so the guard visits point 1, then point 2, then sends a report
                - Keep the existing structure unless changes are required
                - Environment name must remain: PatrolEnv
                - Agent name must remain: GuardAgent
                - One GuardAgent agent
                - Initial belief must remain: Belief("patrol_point", (0,))
                - Initial goal must remain: Goal("patrol_to", (1,))
                - Required code edits:
                - after the existing move to point 1 succeeds, do not stop
                - after reaching point 1, add Goal("patrol_to", (2,))
                - after reaching point 2, add Belief("report_state", ("pending",))
                - after reaching point 2, add Goal("report")
                - add a new plan triggered by Goal("report") with context Belief("report_state", (Any,))
                - in the report plan, remove Belief("report_state", ("pending",)) and add Belief("report_state", ("sent",))
                - Stop only after point 1 has been visited, point 2 has been visited, and the report has been sent
                - Output only the edited MASPY code

                Existing working MASPY code:
                ```python
                from maspy import *

                class PatrolEnv(Environment):
                    def __init__(self, env_name=None):
                        super().__init__(env_name)
                        self.current_point = 0

                    def move_to_point(self, agt, target_point):
                        if self.current_point != target_point:
                            self.current_point = target_point
                            return True
                        return False

                class GuardAgent(Agent):
                    def __init__(self, env, agent_name=None):
                        super().__init__(agent_name)
                        self.env = env
                        self.add(Belief("patrol_point", (0,)))
                        self.add(Goal("patrol_to", (1,)))

                    @pl(gain, Goal("patrol_to", (Any,)), Belief("patrol_point", (Any,)))
                    def patrol_to_point(self, src, target_point, patrol_point):
                        if self.env.move_to_point(self, target_point):
                            self.rm(Belief("patrol_point", (patrol_point,)))
                            self.add(Belief("patrol_point", (target_point,)))
                            self.stop_cycle()

                if __name__ == "__main__":
                    env = PatrolEnv()
                    agent = GuardAgent(env)
                    Admin().connect_to([agent], env)
                    Admin().start_system()
                ```
            """
        }
    }

    for task_id, task_spec in task_specs.items():
        db.insert_task(task_id, task_spec)

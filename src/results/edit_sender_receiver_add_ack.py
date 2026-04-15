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
        self.add(Belief("last_notice", (message,)))

    @pl(gain, Belief("acknowledged", (Any,)), Belief("last_notice", (Any,)))
    def wait_for_acknowledgment(self, src, acknowledged_message, last_notice):
        if acknowledged_message == last_notice:
            self.stop_cycle()

class ReceiverAgent(Agent):
    def __init__(self, env, agent_name=None):
        super().__init__(agent_name or "Receiver")
        self.env = env
        self.add(Belief("ready", ("yes",)))

    @pl(gain, Goal("receive_notice", (Any,)), Belief("ready", (Any,)))
    def receive_notice(self, src, message, ready_state):
        self.add(Belief("received_notice", (message,)))
        self.send(src, tell, Belief("acknowledged", (message,)))

if __name__ == "__main__":
    env = MessageEnv()
    sender = SenderAgent(env)
    receiver = ReceiverAgent(env)
    Admin().connect_to([sender, receiver], env)
    Admin().start_system()
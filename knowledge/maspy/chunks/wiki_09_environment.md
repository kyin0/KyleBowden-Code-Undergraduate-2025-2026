ID: wiki_09_environment
SOURCE: maspy_wiki
TAGS: Environment
TITLE: Environment

MASPY also gives an abstraction to model the environment.

Here's how you create a parking lot for the manager and driver from before:

Creating an environment

```py
from maspy import *

class Park(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        # This creates in the environment a percept for connected agents to perceive.
        # This specific percept does not create a event when percieved by an agent 
        self.create(Percept("spot",(1,"free"),adds_event=False))

    def park_spot(self, agt, spot_id):
        # The function get gives you percepts from the environment
        # It has various filters to make this search more precise
        spot = self.get(Percept("spot",(spot_id,"free")))
        if spot:
            # This function is used to modify the arguments of an percept.
            self.change(spot,(spot_id,driver))

            # You could also remove the old and create the new
            self.remove(spot)
            self.create(Percept("spot",(spot_id,driver)))

    def leave_spot(self, agt):
        spot = self.get(Percept("spot",("ID",driver)))
        if spot:
            self.change(spot,(spot.values[0],"free"))
```

Allowing agents to interact with an environment

```py
from maspy import *

class Park(Environment):
    def __init__(self, env_name=None):
        super().__init__(env_name)
        self.create(Percept("spot",(1,"free"),adds_event=False))

    def park_spot(self, agt, spot_id):
        spot = self.get(Percept("spot",(spot_id,"free")))
        if spot:
            self.change(spot,(spot_id,driver))

class Driver(Agent)
    @pl(gain,Goal("park",("Park_Name", Any)))
    def park_on_spot(self,src,park_name,spot_id):
        # This agent functions makes the connection with an environment or channel
        # Just give it Channel(Name) or Envrionment(Name) to add it to the agent 
        self.connect_to(Environment(park_name))

        # After the connection, the agent can execute the envrionment plan directly
        self.park_spot(spot_id)
```

Simplest System with Every Class

```py
from maspy import *

class SimpleEnv(Environment):
    def env_act(self, agt, agent2):
        self.print(f"Contact between {agt} and {agent2}")

class SimpleAgent(Agent):
    @pl(gain,Goal("say_hello", Any))
    def send_hello(self,src,agent):
        self.send(agent,tell,Belief("Hello"),"SimpleChannel")

    @pl(gain,Belief("Hello"))
    def recieve_hello(self,src):
        self.print(f"Hello received from {src}")
        self.env_act(src)

if __name__ == "__main__":
    Admin().set_logging(show_exec=True)
    agent1 = SimpleAgent()
    agent2 = SimpleAgent()
    env = SimpleEnv()
    ch = Channel("SimpleChannel")
    Admin().connect_to([agent1,agent2],[env,ch])
    agent1.add(Goal("say_hello",(agent2.my_name,)))
    Admin().start_system()
```

This code will generate the following prints:

```
# Admin #> Starting MASPY Program
# Admin #> Registering Agent SimpleAgent:('SimpleAgent', 1)
# Admin #> Registering Channel:default
Channel:default> Connecting agent SimpleAgent:('SimpleAgent', 1)
# Admin #> Registering Agent SimpleAgent:('SimpleAgent', 2)
Channel:default> Connecting agent SimpleAgent:('SimpleAgent', 2)
# Admin #> Registering Environment SimpleEnv:SimpleEnv
# Admin #> Registering Channel:SimpleChannel
Environment:SimpleEnv> Connecting agent SimpleAgent:('SimpleAgent', 1)
Channel:SimpleChannel> Connecting agent SimpleAgent:('SimpleAgent', 1)
Environment:SimpleEnv> Connecting agent SimpleAgent:('SimpleAgent', 2)
Channel:SimpleChannel> Connecting agent SimpleAgent:('SimpleAgent', 2)
Agent:SimpleAgent_1> Adding Goal say_hello(SimpleAgent_2)[self]
Agent:SimpleAgent_1> New Event: gain,Goal say_hello(SimpleAgent_2)[self]
# Admin #> Starting Agents
Agent:SimpleAgent_1> Running gain : Goal say_hello(typing.Any)[self], [], send_hello() )
Channel:SimpleChannel> SimpleAgent_1 sending tell:Belief Hello(())[SimpleAgent_1] to SimpleAgent_2
Agent:SimpleAgent_2> Adding Belief Hello(())[SimpleAgent_1]
Agent:SimpleAgent_2> New Event: gain,Belief Hello(())[SimpleAgent_1]
Agent:SimpleAgent_2> Running gain : Belief Hello(())[self], [], recieve_hello() )
Agent:SimpleAgent_2> Hello received from SimpleAgent_1
Environment:SimpleEnv> Contact between SimpleAgent_2 and SimpleAgent_1
# Admin #> [Closing System]
# Admin #> Still running agent(s):
SimpleAgent_1 | SimpleAgent_2 |
# Admin #> Ending MASPY Program
```
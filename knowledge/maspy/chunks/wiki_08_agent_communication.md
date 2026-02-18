ID: wiki_08_agent_communication
SOURCE: maspy_wiki
TAGS: Agent communication, communicatioin, agent
TITLE:Communication between Agents

After starting the agents they may use the default channel or be connected to private one.

```py
from maspy import *

class Manager(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name,show_exec=False,show_cycle=False)
        self.add(Belief("spotPrice",rnd.randint(12,20),adds_event=False))

    @pl(gain,Goal("sendPrice"),Belief("spotPrice", Any))
    def send_price(self,src,spot_price):
        # The agent manager sends a goal to the manager via the Parking channel
        self.send(src,achieve,Goal("checkPrice",spot_price),"Parking")

class Driver(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name,show_exec=False,show_cycle=False)
        self.add(Belief("budget",(rnd.randint(6,10),rnd.randint(12,20)),adds_event=False))
        self.add(Goal("park"))
    
    @pl(gain,Goal("park"))
    def ask_price(self,src):
        # The agent driver sends a goal to the manager via the Parking channel
        self.send("Manager", achieve, Goal("sendPrice"),"Parking")

park_ch = Channel("Parking")
manager = Manager()
driver = Driver("Drv")
Admin().connect_to([manager,driver],park_ch)
```

The following are the different directives to send messages between agents.

```py
self.send(<target>, <directive>, <info>, optional[<channel>])

Directives:
tell 		-> Add Belief on target
untell		-> Remove Belief from target
achieve 	-> Add Goal to target
unachieve	-> Remove Goal from target
askOne		-> Ask for Belief from target
askOneReply	-> Ask for Belief from target and wait for Reply
askAll		-> Ask for all similar Beliefs from target
askAllReply	-> Ask for all similar Beliefs from target and wait for Reply
tellHow		-> Add Plan on target
untellHow	-> Remove Plan from target
askHow 		-> Ask for Plan from target
askHowReply	-> Ask for Plan from target and wait for Reply
```
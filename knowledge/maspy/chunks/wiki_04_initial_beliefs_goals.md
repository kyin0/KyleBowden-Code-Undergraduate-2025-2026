ID: wiki_04_initial_beliefs_goals
SOURCE: maspy_wiki
TAGS: agent, belief, goal, init, event
TITLE: Initial Beliefs and Goals

The agent can start with some inital Beliefs or Goals.

```py
from maspy import *

class Driver(Agent):
    def __init__(self, agent_name=None):
        super().__init__(agent_name)
        self.add(Belief("budget",(rnd.randint(6,10),rnd.randint(12,20)),adds_event=False))
        self.add(Goal("park"))

driver = Driver("Drv")
```
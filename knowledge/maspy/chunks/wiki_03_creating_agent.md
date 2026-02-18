ID: wiki_03_creating_agent
SOURCE: maspy_wiki
TAGS: Creating agent, creation
TITLE: Creating a new Agent

To create a new agent, you only need to extend Agent in your class, this adds all of the necessary logic to execute an agent. the following snippet shows how to create an DummyAgent.

To create an instance of any agent, only the Extension is needed.

Technically, this is a MASPY Agent:

```py
Dummy Agent
from maspy import *

class DummyAgent(Agent):
    pass

my_agent = DummyAgent()
named_agent = DummyAgent("Ag")
When the snippet above is run, this is the printed result:
```

```
Starting MASPY Program
# Admin #> Registering Agent DummyAgent:('DummyAgent', 1)
Channel:default> Connecting agent DummyAgent:('DummyAgent', 1)
# Admin #> Registering Agent DummyAgent:('Ag', 1)
Channel:default> Connecting agent DummyAgent:('Ag', 1)
It will execute indeterminably, while doing nothing.
```
ID: wiki_07_running_agents
SOURCE: maspy_wiki
TAGS: Running agents, agents
TITLE: Running the agents

Running the system is simple, given the utilities support we have in place. The Admin module contains a few useful methods to start and manage the system.

# Starting all agents
In case you only need to start all agents, the following snippet is enough.

```py
driver1 = Driver("Drv")
driver2 = Driver("Drv")

Admin().start_system()
```
In this example, both agents have the same name "Drv".

For communication to not be ambiguous, the Admin names them "Drv_1" and "Drv_2".
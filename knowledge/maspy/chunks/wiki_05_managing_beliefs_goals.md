ID: wiki_05_managing_beliefs_goals
SOURCE: maspy_wiki
TAGS: agent, belief, goal, gain, lose, event
TITLE: Managing Beliefs and Goals

Here are some info about Beliefs and Goals being created and removed.

- This function adds a goal to the agent;
- The first field represents the goal key and must always be a string;
- The second field represents arguments of the goal and will always be a tuple;
- Each argument can have any structure, with each position of the tuple representing a different one;
- The third field represents the goal source. It is "self" by default, or another agent.
- adding or removing a goal always creates an event for agent, which will try to find a applicable plan.

```py
agent = DummyAgent("Ag")
agent.add( Goal(Name, Values, Source) )
agent.rm( Goal(Name, Values, Source) )
        
agent.add( Goal("check_house", {"Area": [50,100], "Rooms": 5}, ("Seller",27) ) )
agent.add( Goal("SendInfo", ("Information",["List","of","Information",42]) ) )
agent.rm( Goal("walk", source=("trainer",2)) )
```

- This function adds a belief to the agent;
- The first an second field work exaclty the same way as the goal's
- The third field represents the belief source. It is "self" by default, another agent or an environment.
- The fourth field dictates if the adding or removing the belief will generate a new event.
- By default it does, but sometimes one does not want a group of beliefs to be considerend new events

```py
agent = DummyAgent("Ag")
agent.add( Belief(Name, Values, Source, Adds_Event) )
agent.rm( Belief(Name, Values, Source, Adds_Event) )

agent.add( Belief("Dirt", (("remaining",3),[(2,2),(3,7),(5,1)])) )
agent.rm( Belief("spot",("A",4,"free"),"Parking",False) )
agent.add( Belief("velocity",57) )
```
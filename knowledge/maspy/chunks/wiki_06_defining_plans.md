ID: wiki_06_defining_plans
SOURCE: maspy_wiki
TAGS: Plans, Plan definition
TITLE: Defining plans

To define plans it is also really simple, it only needs the @pl decoration. This decoration must contain the plan change {gain, lose or test}, the data that changed {Belief(s) or Goal(s)} and optionally a context needed to be true to execute the plan {Belief(s) or Goal(s)}.

```py
    change: TypeVar('gain'|'lose'|'test')
    changed_data: Iterable[Belief | Goal] | Belief | Goal
    context: Iterable[Belief | Goal] | Belief | Goal

    @pl(change, changed_data, context)
    def foo(self,src, *changed_data.values, *context.values):
```

Resuming the the driver example, you can implement a plan the following way:

```py
from maspy import *

class Driver(Agent):
    def __init__(self, agent_name=None):
        super().__init__(agent_name)
        self.add(Belief("budget",(rnd.randint(6,10),rnd.randint(12,20)),adds_event=False))
        self.add(Goal("park"))

    # This plan will be executed whenever the agent gains the goal "checkPrice"
    # Every plan needs at least self and src, plus the arguments from the trigger and context
    # for this plan, the context is the belief of a budget with wanted and max prices
    @pl(gain,Goal("checkPrice", Any),Belief("budget",(Any, Any)))
    def check_price(self, src, given_price, budget):
        ...

driver = Driver("Drv")
```
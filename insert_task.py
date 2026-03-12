from src.store.database import Database

if __name__ == "__main__":

    db = Database()

    task_spec = {
        "v": 1,
        "id": "coin-collector-001",
        "title": "Coin Collector",
        "domain": "toy",
        "desc": "A Collector agent gathers coins that appear in the environment until it has 3.",

        "env": {
            "name": "CoinWorld",
            "channel": "local",
            "init": { "coins_spawned": 0 },
            "percepts": [
            { "name": "coin", "args": ["id"], "scope": "agent" },
            { "name": "coin_count", "args": ["n"], "scope": "agent" }
            ],
            "actions": [
            { "name": "pick_coin", "by": "Collector", "pre": ["percept:coin(id)"], "eff": ["belief:+has_coin(id)", "env:-coin(id)"] }
            ],
            "step_limit": 30
        },

        "agents": [
            {
            "type": "Collector",
            "count": 1,
            "role": "Collect 3 coins",
            "init": {
                "beliefs": ["coin_count(0)"],
                "goals": ["collect(3)"]
            },

            "plans": [
                { "on": "gain_percept", "key": "Percept:coin(id)", "do": "collect_seen_coin" },
                { "on": "gain_belief", "key": "Belief:coin_count(3)", "do": "finish" }
            ],

            "behaviors": [
                {
                "name": "collect_seen_coin",
                "steps": [
                    { "op": "act", "p": { "name": "pick_coin", "args": ["id"] } },
                    { "op": "update_belief", "p": { "set": "coin_count(+1)" } }
                ],
                "stop_after": False
                },
                {
                "name": "finish",
                "steps": [
                    { "op": "log", "p": { "msg": "Collected 3 coins. Done." } }
                ],
                "stop_after": True
                }
            ]
            }
        ],

        "term": {
            "mode": "event",
            "step_limit": 30,
            "stop": ["belief:coin_count(3)"]
        },

        "success": [
            { "name": "Collected3", "def": "Collector reaches belief coin_count(3) within 30 steps." }
        ],

        "metrics": {
            "primary": ["steps_to_collect_3"],
            "secondary": ["num_actions", "num_percepts_processed"]
        }
    }

    db.insert_task("coin_collector", task_spec)
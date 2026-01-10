# Quick Start

This guide will get you running negotiations with NegoLog agents in minutes.

## Basic Negotiation

```python
from negmas.outcomes import make_issue
from negmas.preferences import LinearAdditiveUtilityFunction
from negmas.sao import SAOMechanism

from negmas_negolog import BoulwareAgent, ConcederAgent

# Step 1: Define the negotiation domain (issues)
issues = [
    make_issue(values=["low", "medium", "high"], name="price"),
    make_issue(values=["1", "2", "3"], name="quantity"),
    make_issue(values=["fast", "normal", "slow"], name="delivery"),
]

# Step 2: Create utility functions for each party
buyer_ufun = LinearAdditiveUtilityFunction(
    values={
        "price": {"low": 1.0, "medium": 0.5, "high": 0.0},
        "quantity": {"1": 0.0, "2": 0.5, "3": 1.0},
        "delivery": {"fast": 1.0, "normal": 0.5, "slow": 0.0},
    },
    weights={"price": 0.5, "quantity": 0.3, "delivery": 0.2},
)

seller_ufun = LinearAdditiveUtilityFunction(
    values={
        "price": {"low": 0.0, "medium": 0.5, "high": 1.0},
        "quantity": {"1": 1.0, "2": 0.5, "3": 0.0},
        "delivery": {"fast": 0.0, "normal": 0.5, "slow": 1.0},
    },
    weights={"price": 0.5, "quantity": 0.3, "delivery": 0.2},
)

# Step 3: Create the mechanism
mechanism = SAOMechanism(issues=issues, n_steps=100)

# Step 4: Add agents with their preferences
mechanism.add(BoulwareAgent(name="buyer"), preferences=buyer_ufun)
mechanism.add(ConcederAgent(name="seller"), preferences=seller_ufun)

# Step 5: Run the negotiation
state = mechanism.run()

# Step 6: Analyze results
if state.agreement:
    print(f"Agreement reached: {state.agreement}")
    print(f"Buyer utility: {buyer_ufun(state.agreement):.3f}")
    print(f"Seller utility: {seller_ufun(state.agreement):.3f}")
else:
    print("No agreement reached")
```

## Understanding the Results

The `state` object contains rich information about the negotiation:

```python
# Did the negotiation end?
print(f"Ended: {state.ended}")

# Was there an agreement?
print(f"Agreement: {state.agreement}")

# How many steps did it take?
print(f"Steps: {state.step}")

# Did it timeout?
print(f"Timed out: {state.timedout}")

# Relative time (0 to 1)
print(f"Relative time: {state.relative_time}")
```

## Choosing Agents

Different agents have different negotiation strategies:

```python
from negmas_negolog import (
    # Time-based concession
    BoulwareAgent,    # Concedes slowly
    ConcederAgent,    # Concedes quickly  
    LinearAgent,      # Concedes linearly
    
    # Competition winners
    Atlas3Agent,      # ANAC 2015 winner
    HardHeaded,       # ANAC 2011 winner
    
    # Sophisticated strategies
    NiceTitForTat,    # Tit-for-tat with opponent modeling
    SAGAAgent,        # Genetic algorithm-based
)
```

## Next Steps

- See [Available Agents](../user-guide/agents.md) for all 25 agents
- Learn about [Mixing with NegMAS](../user-guide/mixing.md) agents
- Run [Tournaments](../user-guide/tournaments.md) to compare agents

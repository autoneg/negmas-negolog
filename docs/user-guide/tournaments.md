# Running Tournaments

Tournaments allow you to systematically compare agent performance across multiple negotiations.

## Simple Round-Robin Tournament

```python
from negmas.sao import SAOMechanism
from negmas_negolog import (
    BoulwareAgent, ConcederAgent, LinearAgent,
    Atlas3Agent, HardHeaded, NiceTitForTat
)

# Define agents to compare
agents = [
    BoulwareAgent, ConcederAgent, LinearAgent,
    Atlas3Agent, HardHeaded, NiceTitForTat
]

# Run round-robin
results = []
for i, AgentA in enumerate(agents):
    for AgentB in agents[i+1:]:
        mechanism = SAOMechanism(issues=issues, n_steps=100)
        mechanism.add(AgentA(name="A"), preferences=ufun1)
        mechanism.add(AgentB(name="B"), preferences=ufun2)
        
        state = mechanism.run()
        
        results.append({
            "agent_a": AgentA.__name__,
            "agent_b": AgentB.__name__,
            "agreement": state.agreement is not None,
            "utility_a": ufun1(state.agreement) if state.agreement else 0,
            "utility_b": ufun2(state.agreement) if state.agreement else 0,
        })

# Analyze results
import pandas as pd
df = pd.DataFrame(results)
print(df.groupby("agent_a")["utility_a"].mean())
```

## Multiple Domains

For robust comparisons, run tournaments across multiple negotiation domains:

```python
def create_domain(seed):
    """Create a random negotiation domain."""
    import random
    random.seed(seed)
    
    issues = [
        make_issue(values=[f"v{i}" for i in range(random.randint(3, 5))], name=f"issue_{j}")
        for j in range(random.randint(2, 4))
    ]
    
    # Create random utility functions
    # ... (implementation details)
    
    return issues, ufun1, ufun2

# Run tournament across multiple domains
all_results = []
for domain_seed in range(10):
    issues, ufun1, ufun2 = create_domain(domain_seed)
    
    for AgentA in agents:
        for AgentB in agents:
            if AgentA == AgentB:
                continue
                
            mechanism = SAOMechanism(issues=issues, n_steps=100)
            mechanism.add(AgentA(name="A"), preferences=ufun1)
            mechanism.add(AgentB(name="B"), preferences=ufun2)
            
            state = mechanism.run()
            
            all_results.append({
                "domain": domain_seed,
                "agent_a": AgentA.__name__,
                "agent_b": AgentB.__name__,
                "agreement": state.agreement is not None,
                "utility_a": ufun1(state.agreement) if state.agreement else 0,
            })
```

## Parallel Execution

For large tournaments, use parallel execution:

```python
from concurrent.futures import ProcessPoolExecutor
from functools import partial

def run_single_negotiation(args):
    AgentA, AgentB, issues, ufun1, ufun2 = args
    mechanism = SAOMechanism(issues=issues, n_steps=100)
    mechanism.add(AgentA(name="A"), preferences=ufun1)
    mechanism.add(AgentB(name="B"), preferences=ufun2)
    state = mechanism.run()
    return {
        "agent_a": AgentA.__name__,
        "agent_b": AgentB.__name__,
        "agreement": state.agreement is not None,
    }

# Create all matchups
matchups = [
    (AgentA, AgentB, issues, ufun1, ufun2)
    for AgentA in agents
    for AgentB in agents
    if AgentA != AgentB
]

# Run in parallel
with ProcessPoolExecutor() as executor:
    results = list(executor.map(run_single_negotiation, matchups))
```

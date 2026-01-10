# Mixing with NegMAS Agents

One of the key features of negmas-negolog is the ability to run negotiations between NegoLog agents and native NegMAS agents.

## Basic Example

```python
from negmas.sao import SAOMechanism, AspirationNegotiator
from negmas_negolog import BoulwareAgent

# Create mechanism
mechanism = SAOMechanism(issues=issues, n_steps=100)

# Add NegoLog agent
mechanism.add(BoulwareAgent(name="negolog_buyer"), preferences=buyer_ufun)

# Add native NegMAS agent
mechanism.add(AspirationNegotiator(name="negmas_seller"), preferences=seller_ufun)

# Run negotiation
state = mechanism.run()
```

## Available NegMAS Agents

NegMAS provides several built-in negotiators:

- `AspirationNegotiator` - Time-based aspiration strategy
- `ToughNegotiator` - Makes minimal concessions
- `OnlyBestNegotiator` - Only offers/accepts the best outcome
- `NaiveTitForTatNegotiator` - Simple tit-for-tat strategy

## Comparing Strategies

```python
from negmas.sao import SAOMechanism, AspirationNegotiator
from negmas_negolog import BoulwareAgent, ConcederAgent, HardHeaded

# Test different matchups
matchups = [
    (BoulwareAgent, AspirationNegotiator),
    (ConcederAgent, AspirationNegotiator),
    (HardHeaded, AspirationNegotiator),
]

for NegoLogAgent, NegMASAgent in matchups:
    mechanism = SAOMechanism(issues=issues, n_steps=100)
    mechanism.add(NegoLogAgent(name="negolog"), preferences=buyer_ufun)
    mechanism.add(NegMASAgent(name="negmas"), preferences=seller_ufun)
    
    state = mechanism.run()
    
    print(f"{NegoLogAgent.__name__} vs {NegMASAgent.__name__}")
    print(f"  Agreement: {state.agreement is not None}")
    if state.agreement:
        print(f"  Buyer utility: {buyer_ufun(state.agreement):.3f}")
        print(f"  Seller utility: {seller_ufun(state.agreement):.3f}")
```

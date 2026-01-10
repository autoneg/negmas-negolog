# Available Agents

negmas-negolog provides 25 NegoLog agents wrapped for use with NegMAS.

## Time-Based Concession Agents

These agents use time-based strategies to determine their concession rate.

### BoulwareAgent

```python
from negmas_negolog import BoulwareAgent
```

A "tough" negotiator that concedes slowly (sub-linearly over time). Uses Bezier curve-based target utility calculation. Good when you have strong bargaining power.

### ConcederAgent

```python
from negmas_negolog import ConcederAgent
```

A "soft" negotiator that concedes quickly (super-linearly over time). Useful when reaching agreement quickly is more important than maximizing utility.

### LinearAgent

```python
from negmas_negolog import LinearAgent
```

Concedes linearly over time. A balanced approach between Boulware and Conceder strategies.

## ANAC Competition Winners

These agents won or performed well in the Automated Negotiating Agents Competition (ANAC).

### Atlas3Agent

```python
from negmas_negolog import Atlas3Agent
```

**ANAC 2015 Winner.** A sophisticated agent with adaptive strategies.

### HardHeaded

```python
from negmas_negolog import HardHeaded
```

**ANAC 2011 Winner.** Uses frequency-based opponent modeling to estimate opponent preferences.

## Opponent Modeling Agents

These agents build models of their opponents to make better decisions.

### NiceTitForTat

```python
from negmas_negolog import NiceTitForTat
```

Plays tit-for-tat strategy with respect to utility, aiming for the Nash point. Uses Bayesian opponent modeling.

### AgentGG

```python
from negmas_negolog import AgentGG
```

ANAC competition agent with opponent modeling capabilities.

### MICROAgent

```python
from negmas_negolog import MICROAgent
```

ANAC competition agent using opponent modeling for bid selection.

## Other Competition Agents

### AgentKN

```python
from negmas_negolog import AgentKN
```

ANAC competition agent.

### AgentBuyog

```python
from negmas_negolog import AgentBuyog
```

ANAC competition agent.

### AhBuNeAgent

```python
from negmas_negolog import AhBuNeAgent
```

ANAC competition agent.

### Caduceus

```python
from negmas_negolog import Caduceus
```

ANAC competition agent.

### Caduceus2015

```python
from negmas_negolog import Caduceus2015
```

ANAC 2015 competition agent.

### CUHKAgent

```python
from negmas_negolog import CUHKAgent
```

ANAC agent from Chinese University of Hong Kong.

### HybridAgent

```python
from negmas_negolog import HybridAgent
```

Combines multiple negotiation strategies.

### IAMhaggler

```python
from negmas_negolog import IAMhaggler
```

ANAC agent from University of Southampton.

### Kawaii

```python
from negmas_negolog import Kawaii
```

ANAC competition agent.

### LuckyAgent2022

```python
from negmas_negolog import LuckyAgent2022
```

ANAC 2022 competition agent.

### ParsAgent

```python
from negmas_negolog import ParsAgent
```

ANAC agent from Amirkabir University.

### ParsCatAgent

```python
from negmas_negolog import ParsCatAgent
```

ANAC agent from Amirkabir University.

### PonPokoAgent

```python
from negmas_negolog import PonPokoAgent
```

ANAC competition agent.

### RandomDance

```python
from negmas_negolog import RandomDance
```

ANAC competition agent.

### Rubick

```python
from negmas_negolog import Rubick
```

ANAC competition agent.

### SAGAAgent

```python
from negmas_negolog import SAGAAgent
```

Uses genetic algorithm for bid selection.

### YXAgent

```python
from negmas_negolog import YXAgent
```

ANAC competition agent.

## Importing All Agents

You can import all agents at once:

```python
from negmas_negolog import (
    # Time-based
    BoulwareAgent, ConcederAgent, LinearAgent,
    # Competition agents
    MICROAgent, Atlas3Agent, NiceTitForTat, YXAgent,
    ParsCatAgent, PonPokoAgent, AgentGG, SAGAAgent,
    CUHKAgent, AgentKN, Rubick, AhBuNeAgent, ParsAgent,
    RandomDance, AgentBuyog, Kawaii, Caduceus2015,
    Caduceus, HardHeaded, IAMhaggler, LuckyAgent2022,
    HybridAgent,
)
```

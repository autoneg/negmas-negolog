# Available Agents

negmas-negolog provides 25 NegoLog agents wrapped for use with NegMAS. Each agent
implements distinct negotiation strategies developed through academic research and
ANAC (Automated Negotiating Agents Competition) participation.

## Agent Summary Table

| Agent | ANAC Achievement | Strategy Type | Opponent Model |
|-------|------------------|---------------|----------------|
| **ANAC Winners** ||||
| Atlas3Agent | 2015 Winner | Adaptive hybrid | Frequency-based |
| HardHeaded | 2011 Winner | Time-dependent | Frequency-based |
| CUHKAgent | 2012 Winner | Time-dependent | Frequency-based |
| AgentGG | 2019 Winner | Adaptive | Frequency-based |
| Caduceus | 2016 Winner | Nash-seeking | Preference estimation |
| AhBuNeAgent | 2020 Winner | Adaptive | Nash product |
| PonPokoAgent | 2017 Winner | Random multi-pattern | None |
| **ANAC Runner-ups** ||||
| YXAgent | 2016 Runner-up | Threshold-based | Frequency-based |
| ParsCatAgent | 2016 Runner-up | Time-piecewise | Bid history |
| AgentBuyog | 2015 Runner-up | Kalai-seeking | Regression-based |
| Kawaii | 2015 Runner-up | SA search | Acceptance tracking |
| LuckyAgent2022 | 2022 Runner-up | Adaptive | Frequency-based |
| MICROAgent | 2022 Runner-up | Time-dependent | Frequency-based |
| **ANAC Finalists** ||||
| AgentKN | 2017 Finalist | SA search | Statistical |
| Rubick | 2017 Finalist | Boulware + random | Frequency-based |
| ParsAgent | 2015 Finalist | Hybrid | Frequency-based |
| RandomDance | 2015 Finalist | Random weights | Multi-model |
| SAGAAgent | 2019 Finalist | Time-dependent | GA-based |
| **Other Agents** ||||
| NiceTitForTat | ANAC 2012 Nash | Tit-for-tat | Bayesian |
| IAMhaggler | ANAC 2012 Nash | Time-dependent | Bayesian |
| Caduceus2015 | 2015 Entry | Nash product | Frequency-based |
| HybridAgent | Research | Time + Behavior | Implicit |
| **Baseline Agents** ||||
| BoulwareAgent | Baseline | Time-dependent | None |
| ConcederAgent | Baseline | Time-dependent | None |
| LinearAgent | Baseline | Time-dependent | None |

## Time-Based Concession Agents

These agents use time-based strategies to determine their concession rate.

### BoulwareAgent

```python
from negmas_negolog import BoulwareAgent
```

A "tough" negotiator that concedes slowly (sub-linearly over time). Uses Bezier
curve-based target utility calculation with exponent > 1. Good when you have
strong bargaining power or expect long negotiations.

### ConcederAgent

```python
from negmas_negolog import ConcederAgent
```

A "soft" negotiator that concedes quickly (super-linearly over time). Useful when
reaching agreement quickly is more important than maximizing utility, or when
facing deadline pressure.

### LinearAgent

```python
from negmas_negolog import LinearAgent
```

Concedes linearly over time. A balanced approach between Boulware and Conceder
strategies. Good baseline for comparison.

## ANAC Competition Winners

These agents won the Automated Negotiating Agents Competition (ANAC).

### Atlas3Agent (ANAC 2015 Winner)

```python
from negmas_negolog import Atlas3Agent
```

A sophisticated agent using adaptive threshold strategies with frequency-based
opponent modeling. Estimates opponent preferences to find mutually beneficial
outcomes while maintaining strong self-utility.

### HardHeaded (ANAC 2011 Winner)

```python
from negmas_negolog import HardHeaded
```

Uses frequency-based opponent modeling (OMS) to estimate opponent preferences.
Employs Boulware-style concession with Best Bid search strategy, always offering
bids above acceptance threshold.

### CUHKAgent (ANAC 2012 Winner)

```python
from negmas_negolog import CUHKAgent
```

From Chinese University of Hong Kong. Uses adaptive concession with opponent
estimation based on bid frequency analysis. Estimates opponent's minimum and
maximum acceptable utilities.

### AgentGG (ANAC 2019 Winner)

```python
from negmas_negolog import AgentGG
```

Uses frequency-based opponent modeling with time-dependent bidding. Implements
ImpMap for opponent preference estimation and adapts strategy based on
estimated opponent behavior.

### Caduceus (ANAC 2016 Winner)

```python
from negmas_negolog import Caduceus
```

Uses Nash product optimization to find fair outcomes. Estimates opponent
preferences to calculate Nash equilibrium points and generates counter-offers
near these optimal solutions.

### AhBuNeAgent (ANAC 2020 Winner)

```python
from negmas_negolog import AhBuNeAgent
```

Applies adaptive hybrid strategy with Nash product-based bid selection.
Estimates opponent preferences using frequency analysis and adjusts concession
based on opponent behavior.

### PonPokoAgent (ANAC 2017 Winner)

```python
from negmas_negolog import PonPokoAgent
```

Uses randomized multi-strategy approach. Randomly selects one of 5 bidding
patterns at start, making it unpredictable. Patterns include sinusoidal,
linear, and conservative variations.

## ANAC Runner-ups

### YXAgent (ANAC 2016 Runner-up)

```python
from negmas_negolog import YXAgent
```

Frequency-based opponent modeling with threshold bidding. Identifies the
"toughest" opponent and adjusts acceptance based on opponent model evaluation.

### ParsCatAgent (ANAC 2016 Runner-up)

```python
from negmas_negolog import ParsCatAgent
```

From Amirkabir University. Uses complex piecewise time-based thresholds with
10 distinct phases creating oscillating acceptance patterns that are hard
to exploit.

### AgentBuyog (ANAC 2015 Runner-up)

```python
from negmas_negolog import AgentBuyog
```

Estimates opponent concession function using regression. Searches for bids
near the Kalai point (social welfare maximum) while tracking opponent
difficulty.

### Kawaii (ANAC 2015 Runner-up)

```python
from negmas_negolog import Kawaii
```

Uses Simulated Annealing for bid search with time-dependent concession.
Adapts acceptance threshold based on number of accepting opponents in
multilateral scenarios.

### LuckyAgent2022 (ANAC 2022 Runner-up)

```python
from negmas_negolog import LuckyAgent2022
```

Adaptive time-dependent strategy with frequency-based opponent modeling.
Uses conservative early-game and accelerated late-game concession.

### MICROAgent (ANAC 2022 Runner-up)

```python
from negmas_negolog import MICROAgent
```

Time-dependent bidding with frequency-based opponent modeling. Builds
opponent preference model using ImpMap approach similar to AgentGG.

## ANAC Finalists

### AgentKN (ANAC 2017 Finalist)

```python
from negmas_negolog import AgentKN
```

Uses Simulated Annealing to search bids maximizing self-utility while
considering opponent value frequencies. Statistical estimation of opponent's
maximum acceptable utility guides acceptance.

### Rubick (ANAC 2017 Finalist)

```python
from negmas_negolog import Rubick
```

Boulware-style conceder with randomized power parameters and frequency-based
opponent modeling. Maintains list of previously accepted bids for near-deadline
offers.

### ParsAgent (ANAC 2015 Finalist)

```python
from negmas_negolog import ParsAgent
```

From Amirkabir University. Hybrid strategy combining time-dependent, random,
and frequency-based approaches. Searches for mutual preferences between
multiple opponents.

### RandomDance (ANAC 2015 Finalist)

```python
from negmas_negolog import RandomDance
```

Uses multiple weighted opponent models with random selection. Employs three
different weighting strategies (Nash-based, equal, alternating) randomly
chosen each round.

### SAGAAgent (ANAC 2019 Finalist)

```python
from negmas_negolog import SAGAAgent
```

Applies Genetic Algorithm approach with Spearman correlation fitness function.
Uses three-phase probabilistic acceptance strategy with time-dependent target
utility.

## Other Notable Agents

### NiceTitForTat

```python
from negmas_negolog import NiceTitForTat
```

**ANAC 2012 Nash Category Winner.** Plays tit-for-tat strategy with respect
to utility, aiming for the Nash point. Uses Bayesian opponent modeling for
preference estimation.

### IAMhaggler

```python
from negmas_negolog import IAMhaggler
```

**ANAC 2012 Nash Category Winner.** From University of Southampton. Uses
Bayesian learning to estimate opponent model with time-dependent concession
strategy.

### Caduceus2015

```python
from negmas_negolog import Caduceus2015
```

Sub-agent for Caduceus system. Uses Nash product optimization with frequency-
based opponent modeling. Two-phase strategy: hardball early, Nash-seeking late.

### HybridAgent

```python
from negmas_negolog import HybridAgent
```

Research agent combining Time-Based and Behavior-Based strategies using
Bezier curves and opponent move mirroring. Developed for human-robot
negotiation research.

## Strategy Quick Reference

### By Concession Style
- **Hard (Boulware)**: BoulwareAgent, HardHeaded, Rubick
- **Soft (Conceder)**: ConcederAgent
- **Adaptive**: Atlas3Agent, AgentGG, AhBuNeAgent, LuckyAgent2022
- **Unpredictable**: PonPokoAgent, RandomDance, ParsCatAgent

### By Opponent Modeling
- **Frequency-based**: HardHeaded, Atlas3Agent, AgentGG, YXAgent, MICROAgent
- **Bayesian**: NiceTitForTat, IAMhaggler
- **Regression**: AgentBuyog
- **None/Minimal**: BoulwareAgent, ConcederAgent, LinearAgent, PonPokoAgent

### By Search Method
- **Simulated Annealing**: AgentKN, Kawaii
- **Genetic Algorithm**: SAGAAgent
- **Nash Product**: Caduceus, Caduceus2015, AhBuNeAgent
- **Random**: PonPokoAgent, RandomDance

## Importing All Agents

You can import all agents at once:

```python
from negmas_negolog import (
    # Time-based baseline
    BoulwareAgent, ConcederAgent, LinearAgent,
    # ANAC Winners
    Atlas3Agent, HardHeaded, CUHKAgent, AgentGG,
    Caduceus, AhBuNeAgent, PonPokoAgent,
    # ANAC Runner-ups
    YXAgent, ParsCatAgent, AgentBuyog, Kawaii,
    LuckyAgent2022, MICROAgent,
    # ANAC Finalists
    AgentKN, Rubick, ParsAgent, RandomDance, SAGAAgent,
    # Other Notable
    NiceTitForTat, IAMhaggler, Caduceus2015, HybridAgent,
)
```

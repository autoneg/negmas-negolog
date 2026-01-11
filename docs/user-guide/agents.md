# Available Agents

negmas-negolog provides 25 NegoLog agents wrapped for use with NegMAS. Each agent
implements distinct negotiation strategies developed through academic research and
ANAC (Automated Negotiating Agents Competition) participation.

## Complete Agent Reference

| Agent | Achievement | Description | Links |
|-------|-------------|-------------|-------|
| [Atlas3Agent](#atlas3agent-anac-2015-winner) | ANAC 2015 Winner | Adaptive threshold strategy with frequency-based opponent modeling. Estimates opponent preferences to find mutually beneficial outcomes. | [API](../api/wrappers.md#atlas3agent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/atlas3.py) |
| [HardHeaded](#hardheaded-anac-2011-winner) | ANAC 2011 Winner | Frequency-based opponent modeling (OMS) with Boulware-style concession. Best Bid search always offers above acceptance threshold. | [API](../api/wrappers.md#hardheaded) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/hardheaded.py) |
| [CUHKAgent](#cuhkagent-anac-2012-winner) | ANAC 2012 Winner | Adaptive concession with opponent estimation based on bid frequency analysis. Estimates opponent's min/max acceptable utilities. | [API](../api/wrappers.md#cuhkagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/cuhk.py) |
| [AgentGG](#agentgg-anac-2019-winner) | ANAC 2019 Winner | Frequency-based opponent modeling with ImpMap for preference estimation. Adapts strategy based on estimated opponent behavior. | [API](../api/wrappers.md#agentgg) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/agent_gg.py) |
| [Caduceus](#caduceus-anac-2016-winner) | ANAC 2016 Winner | Nash product optimization to find fair outcomes. Estimates opponent preferences for Nash equilibrium calculation. | [API](../api/wrappers.md#caduceus) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/caduceus.py) |
| [AhBuNeAgent](#ahbuneagent-anac-2020-winner) | ANAC 2020 Winner | Adaptive hybrid strategy with Nash product-based bid selection. Adjusts concession based on opponent behavior. | [API](../api/wrappers.md#ahbuneagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/ahbune.py) |
| [PonPokoAgent](#ponpokoagent-anac-2017-winner) | ANAC 2017 Winner | Randomized multi-strategy approach. Randomly selects one of 5 unpredictable bidding patterns at start. | [API](../api/wrappers.md#ponpokoagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/ponpoko.py) |
| [YXAgent](#yxagent-anac-2016-runner-up) | ANAC 2016 Runner-up | Frequency-based opponent modeling with threshold bidding. Identifies "toughest" opponent for acceptance adjustment. | [API](../api/wrappers.md#yxagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/yx.py) |
| [ParsCatAgent](#parscatagent-anac-2016-runner-up) | ANAC 2016 Runner-up | Complex piecewise time-based thresholds with 10 distinct phases creating hard-to-exploit oscillating patterns. | [API](../api/wrappers.md#parscatagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/parscat.py) |
| [AgentBuyog](#agentbuyog-anac-2015-runner-up) | ANAC 2015 Runner-up | Regression-based opponent concession estimation. Searches for bids near Kalai point (social welfare maximum). | [API](../api/wrappers.md#agentbuyog) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/agent_buyog.py) |
| [Kawaii](#kawaii-anac-2015-runner-up) | ANAC 2015 Runner-up | Simulated Annealing bid search with time-dependent concession. Adapts acceptance based on accepting opponents. | [API](../api/wrappers.md#kawaii) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/kawaii.py) |
| [LuckyAgent2022](#luckyagent2022-anac-2022-runner-up) | ANAC 2022 Runner-up | Adaptive time-dependent strategy with conservative early-game and accelerated late-game concession. | [API](../api/wrappers.md#luckyagent2022) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/lucky2022.py) |
| [MICROAgent](#microagent-anac-2022-runner-up) | ANAC 2022 Runner-up | Time-dependent bidding with frequency-based opponent modeling using ImpMap approach. | [API](../api/wrappers.md#microagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/micro.py) |
| [AgentKN](#agentkn-anac-2017-finalist) | ANAC 2017 Finalist | Simulated Annealing search maximizing self-utility while considering opponent value frequencies. | [API](../api/wrappers.md#agentkn) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/agent_kn.py) |
| [Rubick](#rubick-anac-2017-finalist) | ANAC 2017 Finalist | Boulware-style conceder with randomized power parameters and frequency-based opponent modeling. | [API](../api/wrappers.md#rubick) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/rubick.py) |
| [ParsAgent](#parsagent-anac-2015-finalist) | ANAC 2015 Finalist | Hybrid strategy combining time-dependent, random, and frequency-based approaches. | [API](../api/wrappers.md#parsagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/pars.py) |
| [RandomDance](#randomdance-anac-2015-finalist) | ANAC 2015 Finalist | Multiple weighted opponent models with random selection between Nash-based, equal, and alternating strategies. | [API](../api/wrappers.md#randomdance) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/random_dance.py) |
| [SAGAAgent](#sagaagent-anac-2019-finalist) | ANAC 2019 Finalist | Genetic Algorithm approach with Spearman correlation fitness. Three-phase probabilistic acceptance. | [API](../api/wrappers.md#sagaagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/saga.py) |
| [NiceTitForTat](#nicetitfortat) | ANAC 2012 Nash Winner | Tit-for-tat strategy aiming for Nash point with Bayesian opponent modeling for preference estimation. | [API](../api/wrappers.md#nicetitfortat) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/nice_tit_for_tat.py) |
| [IAMhaggler](#iamhaggler) | ANAC 2012 Nash Winner | Bayesian learning for opponent model estimation with time-dependent concession strategy. | [API](../api/wrappers.md#iamhaggler) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/iamhaggler.py) |
| [Caduceus2015](#caduceus2015) | ANAC 2015 Entry | Nash product optimization with two-phase strategy: hardball early, Nash-seeking late. | [API](../api/wrappers.md#caduceus2015) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/caduceus2015.py) |
| [HybridAgent](#hybridagent) | Research Agent | Time-Based and Behavior-Based strategies using Bezier curves and opponent move mirroring. | [API](../api/wrappers.md#hybridagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/hybrid.py) |
| [BoulwareAgent](#boulwareagent) | Baseline | "Tough" negotiator with slow sub-linear concession using Bezier curves (exponent > 1). | [API](../api/wrappers.md#boulwareagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/boulware.py) |
| [ConcederAgent](#concederagent) | Baseline | "Soft" negotiator with fast super-linear concession for quick agreements. | [API](../api/wrappers.md#concederagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/conceder.py) |
| [LinearAgent](#linearagent) | Baseline | Linear concession over time - balanced approach between Boulware and Conceder. | [API](../api/wrappers.md#linearagent) \| [Code](https://github.com/yasserfarouk/negmas-negolog/blob/main/src/negmas_negolog/agents/linear.py) |

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

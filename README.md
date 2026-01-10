# negmas-negolog

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A bridge between [NegMAS](https://github.com/yasserfarouk/negmas) and [NegoLog](https://github.com/negoforta/NegoLog) negotiation frameworks, allowing NegoLog agents to be used as NegMAS SAONegotiator instances.

---

## NegoLog Attribution

This package vendors **[NegoLog](https://github.com/negoforta/NegoLog)** — an integrated Python-based automated negotiation framework.

- **Source Repository:** [https://github.com/negoforta/NegoLog](https://github.com/negoforta/NegoLog)
- **License:** GPL-3.0
- **Copyright:** (C) 2024 Anıl Doğru, M. Onur Keskin & Reyhan Aydoğan

NegoLog was presented at **IJCAI 2024**. If you use this package, please cite the original NegoLog paper:

```bibtex
@inproceedings{ijcai2024p998,
  title     = {NegoLog: An Integrated Python-based Automated Negotiation Framework with Enhanced Assessment Components},
  author    = {Doğru, Anıl and Keskin, Mehmet Onur and Jonker, Catholijn M. and Baarslag, Tim and Aydoğan, Reyhan},
  booktitle = {Proceedings of the Thirty-Third International Joint Conference on
               Artificial Intelligence, {IJCAI-24}},
  publisher = {International Joint Conferences on Artificial Intelligence Organization},
  editor    = {Kate Larson},
  pages     = {8640--8643},
  year      = {2024},
  month     = {8},
  note      = {Demo Track},
  doi       = {10.24963/ijcai.2024/998},
  url       = {https://doi.org/10.24963/ijcai.2024/998},
}
```

---

## Features

- **25 NegoLog agents** available as NegMAS negotiators
- **Seamless integration** with NegMAS mechanisms and tournaments
- **Full compatibility** with NegMAS utility functions and outcome spaces
- **Zero configuration** - agents work out of the box

## Installation

```bash
pip install negmas-negolog
```

Or with uv:

```bash
uv add negmas-negolog
```

### Development Installation

```bash
git clone https://github.com/yasserfarouk/negmas-negolog.git
cd negmas-negolog
uv sync --dev
```

## Quick Start

```python
from negmas.outcomes import make_issue
from negmas.preferences import LinearAdditiveUtilityFunction
from negmas.sao import SAOMechanism

from negmas_negolog import BoulwareAgent, ConcederAgent

# Define negotiation issues
issues = [
    make_issue(values=["low", "medium", "high"], name="price"),
    make_issue(values=["1", "2", "3"], name="quantity"),
]

# Create utility functions
buyer_ufun = LinearAdditiveUtilityFunction(
    values={
        "price": {"low": 1.0, "medium": 0.5, "high": 0.0},
        "quantity": {"1": 0.0, "2": 0.5, "3": 1.0},
    },
    weights={"price": 0.6, "quantity": 0.4},
)

seller_ufun = LinearAdditiveUtilityFunction(
    values={
        "price": {"low": 0.0, "medium": 0.5, "high": 1.0},
        "quantity": {"1": 1.0, "2": 0.5, "3": 0.0},
    },
    weights={"price": 0.6, "quantity": 0.4},
)

# Create mechanism and add agents
mechanism = SAOMechanism(issues=issues, n_steps=100)
mechanism.add(BoulwareAgent(name="buyer"), preferences=buyer_ufun)
mechanism.add(ConcederAgent(name="seller"), preferences=seller_ufun)

# Run negotiation
state = mechanism.run()

if state.agreement:
    print(f"Agreement reached: {state.agreement}")
    print(f"Buyer utility: {buyer_ufun(state.agreement):.3f}")
    print(f"Seller utility: {seller_ufun(state.agreement):.3f}")
else:
    print("No agreement reached")
```

## Available Agents

### Time-Based Concession Agents

| Agent | Description |
|-------|-------------|
| `BoulwareAgent` | Concedes slowly (sub-linearly), using Bezier curve-based target utility |
| `ConcederAgent` | Concedes quickly (super-linearly) |
| `LinearAgent` | Concedes linearly over time |

### ANAC Competition Agents

| Agent | Description |
|-------|-------------|
| `Atlas3Agent` | ANAC 2015 competition winner |
| `HardHeaded` | ANAC 2011 competition winner, uses frequency-based opponent modeling |
| `NiceTitForTat` | Tit-for-tat strategy aiming for Nash point, uses Bayesian opponent modeling |
| `AgentGG` | ANAC competition agent |
| `AgentKN` | ANAC competition agent |
| `AgentBuyog` | ANAC competition agent |
| `AhBuNeAgent` | ANAC competition agent |
| `Caduceus` | ANAC competition agent |
| `Caduceus2015` | ANAC 2015 competition agent |
| `CUHKAgent` | ANAC agent from Chinese University of Hong Kong |
| `HybridAgent` | Combines multiple negotiation strategies |
| `IAMhaggler` | ANAC agent from University of Southampton |
| `Kawaii` | ANAC competition agent |
| `LuckyAgent2022` | ANAC 2022 competition agent |
| `MICROAgent` | ANAC agent using opponent modeling |
| `ParsAgent` | ANAC agent from Amirkabir University |
| `ParsCatAgent` | ANAC agent from Amirkabir University |
| `PonPokoAgent` | ANAC competition agent |
| `RandomDance` | ANAC competition agent |
| `Rubick` | ANAC competition agent |
| `SAGAAgent` | Uses genetic algorithm for bid selection |
| `YXAgent` | ANAC competition agent |

## Mixing with NegMAS Agents

NegoLog agents can negotiate with native NegMAS agents:

```python
from negmas.sao import AspirationNegotiator
from negmas_negolog import BoulwareAgent

mechanism = SAOMechanism(issues=issues, n_steps=100)
mechanism.add(BoulwareAgent(name="negolog_agent"), preferences=ufun1)
mechanism.add(AspirationNegotiator(name="negmas_agent"), preferences=ufun2)

state = mechanism.run()
```

## Running Tournaments

```python
from negmas.sao import SAOMechanism
from negmas_negolog import (
    BoulwareAgent, ConcederAgent, LinearAgent,
    Atlas3Agent, HardHeaded, NiceTitForTat
)

agents = [
    BoulwareAgent, ConcederAgent, LinearAgent,
    Atlas3Agent, HardHeaded, NiceTitForTat
]

# Run round-robin tournament
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
        })
```

## API Reference

### Base Classes

#### `NegologNegotiatorWrapper`

Base class for all NegoLog agent wrappers. Inherits from `negmas.sao.SAONegotiator`.

```python
class NegologNegotiatorWrapper(SAONegotiator):
    def __init__(
        self,
        preferences: BaseUtilityFunction | None = None,
        ufun: BaseUtilityFunction | None = None,
        name: str | None = None,
        session_time: int = 180,  # Session time in seconds for NegoLog agent
        **kwargs,
    ): ...
```

#### `NegologPreferenceAdapter`

Adapts NegMAS utility functions to NegoLog's Preference interface. Used internally by the wrappers.

### Creating Custom Wrappers

To wrap additional NegoLog agents:

```python
from negmas_negolog import NegologNegotiatorWrapper
from agents.MyAgent.MyAgent import MyAgent as NLMyAgent

class MyAgent(NegologNegotiatorWrapper):
    """NegMAS wrapper for NegoLog's MyAgent."""
    negolog_agent_class = NLMyAgent
```

## Development

### Running Tests

```bash
uv run pytest tests/ -v
```

### Running Specific Test Files

```bash
uv run pytest tests/test_wrapper.py -v      # Wrapper functionality tests
uv run pytest tests/test_equivalence.py -v  # Native vs wrapped comparison tests
```

## Architecture

```
negmas-negolog/
├── src/negmas_negolog/
│   ├── __init__.py      # Package exports
│   └── wrapper.py       # Wrapper implementation
├── vendor/NegoLog/      # Vendored NegoLog library
│   ├── agents/          # NegoLog agent implementations
│   └── nenv/            # NegoLog environment
└── tests/
    ├── test_wrapper.py      # Wrapper tests
    └── test_equivalence.py  # Equivalence tests
```

## How It Works

1. **Preference Adaptation**: `NegologPreferenceAdapter` wraps NegMAS utility functions to provide NegoLog's `Preference` interface, allowing NegoLog agents to evaluate bids using NegMAS utility functions.

2. **Bid/Outcome Conversion**: The wrapper handles conversion between NegMAS `Outcome` tuples and NegoLog `Bid` objects.

3. **Time Mapping**: NegMAS relative time (0 to 1) is passed directly to NegoLog agents, which use it for their concession strategies.

4. **Action Translation**: NegoLog `Offer` and `Accept` actions are translated to NegMAS `propose()` returns and `ResponseType` values.

## License

AGPL-3.0 License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [NegMAS](https://github.com/yasserfarouk/negmas) - Negotiation Managed by Situated Agents
- [NegoLog](https://github.com/negoforta/NegoLog) - Negotiation Environment for Learning and Optimization (see [NegoLog Attribution](#negolog-attribution) above)

## Citation

If you use this library in your research, please cite both this wrapper and the original NegoLog paper:

```bibtex
@software{negmas_negolog,
  title = {negmas-negolog: Bridge between NegMAS and NegoLog},
  author = {Mohammad, Yasser},
  year = {2024},
  url = {https://github.com/yasserfarouk/negmas-negolog}
}

@inproceedings{ijcai2024p998,
  title     = {NegoLog: An Integrated Python-based Automated Negotiation Framework with Enhanced Assessment Components},
  author    = {Doğru, Anıl and Keskin, Mehmet Onur and Jonker, Catholijn M. and Baarslag, Tim and Aydoğan, Reyhan},
  booktitle = {Proceedings of the Thirty-Third International Joint Conference on
               Artificial Intelligence, {IJCAI-24}},
  publisher = {International Joint Conferences on Artificial Intelligence Organization},
  editor    = {Kate Larson},
  pages     = {8640--8643},
  year      = {2024},
  month     = {8},
  note      = {Demo Track},
  doi       = {10.24963/ijcai.2024/998},
  url       = {https://doi.org/10.24963/ijcai.2024/998},
}
```

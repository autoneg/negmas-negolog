# negmas-negolog

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/negmas-negolog.svg)](https://pypi.python.org/pypi/negmas-negolog)
[![PyPI - Version](https://img.shields.io/pypi/v/negmas-negolog.svg)](https://pypi.python.org/pypi/negmas-negolog)
[![PyPI - Status](https://img.shields.io/pypi/status/negmas-negolog.svg)](https://pypi.python.org/pypi/negmas-negolog)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/negmas-negolog.svg)](https://pypi.python.org/pypi/negmas-negolog)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Tests](https://github.com/autoneg/negmas-negolog/actions/workflows/test.yml/badge.svg)](https://github.com/autoneg/negmas-negolog/actions/workflows/test.yml)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://autoneg.github.io/negmas-negolog/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A bridge between [NegMAS](https://github.com/yasserfarouk/negmas) and [NegoLog](https://github.com/aniltrue/NegoLog) negotiation frameworks, allowing NegoLog agents to be used as NegMAS SAONegotiator instances.

**[Documentation](https://autoneg.github.io/negmas-negolog/)** | **[API Reference](https://autoneg.github.io/negmas-negolog/api/wrappers/)** | **[Available Agents](https://autoneg.github.io/negmas-negolog/user-guide/agents/)**

---

## NegoLog Attribution

This package vendors **[NegoLog](https://github.com/aniltrue/NegoLog)** — an integrated Python-based automated negotiation framework.

- **Source Repository:** [https://github.com/aniltrue/NegoLog](https://github.com/aniltrue/NegoLog)
- **License:** GPL-3.0
- **Copyright:** (C) 2024 Anıl Doğru, M. Onur Keskin & Reyhan Aydoğan

NegoLog was presented at **IJCAI 2024**. If you use this package, please cite the original NegoLog paper as well as NegMAS (see [Citation](#citation)):

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

- **26 NegoLog agents** available as NegMAS negotiators
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

The following table lists all 26 available agents with their ANAC competition results and references.

> **Note:** Agent descriptions were AI-generated based on the referenced papers and source code analysis.

| Agent | Competition | Algorithm Summary | Reference |
|-------|-------------|-------------------|-----------|
| `Atlas3Agent` | ANAC 2015 Winner | Utility-based bid search with frequency-based opponent modeling and evolutionary stable strategy concession | [Mori & Ito 2017](https://doi.org/10.1007/978-3-319-51563-2_11) |
| `HardHeaded` | ANAC 2011 Winner | Hardheaded concession with frequency-based opponent preference learning | [van Krimpen et al. 2013](https://doi.org/10.1007/978-3-642-30737-9_17) |
| `CUHKAgent` | ANAC 2012 Winner | Adaptive negotiation strategy for bilateral multi-item negotiations | [Hao & Leung 2014](https://doi.org/10.1007/978-4-431-54758-7_11) |
| `Caduceus` | ANAC 2016 Winner | Portfolio/mixture of experts combining multiple negotiation agents | [Güneş et al. 2017](https://doi.org/10.1007/978-3-319-69131-2_27) |
| `PonPokoAgent` | ANAC 2017 Winner | Multiple random bidding strategies to prevent opponent prediction | [Aydoğan et al. 2021](https://link.springer.com/chapter/10.1007/978-981-16-0471-3_7) |
| `AgentGG` | ANAC 2019 Winner | Frequentist opponent model with importance-based bid selection | [Aydoğan et al. 2020](https://doi.org/10.1007/978-3-030-66412-1_23) |
| `AhBuNeAgent` | ANAC 2020 Winner | Heuristic bidding with Importance Map opponent model | [Yıldırım et al. 2023](https://doi.org/10.1007/978-981-99-0561-4_6) |
| `AgentBuyog` | ANAC 2015 Runner-up | Opponent concession function estimation | [Fujita et al. 2017](https://doi.org/10.1007/978-3-319-51563-2_9) |
| `Kawaii` | ANAC 2015 Runner-up | Time-based concession strategy | [Baarslag et al. 2015](https://doi.org/10.1609/aimag.v36i4.2609) |
| `ParsCatAgent` | ANAC 2016 Runner-up | Time-dependent bidding with adaptive thresholds | [Aydoğan et al. 2021](https://link.springer.com/chapter/10.1007/978-981-16-0471-3_7) |
| `YXAgent` | ANAC 2016 Runner-up | Frequency-based opponent modeling | [Aydoğan et al. 2021](https://link.springer.com/chapter/10.1007/978-981-16-0471-3_7) |
| `LuckyAgent2022` | ANAC 2022 Runner-up | BOA components with stop-learning multi-armed bandit mechanism | [Ebrahimnezhad & Nassiri-Mofakham 2022](https://doi.org/10.1109/IKT57960.2022.10039035) |
| `MICROAgent` | ANAC 2022 Runner-up | Concedes only when opponent concedes | [de Jonge 2022](https://www.ijcai.org/proceedings/2022/32) |
| `IAMhaggler` | ANAC 2012 Nash Winner | Gaussian Process prediction for opponent concession | [Williams et al. 2012](https://doi.org/10.1007/978-3-642-24696-8_10) |
| `AgentKN` | ANAC 2017 Nash Finalist | Simulated Annealing bid search with frequency-based scoring | [Aydoğan et al. 2021](https://link.springer.com/chapter/10.1007/978-981-16-0471-3_7) |
| `ParsAgent` | ANAC 2015 Finalist | Hybrid time-dependent, random and frequency-based strategy | [Khosravimehr & Nassiri-Mofakham 2017](https://doi.org/10.1007/978-3-319-51563-2_12) |
| `RandomDance` | ANAC 2015 Finalist | Weighted function opponent modeling with random selection | [Kakimoto & Fujita 2017](https://doi.org/10.1007/978-3-319-51563-2_13) |
| `Rubick` | ANAC 2017 Finalist | Time-based conceder with frequency-based opponent model | [Aydoğan et al. 2021](https://link.springer.com/chapter/10.1007/978-981-16-0471-3_7) |
| `SAGAAgent` | ANAC 2019 Finalist | Genetic Algorithm for self-preference estimation | [Aydoğan et al. 2020](https://doi.org/10.1007/978-3-030-66412-1_23) |
| `NiceTitForTat` | — | Tit-for-tat with Bayesian opponent model aiming for Nash point | [Baarslag et al. 2013](https://link.springer.com/chapter/10.1007/978-3-642-30737-9_14) |
| `BoulwareAgent` | — | Time-based concession (slow, sub-linear) using Bezier curves | [Faratin et al. 1998](https://doi.org/10.1016/S0921-8890(98)00026-0) |
| `ConcederAgent` | — | Time-based concession (fast, super-linear) | [Faratin et al. 1998](https://doi.org/10.1016/S0921-8890(98)00026-0) |
| `LinearAgent` | — | Time-based concession (linear) | [Faratin et al. 1998](https://doi.org/10.1016/S0921-8890(98)00026-0) |
| `HybridAgent` | — | Combines Time-Based and Behavior-Based strategies | [Keskin et al. 2021](https://dl.acm.org/doi/10.5555/3463952.3464182) |
| `HybridAgentWithOppModel` | — | Hybrid Agent extended with opponent modeling | [Yesevi et al. 2023](https://doi.org/10.1007/978-3-031-21203-1_23) |
| `Caduceus2015` | — | Sub-agent for Caduceus portfolio | [Güneş et al. 2017](https://doi.org/10.1007/978-3-319-69131-2_27) |

## Using the NegMAS Registry

All NegoLog agents are automatically registered in the NegMAS negotiator registry when you import the package. This allows you to discover and instantiate agents dynamically:

```python
import negmas_negolog  # Triggers auto-registration
from negmas import negotiator_registry

# Query all negolog agents
negolog_agents = negotiator_registry.query_by_tag("negolog")
print(f"Found {len(negolog_agents)} NegoLog agents")

# Query by ANAC competition year
anac2015_agents = negotiator_registry.query_by_tag("anac-2015")

# Query learning agents
learning_agents = negotiator_registry.query_by_tag("learning")

# Get a specific agent class by name
AgentClass = negotiator_registry.get("Atlas3Agent").type
agent = AgentClass(name="my_atlas3")

# Combined queries
from negmas.registry import query
results = query(negotiator_registry, tags=["negolog", "frequency"], bilateral_only=True)
```

### Registry Tags

Each agent is tagged with relevant metadata:
- `negolog` - All agents from this package
- `sao`, `propose`, `respond` - Negotiation capabilities
- `anac`, `anac-YYYY` - ANAC competition participation
- `time-based`, `learning`, `frequency`, `bayesian`, `tit-for-tat` - Strategy types

### Naming Convention

To avoid conflicts with Genius agents that share the same name, some agents are registered with an "NL" prefix:
- Genius has `AgentGG`, negmas-negolog registers `NLAgentGG`
- Genius has `HardHeaded`, negmas-negolog registers `NLHardHeaded`

Agents unique to NegoLog keep their original names (e.g., `Atlas3Agent`, `BoulwareAgent`).

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

### Behavior Comparison

The project includes a comprehensive behavior comparison script that tests all 25 agents in both native NegoLog and wrapped NegMAS environments. This helps verify that wrapped agents behave equivalently to their native counterparts.

```bash
# Run the behavior comparison
uv run python scripts/compare_behavior.py
```

The script generates reports in the `reports/` directory:

- `behavior_comparison_report.md` - Human-readable Markdown report
- `behavior_comparison_report.json` - Machine-readable JSON data

The comparison tests each agent against a Boulware opponent and measures:

- **Agreement consistency** - Whether both environments reach the same agreement outcome
- **Round count similarity** - How close the negotiation lengths are
- **Utility equivalence** - Whether final utilities match when both agree
- **First offer similarity** - Whether agents start with the same initial offer

See the [latest comparison report](reports/behavior_comparison_report.md) for current results.

## Architecture

```
negmas-negolog/
├── src/negmas_negolog/
│   ├── __init__.py      # Package exports
│   ├── common.py        # Base classes (NegologNegotiatorWrapper, NegologPreferenceAdapter)
│   └── agents/          # Individual agent wrapper modules
│       ├── atlas3.py
│       ├── boulware.py
│       ├── conceder.py
│       └── ...          # 25 agent wrappers total
├── vendor/NegoLog/      # Vendored NegoLog library
│   ├── agents/          # NegoLog agent implementations
│   └── nenv/            # NegoLog environment
├── docs/                # Documentation source
├── scripts/
│   └── compare_behavior.py  # Behavior comparison script
├── reports/             # Generated comparison reports
│   ├── behavior_comparison_report.md
│   └── behavior_comparison_report.json
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
- [NegoLog](https://github.com/aniltrue/NegoLog) - Negotiation Environment for Learning and Optimization (see [NegoLog Attribution](#negolog-attribution) above)

## Citation

If you use this library in your research, please cite this wrapper, NegMAS, and the original NegoLog paper:

```bibtex
@software{negmas_negolog,
  title = {negmas-negolog: Bridge between NegMAS and NegoLog},
  author = {Mohammad, Yasser},
  year = {2024},
  url = {https://github.com/yasserfarouk/negmas-negolog}
}

@inproceedings{mohammad2018negmas,
  title     = {NegMAS: A Platform for Situated Negotiations},
  author    = {Mohammad, Yasser and Greenwald, Amy and Nakadai, Shinji},
  booktitle = {ACAN Workshop at IJCAI},
  year      = {2018},
  url       = {https://github.com/yasserfarouk/negmas}
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

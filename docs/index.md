# negmas-negolog

A bridge between [NegMAS](https://github.com/yasserfarouk/negmas) and [NegoLog](https://github.com/aniltrue/NegoLog) negotiation frameworks.

!!! warning "NegoLog Attribution"
    This package vendors **[NegoLog](https://github.com/aniltrue/NegoLog)** — an integrated Python-based automated negotiation framework.

    - **Source Repository:** [https://github.com/aniltrue/NegoLog](https://github.com/aniltrue/NegoLog)
    - **License:** GPL-3.0
    - **Copyright:** (C) 2024 Anıl Doğru, M. Onur Keskin & Reyhan Aydoğan

    NegoLog was presented at **IJCAI 2024**. If you use this package, please cite the original NegoLog paper as well as NegMAS:

    ```bibtex
    @inproceedings{mohammad2018negmas,
      title     = {NegMAS: A Platform for Situated Negotiations},
      author    = {Mohammad, Yasser and Greenwald, Amy and Nakadai, Shinji},
      booktitle = {ACAN Workshop at IJCAI},
      year      = {2018},
      url       = {https://github.com/yasserfarouk/negmas}
    }

    @inproceedings{ijcai2024p998,
      title     = {NegoLog: An Integrated Python-based Automated Negotiation
                   Framework with Enhanced Assessment Components},
      author    = {Doğru, Anıl and Keskin, Mehmet Onur and Jonker, Catholijn M.
                   and Baarslag, Tim and Aydoğan, Reyhan},
      booktitle = {Proceedings of the Thirty-Third International Joint Conference
                   on Artificial Intelligence, {IJCAI-24}},
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

## Overview

**negmas-negolog** allows you to use NegoLog negotiating agents within the NegMAS framework as `SAONegotiator` instances. This enables:

- Running NegoLog agents in NegMAS mechanisms
- Mixing NegoLog agents with native NegMAS agents
- Using NegoLog agents in NegMAS tournaments
- Leveraging NegMAS's rich analysis and visualization tools

## Features

- **25 NegoLog agents** available as NegMAS negotiators (see [Available Agents](user-guide/agents.md))
- **Seamless integration** with NegMAS mechanisms and tournaments
- **Full compatibility** with NegMAS utility functions and outcome spaces
- **Zero configuration** - agents work out of the box

## Quick Example

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

# Create mechanism and run negotiation
mechanism = SAOMechanism(issues=issues, n_steps=100)
mechanism.add(BoulwareAgent(name="buyer"), preferences=buyer_ufun)
mechanism.add(ConcederAgent(name="seller"), preferences=seller_ufun)

state = mechanism.run()

if state.agreement:
    print(f"Agreement: {state.agreement}")
```

## License

This project is licensed under the AGPL-3.0 License.

# Base Classes

## NegologNegotiatorWrapper

::: negmas_negolog.NegologNegotiatorWrapper

The base class for all NegoLog agent wrappers. Inherits from `negmas.sao.SAONegotiator`.

### Usage

To create a custom wrapper for a NegoLog agent:

```python
from negmas_negolog import NegologNegotiatorWrapper

class MyCustomAgent(NegologNegotiatorWrapper):
    """Wrapper for a custom NegoLog agent."""
    negolog_agent_class = MyNegoLogAgent
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `preferences` | `BaseUtilityFunction` | `None` | NegMAS preferences/utility function |
| `ufun` | `BaseUtilityFunction` | `None` | Utility function (overrides preferences) |
| `name` | `str` | `None` | Negotiator name |
| `session_time` | `int` | `180` | Session time in seconds for NegoLog agent |

### Key Methods

#### `propose(state, dest=None)`

Generate a proposal using the wrapped NegoLog agent.

**Parameters:**
- `state`: Current `SAOState`
- `dest`: Destination negotiator ID (optional)

**Returns:** `Outcome` tuple or `None`

#### `respond(state, source=None)`

Respond to an offer using the wrapped NegoLog agent.

**Parameters:**
- `state`: Current `SAOState` (access offer via `state.current_offer`)
- `source`: ID of negotiator who made the offer

**Returns:** `ResponseType` (ACCEPT_OFFER or REJECT_OFFER)

## NegologPreferenceAdapter

::: negmas_negolog.NegologPreferenceAdapter

Adapts NegMAS utility functions to NegoLog's `Preference` interface. Used internally by the wrappers.

### How It Works

1. Takes a NegMAS `BaseUtilityFunction`
2. Creates NegoLog `Issue` objects from the NegMAS outcome space
3. Evaluates bids using the NegMAS utility function
4. Provides issue/value weights for opponent models

This adapter allows NegoLog agents to use NegMAS utility functions transparently, without requiring JSON preference files.

# Architecture

## Overview

negmas-negolog bridges two negotiation frameworks:

```
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│     NegMAS      │ ←── │  negmas-negolog     │ ──→ │    NegoLog      │
│   Framework     │     │     Wrappers        │     │    Agents       │
└─────────────────┘     └─────────────────────┘     └─────────────────┘
```

## Component Diagram

```
src/negmas_negolog/
├── __init__.py          # Package exports
└── wrapper.py           # Core implementation
    ├── NegologPreferenceAdapter  # Adapts NegMAS ufuns to NegoLog
    ├── NegologNegotiatorWrapper  # Base wrapper class
    └── 25 concrete wrappers      # One per NegoLog agent

vendor/NegoLog/          # Vendored NegoLog library
├── agents/              # NegoLog agent implementations
│   ├── boulware/
│   ├── conceder/
│   └── ...
└── nenv/                # NegoLog environment
    ├── Preference.py
    ├── Bid.py
    └── ...
```

## Data Flow

### Negotiation Flow

```
1. NegMAS calls wrapper.propose(state)
   └── wrapper converts time → relative_time
   └── wrapper calls negolog_agent.act(t)
   └── NegoLog returns Offer(bid)
   └── wrapper converts bid → NegMAS Outcome
   └── returns Outcome to NegMAS

2. NegMAS calls wrapper.respond(state)
   └── wrapper gets offer from state.current_offer
   └── wrapper converts Outcome → NegoLog Bid
   └── wrapper calls negolog_agent.receive_bid(bid, t)
   └── wrapper calls negolog_agent.act(t)
   └── NegoLog returns Accept or Offer
   └── wrapper returns ResponseType to NegMAS
```

### Preference Adaptation

```
NegMAS LinearAdditiveUtilityFunction
    │
    ▼
NegologPreferenceAdapter
    ├── Converts NegMAS issues → NegoLog Issues
    ├── Extracts weights and value functions
    └── Implements get_utility(bid) using NegMAS ufun
    │
    ▼
NegoLog Agent can use preference.get_utility(bid)
```

## Key Design Decisions

### 1. Vendored NegoLog

NegoLog is vendored (included) rather than installed as a dependency because:
- NegoLog is not on PyPI
- We need to patch some bugs in NegoLog
- Ensures version compatibility

### 2. Monkey-Patching EstimatedPreference

NegoLog's `EstimatedPreference` expects preferences loaded from JSON files. We patch `__init__` to handle programmatically-created preferences (from NegMAS ufuns).

### 3. No N Prefix on Wrapper Names

Wrapper classes use the same names as their NegoLog counterparts (e.g., `BoulwareAgent` not `NBoulwareAgent`) for simplicity. The NegoLog originals are aliased with `_NL` prefix internally.

### 4. Session Time Default

The default `session_time=180` (3 minutes) matches NegoLog's default. This affects time-based strategies but NegMAS's `relative_time` (0 to 1) is used directly.

## Bug Fixes in Vendored NegoLog

Several bugs were fixed in the vendored NegoLog:

1. **EstimatedPreference** - Handle preferences without JSON file paths
2. **Caduceus2015/UtilFunctions.py** - Fix division by zero in `normalize()`
3. **IAMhaggler** - Fix uninitialized `means` and `variances` arrays

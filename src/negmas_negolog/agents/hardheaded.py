"""HardHeaded wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.HardHeaded.KLH import HardHeaded as _NLHardHeaded


class HardHeaded(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's HardHeaded agent.

    **ANAC 2011 Winner** (Individual Utility category).

    As the name implies, HardHeaded (developed by Thijs van Krimpen) is an
    aggressive negotiator that maintains high demands throughout most of the
    negotiation and only concedes near the deadline.

    **Offering Strategy:**
        - Uses a monotonic concession function that generates bids in decreasing
          utility order
        - Cycles through the same range of high-utility bids for most of the
          negotiation
        - Resets to a random bid after reaching the dynamic concession limit
        - Selects bids that maximize estimated opponent utility among equivalent
          bids for itself

    **Acceptance Strategy:**
        - Accepts if opponent's offer exceeds the lowest utility offered so far
        - Accepts if opponent's offer is better than the next planned offer
        - Very conservative early acceptance thresholds

    **Opponent Modeling:**
        Frequency-based learning approach:
        - Tracks unchanged issues between consecutive opponent bids to estimate
          issue weights
        - Counts value frequencies to estimate value utilities
        - Uses learned model to select bids favorable to opponent among
          equivalent options

    References:
        .. [Krimpen2013] van Krimpen, T., Looije, D., Hajizadeh, S. (2013).
           HardHeaded. In: Complex Automated Negotiations: Theories, Models,
           and Software Competitions. Studies in Computational Intelligence,
           vol 435. Springer, Berlin, Heidelberg.

    See Also:
        Paper: https://doi.org/10.1007/978-3-642-30737-9_17

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLHardHeaded

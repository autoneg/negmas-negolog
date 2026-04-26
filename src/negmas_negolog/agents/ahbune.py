"""AhBuNeAgent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.AhBuNeAgent.AhBuNeAgent import AhBuNeAgent as _NLAhBuNeAgent


class AhBuNeAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's AhBuNeAgent.

    **ANAC 2020 Winner** (Individual Utility category).

    AhBuNeAgent (developed by Ahmet Burak Yildirim) uses similarity maps
    and linear ordering to estimate preferences and make strategic decisions
    about preference elicitation vs. utility maximization.

    **Offering Strategy:**
        - Uses similarity maps to find bids compatible with estimated preferences
        - Time-based concession with utility lower bound that decreases over time
        - Early phase (t < 0.015): explores bids to gather preference information
        - Takes estimated opponent preferences into account when selecting offers
        - Near deadline: considers opponent's elicited bids as candidates

    **Acceptance Strategy:**
        - Accepts if bid has high similarity (>= 0.9) to best known outcomes
        - Uses opponent model to validate bids as "compromised" (acceptable
          to opponent)
        - Near deadline: relaxes acceptance threshold by max compromise amount

    **Opponent Modeling:**
        Similarity Map approach:
        - Tracks opponent's bidding history to build linear ordering
        - Estimates issue importance from bid content analysis
        - Identifies "forbidden" (worst) and "available" (best) values
        - Determines if bids are "compromised" (likely acceptable to opponent)

    References:
        .. [Yildirim2023] Yildirim, A.B., Sunman, N., Aydogan, R. (2023).
           AhBuNe Agent: Winner of the Eleventh International Automated
           Negotiating Agent Competition (ANAC 2020). In: Recent Advances
           in Agent-Based Negotiation. Studies in Computational Intelligence,
           vol 1092. Springer, Singapore.

    See Also:
        Paper: https://doi.org/10.1007/978-981-99-0561-4_6

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLAhBuNeAgent

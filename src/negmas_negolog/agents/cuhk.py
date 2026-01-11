"""CUHKAgent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.CUHKAgent.CUHKAgent import CUHKAgent as _NLCUHKAgent


class CUHKAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's CUHKAgent.

    **ANAC 2012 Winner**.

    CUHKAgent (developed at Chinese University of Hong Kong by Jianye Hao)
    is an adaptive negotiation agent that adjusts its strategy based on
    opponent behavior and time pressure.

    **Offering Strategy:**
        - Time-dependent concession with adaptive threshold adjustment
        - Concession rate adapts based on opponent's toughness degree
        - In large domains: focuses on high-utility bid range
        - Near deadline: considers opponent's best offer as fallback
        - Uses opponent model to select bids favorable to opponent among
          candidates

    **Acceptance Strategy:**
        - Accepts if offer exceeds current utility threshold
        - Accepts if offer exceeds the utility of planned counter-offer
        - Near deadline: more lenient acceptance based on opponent's best offer
        - Adapts acceptance based on predicted maximum achievable utility

    **Opponent Modeling:**
        - Tracks opponent's bidding history to estimate preferences
        - Calculates opponent's concession degree to adapt own strategy
        - Identifies opponent's maximum offered bid for reference
        - Uses opponent model to choose mutually beneficial bids

    References:
        .. [Hao2014] Hao, J., Leung, Hf. (2014). CUHKAgent: An Adaptive
           Negotiation Strategy for Bilateral Negotiations over Multiple Items.
           In: Novel Insights in Agent-based Complex Automated Negotiation.
           Studies in Computational Intelligence, vol 535. Springer, Tokyo.

    See Also:
        Paper: https://doi.org/10.1007/978-4-431-54758-7_11

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLCUHKAgent

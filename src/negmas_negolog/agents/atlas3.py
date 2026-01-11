"""Atlas3Agent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.Atlas3.Atlas3Agent import Atlas3Agent as _NLAtlas3Agent


class Atlas3Agent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's Atlas3Agent.

    **ANAC 2015 Winner** (Individual Utility & Nash Product categories).

    Atlas3 is a sophisticated negotiation agent developed by Akiyuki Mori that
    uses adaptive strategies based on opponent behavior analysis and game-theoretic
    concepts.

    **Offering Strategy:**
        - Uses appropriate bid searching based on relative utility for linear
          utility spaces
        - Applies replacement method based on frequency analysis of opponent's
          bidding history
        - Concession function derived from Evolutionary Stable Strategy (ESS)
          expected utility analysis
        - Near deadline: cycles through promising bids from opponent's history

    **Acceptance Strategy:**
        - Accepts if the offer utility exceeds the current threshold calculated
          from ESS-based concession function
        - Near deadline: accepts bids above reservation value from candidate list

    **Opponent Modeling:**
        Frequency-based model that tracks opponent's bidding patterns to:
        - Estimate opponent preferences
        - Identify promising bids that might be acceptable to both parties
        - Guide bid search towards mutually beneficial outcomes

    References:
        .. [Mori2017] Mori, A., Ito, T. (2017). Atlas3: A Negotiating Agent Based
           on Expecting Lower Limit of Concession Function. In: Modern Approaches
           to Agent-based Complex Automated Negotiation. Studies in Computational
           Intelligence, vol 674. Springer, Cham.

        .. [Mori2015] Mori, A., & Ito, T. (2015). A compromising strategy based on
           expected utility of evolutionary stable strategy in bilateral closed
           bargaining problem. ACAN 2015.

    See Also:
        Paper: https://doi.org/10.1007/978-3-319-51563-2_11

    Note:
        This description was AI-generated based on the referenced papers
        and source code analysis.
    """

    negolog_agent_class = _NLAtlas3Agent

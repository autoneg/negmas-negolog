"""AgentGG wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.AgentGG.AgentGG import AgentGG as _NLAgentGG


class AgentGG(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's AgentGG.

    **ANAC 2019 Winner** (Individual Utility category).

    AgentGG (developed by Shaobo Xu) uses importance maps (a frequentist
    approach) to estimate both self and opponent preferences, focusing on
    bid importance rather than raw utility values.

    **Offering Strategy:**
        - Time-based concession with importance thresholds
        - Early phase (t < 0.2): random bid selection within threshold
        - Middle phase: selects bids maximizing estimated opponent importance
        - Thresholds decrease over time based on estimated Nash point
        - Uses importance maps instead of utility for bid evaluation

    **Acceptance Strategy:**
        - Accepts if received bid's importance ratio exceeds current threshold
        - Near deadline (t >= 0.9989): accepts if importance exceeds
          reservation + 0.2
        - Thresholds adapt based on estimated Nash point

    **Opponent Modeling:**
        Frequentist importance maps that estimate:
        - Self preferences from own utility function analysis
        - Opponent preferences from their bidding patterns
        - Uses estimated opponent importance to select favorable bids
        - Updates opponent model during early negotiation (t < 0.3)

    References:
        .. [Aydogan2020] Aydogan, R. et al. (2020). Challenges and Main Results
           of the Automated Negotiating Agents Competition (ANAC) 2019.
           In: Multi-Agent Systems and Agreement Technologies. EUMAS AT 2020.
           Lecture Notes in Computer Science, vol 12520. Springer, Cham.

    See Also:
        Paper: https://doi.org/10.1007/978-3-030-66412-1_23

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLAgentGG

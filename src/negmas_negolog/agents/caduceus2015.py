"""Caduceus2015 wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.Caduceus2015.Caduceus import Caduceus2015 as _NLCaduceus2015


class Caduceus2015(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's Caduceus2015 agent.

    **ANAC 2015 Competition Agent**.

    Caduceus2015 by Taha Gunes is a sub-agent developed for the Caduceus
    multilateral negotiation system. It uses Nash product optimization
    to find mutually beneficial outcomes and employs frequency-based
    opponent modeling to estimate opponent preferences.

    **Offering Strategy:**
        Two-phase bidding approach based on time:

        1. **Early phase (t < 0.83)**: Offers the best bid (maximum utility)
           to establish a strong opening position.

        2. **Later phase (t >= 0.83)**: Calculates Nash product across all
           parties using estimated opponent utility spaces:
           - Computes Nash bid that maximizes product of utilities
           - Uses CounterOfferGenerator to generate bids around Nash point
           - Ensures bid utility stays above reservation value (min 0.75)

        If generated bid has lower utility than opponent's last offer
        (by margin > 0.2), accepts instead.

    **Acceptance Strategy:**
        Implicit acceptance based on bid comparison: if the opponent's
        previous bid has utility exceeding the generated counter-offer
        by more than 0.2, the agent accepts. This creates a dynamic
        acceptance threshold based on what the agent can offer.

    **Opponent Modeling:**
        Frequency-based preference estimation with time-weighted updates:

        - Tracks issue-value frequencies using a "round value" weight:

          .. math::

              roundValue = 2t^2 - 101t + 100

          This gives high weight to early observations that decreases
          over time.

        - Extra weight given to values that remain unchanged between
          consecutive opponent bids (stability bonus)
        - Constructs SaneUtilitySpace for each opponent to estimate
          their preferences

    References:
        .. [Gunes2017] Gunes, T.D., Arditi, E., Aydogan, R. (2017).
           Collective Voice of Experts in Multilateral Negotiation.
           In: An, B., Bazzan, A., Leite, J., Villata, S., van der Torre, L.
           (eds) PRIMA 2017: Principles and Practice of Multi-Agent Systems.
           Lecture Notes in Computer Science, vol 10621. Springer, Cham.

    See Also:
        Paper: https://doi.org/10.1007/978-3-319-69131-2_27

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLCaduceus2015

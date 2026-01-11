"""ParsAgent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.ParsAgent.ParsAgent import ParsAgent as _NLParsAgent


class ParsAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's ParsAgent.

    **ANAC 2015 Individual Utility Category Finalist**.

    ParsAgent by Zahra Khosravimehr from Amirkabir University of Technology
    uses a hybrid bidding strategy combining time-dependent, random, and
    frequency-based approaches to propose high-utility offers close to
    opponent preferences, increasing the likelihood of early agreement.

    **Offering Strategy:**
        Employs a multi-step bid generation process:

        1. First checks if there's a mutually beneficial bid from the
           intersection of both opponents' preferences (in multilateral).
        2. If not found, constructs a bid using:
           - Mutual issue values (agreed by both opponents based on frequency)
           - Own best values for non-mutual issues
        3. Falls back to modifying the best bid on the worst-weighted issue

        Target utility follows Boulware-style concession:

        .. math::

            target(t) = 1 - t^{1/e}

        where e = 0.15 (or 0.2 with discount factor). Minimum threshold is 0.7.

    **Acceptance Strategy:**
        Simple time-dependent acceptance: accepts if opponent's offer
        utility exceeds the target utility at current time. The target
        decreases from 1.0 towards 0.7 following the Boulware curve.

    **Opponent Modeling:**
        Frequency-based modeling for each opponent:

        - Tracks repeated values for each issue across opponent bids
        - Identifies mutual preferences between opponents (values both
          opponents frequently request)
        - Maintains sorted list of opponent bids by utility
        - Searches for Nash-like outcomes using common preferences

    References:
        .. [Khosravimehr2017] Khosravimehr, Z., Nassiri-Mofakham, F. (2017).
           Pars Agent: Hybrid Time-Dependent, Random and Frequency-Based
           Bidding and Acceptance Strategies in Multilateral Negotiations.
           In: Fujita, K., et al. Modern Approaches to Agent-based Complex
           Automated Negotiation. Studies in Computational Intelligence,
           vol 674. Springer, Cham.

    See Also:
        Paper: https://doi.org/10.1007/978-3-319-51563-2_12

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLParsAgent

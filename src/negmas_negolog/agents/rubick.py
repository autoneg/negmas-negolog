"""Rubick wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.Rubick.Rubick import Rubick as _NLRubick


class Rubick(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's Rubick agent.

    **ANAC 2017 Individual Utility Category Finalist**.

    Rubick Agent by Okan Tunali is a complex time-based conceder enriched
    with frequency-based opponent modeling. It maintains the highest utility
    ever received as a lower bound and uses randomized Boulware-style
    concession with increasing variance over time.

    **Offering Strategy:**
    Generates bids above a target utility using opponent model insights:

    - Searches for bids that maximize intersection with opponent's
      most frequently offered values (frequency-based search)
    - If no suitable bid found via opponent model, falls back to
      nearest bid to target utility
    - Near deadline (t > 0.995), offers from a cached list of
      previously accepted bids

    Target utility follows randomized Boulware with power parameter
    randomly selected based on max received utility.

    **Acceptance Strategy:**
    Time-based with randomness to prevent exploitation:

    $$target = 1 - t^{power} \cdot |\mathcal{N}(0, 1/3)|$$

    where power is randomly 2, 3, or 10 based on opponent behavior.
    The target is bounded by the maximum received utility.
    Accepts if opponent offer exceeds target or time > 0.999.

    **Opponent Modeling:**
    Employs frequency-based opponent modeling:

    - Tracks value frequencies for each issue per opponent
    - Extracts "bags" of preferred values (above median frequency)
    - Scores bids by counting intersections with opponent preferences
    - Maintains separate models for multilateral scenarios

    Also keeps a sorted list of bids that were accepted by opponents
    in previous negotiations for use near the deadline.

    References:
        .. [Aydogan2021] Reyhan Aydogan, Katsuhide Fujita, Tim Baarslag,
           Catholijn M. Jonker, and Takayuki Ito. ANAC 2017: Repeated
           multilateral negotiation league. In Advances in Automated
           Negotiations, pages 101-115, Singapore, 2021. Springer Singapore.

    See Also:
        Paper: https://doi.org/10.1007/978-981-16-0471-3_7

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLRubick

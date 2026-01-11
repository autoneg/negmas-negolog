"""Kawaii wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.Kawaii.Kawaii import Kawaii as _NLKawaii


class Kawaii(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's Kawaii agent.

    **ANAC 2015 Individual Utility Category Runner-up**.

    Kawaii is a negotiation agent that uses Simulated Annealing for bid
    search and a time-dependent conceding strategy. It adapts its
    acceptance threshold based on the number of accepting opponents in
    multilateral negotiations.

    **Offering Strategy:**
        Uses Simulated Annealing to search for bids near the target utility:

        1. First attempts relative utility search (for linear utility spaces)
           by selecting values that sum to the target concession amount
        2. Falls back to Simulated Annealing with parameters:
           - Start temperature: 1.0
           - End temperature: 0.0001
           - Cooling rate: 0.999

        The search minimizes the distance to target utility while staying
        above it. Returns the maximum utility bid if no suitable bid found.

    **Acceptance Strategy:**
        Time-dependent threshold with conceder behavior (exponent = 2):

        $$threshold(t) = 1 - (1 - a) \cdot t^2$$

        where a = 0.8 is the minimum threshold.

        In multilateral scenarios, the threshold is reduced based on how
        many opponents have already accepted:

        $$threshold -= (threshold - minThreshold) \cdot \frac{acceptCount}{numOpponents}$$

        This encourages acceptance when close to agreement.

    **Opponent Modeling:**
        Tracks which opponents have made accepting moves (offered bids
        close to previous offers). This information adjusts the acceptance
        threshold to facilitate agreement when multiple parties are close
        to consensus.

    References:
        .. [Baarslag2015] Baarslag, T., Aydogan, R., Hindriks, K. V.,
           Fujita, K., Ito, T., & Jonker, C. M. (2015). The Automated
           Negotiating Agents Competition, 2010-2015. AI Magazine,
           36(4), 115-118.

    See Also:
        Paper: https://doi.org/10.1609/aimag.v36i4.2609

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLKawaii

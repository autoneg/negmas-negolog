"""RandomDance wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.RandomDance.RandomDance import RandomDance as _NLRandomDance


class RandomDance(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's RandomDance agent.

    **ANAC 2015 Individual Utility Category Finalist**.

    RandomDance Agent by Shinji Kakimoto proposes an opponent modeling
    approach using multiple weighted utility estimation functions. The
    agent randomly selects among different weighting schemes, making it
    unpredictable while still being responsive to opponent behavior.

    **Offering Strategy:**
        Searches for bids that balance self-utility with estimated opponent
        utility using weighted combination:

        1. For each issue, selects values that maximize weighted sum of
           estimated utilities across all parties
        2. Adjusts own weight iteratively (0 to 10) until finding a bid
           above the target utility
        3. Target utility is adaptive: starts at estimated Nash point and
           decreases following t^discount curve

        Falls back to best bid if no suitable bid found.

    **Acceptance Strategy:**
        Accepts based on target utility comparison with safety margin:

        - Tracks time per round to estimate remaining rounds
        - If remaining rounds <= 5, accepts to avoid negotiation failure
        - Otherwise accepts if opponent's offer exceeds target utility

    **Opponent Modeling:**
        Uses a library of multiple PlayerData models with different
        learning rates (delta = 1.0, 1.05, 0.55):

        - Each model tracks value frequencies with exponential weighting
        - Issue weights derived from maximum value frequencies
        - Randomly selects which model to use for each decision
        - Tracks Nash-optimal opponent (whose bids maximize product of
          estimated utilities) for weighting decisions

        Three weighting strategies randomly selected:
        1. Nash-based: weight by Nash optimality history
        2. Equal: all opponents weighted equally
        3. Alternating: alternate between opponents

    References:
        .. [Kakimoto2017] Kakimoto, S., Fujita, K. (2017). RandomDance:
           Compromising Strategy Considering Interdependencies of Issues
           with Randomness. In: Fujita, K., et al. Modern Approaches to
           Agent-based Complex Automated Negotiation. Studies in
           Computational Intelligence, vol 674. Springer, Cham.

    See Also:
        Paper: https://doi.org/10.1007/978-3-319-51563-2_13

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLRandomDance

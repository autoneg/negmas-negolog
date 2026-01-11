"""NiceTitForTat wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.NiceTitForTat.NiceTitForTat import NiceTitForTat as _NLNiceTitForTat


class NiceTitForTat(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's NiceTitForTat agent.

    NiceTitForTat (developed by Tim Baarslag) implements a cooperative
    tit-for-tat strategy with respect to utility space, aiming for the
    Nash bargaining solution.

    **Offering Strategy:**
        - Initially cooperates with high utility bids
        - Responds in kind to opponent's concessions
        - Calculates opponent's concession factor relative to Nash point
        - Mirrors opponent's concession proportionally
        - Time bonus near deadline to encourage agreement
        - Selects bids that maximize opponent utility among equivalents

    **Acceptance Strategy:**
        - Accepts if opponent's offer >= planned counter-offer utility
        - Near deadline: probabilistic acceptance based on expected utility
          of waiting for better offers
        - Considers recent bid history to estimate probability of improvement

    **Opponent Modeling:**
        Bayesian opponent model that:
        - Updates beliefs about opponent preferences after each bid
        - Estimates opponent's utility function
        - Used to find Nash point and select opponent-favorable bids
        - Guides concession strategy to match opponent's behavior

    References:
        .. [Baarslag2013] Tim Baarslag, Koen Hindriks, and Catholijn Jonker.
           "A tit for tat negotiation strategy for real-time bilateral
           negotiations." Studies in Computational Intelligence, 435:229-233,
           2013.

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLNiceTitForTat

"""Caduceus wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.Caduceus.Caduceus import Caduceus as _NLCaduceus


class Caduceus(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's Caduceus agent.

    **ANAC 2016 Winner** (Individual Utility category).

    Caduceus (developed by Taha Gunes) combines multiple negotiation experts
    using ideas from algorithm portfolios, mixture of experts, and genetic
    algorithms to make collective decisions.

    **Offering Strategy:**
        - Portfolio of 5 expert agents: ParsAgent, RandomDance, Kawaii,
          Atlas3, and Caduceus2015
        - Early phase (t < 0.83): offers the best possible bid
        - Crossover strategy: each expert suggests a bid, then majority
          voting on each issue value determines final bid content
        - Experts are weighted by expertise scores (100, 10, 5, 3, 1)
        - Stochastic selection based on expertise levels

    **Acceptance Strategy:**
        - Weighted voting among expert agents
        - Accepts if weighted score of "accept" votes exceeds "bid" votes
        - Each expert's vote weighted by its expertise score

    **Opponent Modeling:**
        Delegated to individual expert agents in the portfolio:
        - ParsAgent, Atlas3, Kawaii each have their own opponent models
        - Collective decision benefits from diverse modeling approaches

    References:
        .. [Gunes2017] Gunes, T.D., Arditi, E., Aydogan, R. (2017). Collective
           Voice of Experts in Multilateral Negotiation. In: PRIMA 2017:
           Principles and Practice of Multi-Agent Systems. Lecture Notes in
           Computer Science, vol 10621. Springer, Cham.

    See Also:
        Paper: https://doi.org/10.1007/978-3-319-69131-2_27

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLCaduceus

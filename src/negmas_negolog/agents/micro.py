"""MICROAgent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.MICRO.MICRO import MICROAgent as _NLMICROAgent


class MICROAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's MICROAgent.

    **ANAC 2022 Runner-up** (Individual Utility category).

    MiCRO (Monotonic Concession with Reciprocal Offers, developed by Dave de
    Jonge) is a benchmark strategy that only concedes when the opponent
    demonstrates willingness to concede through unique bid proposals.

    **Offering Strategy:**
        - Starts with the highest utility bid
        - Concedes only when opponent has made at least as many unique bids
          as the agent
        - When conceding, moves to the next lower utility bid
        - Checks if opponent has proposed any bid with equal utility and
          prefers to offer those (reciprocity)
        - Between concessions, randomly selects from previously offered bids

    **Acceptance Strategy:**
        - Uses AC_Next: accepts if opponent's last offer provides utility
          greater than or equal to the agent's planned next bid
        - Also requires offer to meet reservation value

    **Opponent Modeling:**
        Simple reciprocity-based tracking:
        - Counts unique bids received from opponent
        - Uses this count to determine when to concede (tit-for-tat style)
        - Checks if opponent has proposed equivalent-utility bids for
          preferential selection

    References:
        .. [deJonge2022] Dave de Jonge. "An analysis of the linear bilateral
           ANAC domains using the MiCRO benchmark strategy." IJCAI 2022,
           Vienna, Austria, pp. 223-229.

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLMICROAgent

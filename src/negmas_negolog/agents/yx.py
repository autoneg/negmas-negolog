"""YXAgent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.YXAgent.YXAgent import YXAgent as _NLYXAgent


class YXAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's YXAgent.

    **ANAC 2016 Individual Utility Category Runner-up**.

    YXAgent employs a frequency-based opponent modeling approach combined with
    threshold-based bidding and acceptance strategies. The agent maintains
    separate models for issue weights and value frequencies for each opponent,
    identifying the "toughest" opponent to inform its acceptance decisions.

    **Offering Strategy:**
        The agent generates random bids above a threshold that is calculated
        based on the number of opponents (minimum 0.7). In early rounds, it
        offers bids with utility above a temporary threshold. After 10 rounds
        and before 90% of the time has elapsed, it uses the opponent model to
        calculate a more nuanced threshold based on the estimated utility of
        the opponent's last bid according to the toughest opponent's model.

    **Acceptance Strategy:**
        - In early rounds (first 10) or late game (>90% time): accepts if the
          opponent's offer utility exceeds the temporary threshold.
        - During mid-game: accepts if the opponent's offer utility exceeds a
          calculated threshold that accounts for the opponent model's
          evaluation of the bid.

    **Opponent Modeling:**
        YXAgent builds frequency-based models for each opponent:

        - **Issue weights**: Updated when the opponent keeps the same value
          for an issue between consecutive bids, using a time-decaying formula.
        - **Value frequencies**: Tracks how often each value is offered,
          normalized by the maximum frequency.
        - Identifies the "hardest" (toughest) opponent based on their behavior.

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

    negolog_agent_class = _NLYXAgent

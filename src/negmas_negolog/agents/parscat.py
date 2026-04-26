"""ParsCatAgent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.ParsCat.ParsCat import ParsCatAgent as _NLParsCatAgent


class ParsCatAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's ParsCatAgent.

    **ANAC 2016 Individual Utility Category Runner-up**.

    ParsCatAgent is developed by Amirkabir University of Technology and uses
    a time-dependent bidding strategy with a complex piecewise acceptance
    function. The agent maintains a history of opponent bids and uses
    time-based thresholds that vary across different negotiation phases.

    **Offering Strategy:**
        The agent generates random bids within a narrow utility window around
        a time-varying threshold. The threshold decreases over time but with
        different rates across negotiation phases:

        - t < 0.5: threshold = 1.0 - t/4 (slow concession)
        - 0.5 <= t < 0.8: threshold = 0.9 - t/5
        - 0.8 <= t < 0.9: threshold = 0.7 + t/5 (strategic increase)
        - 0.9 <= t < 0.95: threshold = 0.8 + t/5
        - t >= 0.95: threshold = 1.0 - t/4 - 0.01

        The search window around the threshold is typically +/- 0.01 to 0.02.
        If the best opponent bid has higher utility than the generated bid
        (in bilateral negotiations), it returns the opponent's best bid.

    **Acceptance Strategy:**
        Uses a complex piecewise function based on negotiation time with 10
        distinct phases, creating an oscillating acceptance threshold:

        - Starts high (1.0), drops to ~0.9 by t=0.25
        - Oscillates between 0.7-1.0 through mid-game
        - Ends around 0.5-0.7 in the final phase

        This non-monotonic pattern makes the agent's behavior harder to
        predict and exploit.

    **Opponent Modeling:**
        Maintains a history of opponent bids with utilities and timestamps.
        Uses the best bid from opponent history as a fallback offer when
        the generated bid has lower utility.

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

    negolog_agent_class = _NLParsCatAgent

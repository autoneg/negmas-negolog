"""AgentKN wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.AgentKN.AgentKN import AgentKN as _NLAgentKN


class AgentKN(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's AgentKN.

    **ANAC 2017 Nash Product Category Finalist**.

    AgentKN by Keita Nakamura uses Simulated Annealing for bid search and
    a sophisticated opponent modeling approach to estimate the maximum
    utility the opponent might offer. It balances self-utility maximization
    with opponent value frequency analysis.

    **Offering Strategy:**
        Uses Simulated Annealing to search for 10 bids that maximize utility
        while starting from a random initial bid. The bids are then scored
        using a combined metric:

        $$score = utility + 0.1^{(\log_{10}(frequency)+1)} \cdot frequency \cdot utility$$

        where frequency is the sum of opponent-offered value frequencies.
        This encourages bids that are both high-utility and contain values
        the opponent has frequently requested.

    **Acceptance Strategy:**
        Accepts when the opponent's bid exceeds a dynamic threshold:

        $$threshold(t) = 1 - (1 - e_{max}(t)) \cdot t^\alpha$$

        where alpha > 1 controls concession rate and e_max(t) is the
        estimated maximum utility the opponent might offer, calculated as:

        $$e_{max}(t) = \mu(t) + (1 - \mu(t)) \cdot d(t)$$

        $$d(t) = \frac{\sqrt{3} \cdot \sigma(t)}{\sqrt{\mu(t) \cdot (1 - \mu(t))}}$$

        where mu(t) is the mean and sigma(t) is the standard deviation of
        utilities from opponent offers.

    **Opponent Modeling:**
        Tracks value frequencies for each issue across opponent bids:

        - Updates issue weights when consecutive bids have the same value
        - Maintains normalized value frequency counts per issue
        - Uses statistical analysis (mean, std) of opponent bid utilities
          to estimate the opponent's bidding range

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

    negolog_agent_class = _NLAgentKN

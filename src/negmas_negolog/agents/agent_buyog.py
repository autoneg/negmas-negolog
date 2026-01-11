"""AgentBuyog wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.AgentBuyog.AgentBuyog import AgentBuyog as _NLAgentBuyog


class AgentBuyog(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's AgentBuyog.

    **ANAC 2015 Individual Utility Category Runner-up**.

    AgentBuyog estimates the opponent's concession function using regression
    analysis and uses this to determine optimal acceptance thresholds. It
    also estimates opponent preferences to find bids near the Kalai point
    (social welfare maximum).

    **Offering Strategy:**
        Selects bids based on domain competitiveness and opponent difficulty:

        1. Calculates acceptance threshold based on estimated opponent
           difficulty and time-based concession:

           .. math::

               threshold = minPoint + (1 - minPoint) \\cdot (1 - t^{1.8})

        2. Searches for bids at or above threshold that are closest to
           the estimated Kalai point (maximizing social welfare)
        3. If common bids exist (offered by multiple opponents), prefers
           those with highest utility

        Near deadline (remaining rounds <= 3), threshold is halved.

    **Acceptance Strategy:**
        Multi-criteria acceptance based on:

        - Most recent offer utility vs. threshold
        - Best agreeable bid utility (common to both opponents)
        - Generated bid utility

        Accepts if opponent's offer exceeds all other options and the
        acceptance threshold, especially when near deadline.

    **Opponent Modeling:**
        Sophisticated multi-component model:

        - **Concession estimation**: Uses weighted regression to fit
          exponential concession function exp(alpha) * t^beta to opponent
          bid utilities over time
        - **Leniency calculation**: Derived from slope of estimated
          concession curve, adjusted by a leniency factor
        - **Preference estimation**: Frequency-based issue weight and
          value estimation, normalized after each update
        - **Kalai point estimation**: Finds social welfare maximum
          using estimated opponent preferences
        - **Agent difficulty**: Combined metric of leniency and domain
          competitiveness to assess how hard to negotiate with

    References:
        .. [Fujita2017] Fujita, K., Aydogan, R., Baarslag, T., Hindriks, K.,
           Ito, T., Jonker, C. (2017). The Sixth Automated Negotiating
           Agents Competition (ANAC 2015). In: Fujita, K., et al. Modern
           Approaches to Agent-based Complex Automated Negotiation. Studies
           in Computational Intelligence, vol 674. Springer, Cham.

    See Also:
        Paper: https://doi.org/10.1007/978-3-319-51563-2_9

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLAgentBuyog

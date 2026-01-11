"""IAMhaggler wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.IAMhaggler.IAMhaggler import IAMhaggler as _NLIAMhaggler


class IAMhaggler(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's IAMhaggler agent.

    **ANAC 2012 Winner** (Nash Product category).

    IAMhaggler (developed by Colin R. Williams at University of Southampton)
    uses Gaussian Process regression to predict opponent behavior and
    optimize concession timing.

    **Offering Strategy:**
        - Uses Gaussian Process to predict when opponent will make maximum
          concession
        - Calculates expected utility surface over time and utility dimensions
        - Target utility based on interpolation toward predicted best agreement
        - Limits concession based on observed opponent bidding range
        - Risk-aware utility function with configurable risk parameter

    **Acceptance Strategy:**
        - Accepts if opponent's offer * multiplier >= target utility
        - Accepts if opponent's offer * multiplier >= maximum aspiration (0.9)
        - Accepts if opponent's offer >= planned bid utility
        - Multiple acceptance thresholds for robustness

    **Opponent Modeling:**
        Gaussian Process regression approach:
        - Tracks opponent utilities over time slots
        - Fits GP model to predict future opponent concessions
        - Calculates probability distribution of opponent's future offers
        - Uses predictions to optimize concession timing
        - Incorporates discounting factor for time-sensitive domains

    References:
        .. [Williams2012] Williams, C.R., Robu, V., Gerding, E.H., Jennings, N.R.
           (2012). IAMhaggler: A Negotiation Agent for Complex Environments.
           In: New Trends in Agent-Based Complex Automated Negotiations.
           Studies in Computational Intelligence, vol 383. Springer.

    See Also:
        Paper: https://doi.org/10.1007/978-3-642-24696-8_10

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLIAMhaggler

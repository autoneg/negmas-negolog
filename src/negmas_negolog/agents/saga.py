"""SAGAAgent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.SAGA.SAGAAgent import SAGAAgent as _NLSAGAAgent


class SAGAAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's SAGAAgent.

    **ANAC 2019 Individual Utility Category Finalist**.

    SAGA (Simulated Annealing Genetic Algorithm) Agent by Yuta Hosokawa
    applies a Genetic Algorithm approach to estimate its own preferences
    (using Spearman correlation as the fitness function) combined with
    time-based bidding and acceptance strategies.

    **Offering Strategy:**
    Uses a time-dependent target utility function:

    $$target(t) = target_{min} + (1 - target_{min}) \cdot (1 - t^5)$$

    where target_min is derived from the utility of the first received
    bid: target_min = firstUtil + 0.6 * (1 - firstUtil).

    Bids are randomly generated above the target utility threshold.

    **Acceptance Strategy:**
    Employs a three-phase probabilistic acceptance strategy:

    - **Phase 1 (t <= 0.6)**: Probabilistic acceptance based on how much
      the offer exceeds the target. Uses power function with exponent
      that increases as time approaches 0.5.
    - **Phase 2 (0.6 < t < 0.997)**: Gradually increasing acceptance
      probability for bids below target, with linear interpolation.
    - **Phase 3 (t >= 0.997)**: Near deadline, accepts with probability
      proportional to utility squared.

    Always rejects offers below reservation value.

    **Opponent Modeling:**
    SAGA Agent was designed to use Genetic Algorithm to estimate
    preferences, though the current implementation uses actual
    preferences. The GA approach uses Spearman rank correlation as
    the fitness metric to evaluate preference estimation quality.

    References:
        .. [Aydogan2020] Aydogan, R. et al. (2020). Challenges and Main
           Results of the Automated Negotiating Agents Competition (ANAC)
           2019. In: Bassiliades, N., Chalkiadakis, G., de Jonge, D. (eds)
           Multi-Agent Systems and Agreement Technologies. EUMAS AT 2020.
           Lecture Notes in Computer Science, vol 12520. Springer, Cham.

    See Also:
        Paper: https://doi.org/10.1007/978-3-030-66412-1_23

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLSAGAAgent

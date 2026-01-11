"""PonPokoAgent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.PonPoko.PonPoko import PonPokoAgent as _NLPonPokoAgent


class PonPokoAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's PonPokoAgent.

    **ANAC 2017 Individual Utility Category Winner**.

    PonPokoAgent by Takaki Matsune employs a randomized multi-strategy approach
    that makes it difficult for opponents to predict its behavior. At the start
    of each negotiation session, it randomly selects one of 5 different bidding
    patterns, each with distinct concession characteristics.

    **Offering Strategy:**
        The agent randomly selects one of 5 bidding patterns at initialization:

        - **Pattern 0**: Sinusoidal oscillation with slow linear decline.
          High/Low thresholds follow sin(40t) pattern.
        - **Pattern 1**: Linear concession from 1.0, slow decline to 0.78.
        - **Pattern 2**: Sinusoidal with larger amplitude (sin(20t)).
        - **Pattern 3**: Very conservative, minimal concession (0.95-1.0)
          until deadline when it drops to 0.7.
        - **Pattern 4**: Sinusoidal pattern tied to time (sin(20t) * t).

        Bids are selected from the pre-sorted bid space within the
        [threshold_low, threshold_high] utility range.

    **Acceptance Strategy:**
        Accepts if the opponent's offer has utility greater than the current
        threshold_low value. This creates a simple but effective acceptance
        criterion that varies with the selected bidding pattern.

    **Opponent Modeling:**
        PonPokoAgent does not employ explicit opponent modeling. Its strength
        lies in the unpredictability of its randomly selected strategy, making
        it resistant to exploitation by adaptive opponents.

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

    negolog_agent_class = _NLPonPokoAgent

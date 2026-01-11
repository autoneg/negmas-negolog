"""ConcederAgent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.conceder.Conceder import ConcederAgent as _NLConcederAgent


class ConcederAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's ConcederAgent.

    A "soft" time-based concession agent that concedes quickly (super-linearly)
    over the negotiation deadline. Useful when reaching agreement is more
    important than maximizing utility.

    **Offering Strategy:**
        Uses a quadratic Bézier curve to calculate target utility over time:

        .. math::
            TU = (1-t)^2 P_0 + 2(1-t)t P_1 + t^2 P_2

        where t is normalized time [0,1], P0=1.0 (initial utility),
        P1=0.55 (control point), and P2=0.4 (final utility). The low P1 value
        (P1 <= (P0+P2)/2) creates a convex curve that concedes quickly early
        in the negotiation.

    **Acceptance Strategy:**
        Uses AC_Next: accepts if the opponent's last offer provides utility
        greater than or equal to the agent's current target utility.

    **Opponent Modeling:**
        None. This is a pure time-based strategy that ignores opponent behavior.

    References:
        .. [Faratin1998] Peyman Faratin, Carles Sierra, and Nick R. Jennings.
           "Negotiation decision functions for autonomous agents."
           Robotics and Autonomous Systems 24, 3 (1998), 159-182.

        .. [Vahidov2017] Rustam M. Vahidov, Gregory E. Kersten, and Bo Yu.
           "Human-Agent Negotiations: The Impact Agents' Concession Schedule
           and Task Complexity on Agreements." HICSS 2017.

    See Also:
        Paper: https://doi.org/10.1016/S0921-8890(98)00023-6

    Note:
        This description was AI-generated based on the referenced papers
        and source code analysis.
    """

    negolog_agent_class = _NLConcederAgent

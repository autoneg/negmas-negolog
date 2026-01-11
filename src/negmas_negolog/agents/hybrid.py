"""HybridAgent wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.HybridAgent.HybridAgent import HybridAgent as _NLHybridAgent


class HybridAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's HybridAgent.

    HybridAgent combines Time-Based and Behavior-Based negotiation strategies
    using a Bezier curve for time-based concession and weighted opponent
    move mirroring for behavior-based adaptation. It was developed for
    emotional and opponent-aware human-robot negotiation research.

    **Offering Strategy:**
        Combines two strategies with time-varying weights:

        1. **Time-Based (Bezier curve)**:

           $$target_{time}(t) = (1-t)^2 p_0 + 2(1-t)t \cdot p_1 + t^2 \cdot p_2$$

           where p0=1.0, p1=0.75, p2=0.55 (bounded by reservation value).

        2. **Behavior-Based**: Mirrors opponent concession moves using a
           weighted window of recent utility differences:

           - Window weights: {1: [1], 2: [0.25, 0.75], 3: [0.11, 0.22, 0.66],
             4: [0.05, 0.15, 0.3, 0.5]}
           - Empathy parameter p3=0.5 controls response magnitude

        Combined target (after first 2 rounds):

        $$target = (1-t^2) \cdot target_{behavior} + t^2 \cdot target_{time}$$

        This starts behavior-focused and shifts to time-based near deadline.

    **Acceptance Strategy:**
        AC_Next strategy: accepts if opponent's last offer utility exceeds
        the current target utility. Simple but effective when combined
        with the hybrid target calculation.

    **Opponent Modeling:**
        Implicit modeling through behavior-based component:

        - Tracks utility differences between consecutive opponent offers
        - Uses weighted window to emphasize recent moves (recent moves
          have higher weight)
        - Adapts own concession rate based on opponent's concession pattern
        - Empathy factor increases with time: (p3 + p3 * t)

    References:
        .. [Keskin2021] Mehmet Onur Keskin, Umut Cakan, and Reyhan Aydogan.
           2021. Solver Agent: Towards Emotional and Opponent-Aware Agent
           for Human-Robot Negotiation. In Proceedings of the 20th
           International Conference on Autonomous Agents and MultiAgent
           Systems (AAMAS '21). International Foundation for Autonomous
           Agents and Multiagent Systems, Richland, SC, 1557-1559.

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLHybridAgent

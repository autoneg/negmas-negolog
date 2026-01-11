"""LuckyAgent2022 wrapper for NegMAS."""

from negmas_negolog.common import NegologNegotiatorWrapper
from agents.LuckyAgent2022.LuckyAgent2022 import LuckyAgent2022 as _NLLuckyAgent2022


class LuckyAgent2022(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's LuckyAgent2022.

    **ANAC 2022 Runner-up** (Individual Utility category).

    LuckyAgent2022 (developed by Arash Ebrahimnezhad) uses BOA (Bidding,
    Opponent modeling, Acceptance) components with a novel Stop-Learning
    Mechanism (SLM) adapted from multi-armed bandit theory to prevent
    overfitting.

    **Offering Strategy:**
        - Time-dependent bidding with adaptive thresholds
        - Divides target utility range into multiple goals (NUMBER_OF_GOALS=5)
        - Randomly selects from bids matching utility goals
        - Weights bid selection by estimated opponent utility
        - Uses sinusoidal variation in lower threshold for exploration

    **Acceptance Strategy:**
        - Condition 1: Offer exceeds acceptance threshold and reservation
        - Condition 2: Near deadline (t > 0.97) with offer above minimum
        - Condition 3: Weighted offer utility exceeds next planned bid utility
        - Multiple acceptance conditions increase agreement likelihood

    **Opponent Modeling:**
        Frequency-based model with Stop-Learning Mechanism:
        - Tracks opponent bids to estimate preferences
        - Uses multi-armed bandit approach to balance exploration/exploitation
        - SLM prevents overfitting by stopping learning at optimal point
        - Model used to weight bid selection toward opponent preferences

    References:
        .. [Ebrahimnezhad2022] A. Ebrahimnezhad and F. Nassiri-Mofakham,
           LuckyAgent2022: A Stop-Learning Multi-Armed Bandit Automated
           Negotiating Agent. 13th International Conference on Information
           and Knowledge Technology (IKT), 2022.

    See Also:
        Paper: https://doi.org/10.1109/IKT57960.2022.10039035

    Note:
        This description was AI-generated based on the referenced paper
        and source code analysis.
    """

    negolog_agent_class = _NLLuckyAgent2022

"""
negmas-negolog: Bridge between NegMAS and NegoLog negotiation frameworks.

This package provides wrapper classes that allow NegoLog negotiating agents
to be used within the NegMAS framework as SAONegotiator subclasses.

Wrapper classes share the same names as their NegoLog counterparts for ease of use.

Example usage:
    >>> from negmas.sao import SAOMechanism, AspirationNegotiator
    >>> from negmas_negolog import BoulwareAgent
    >>>
    >>> mechanism = SAOMechanism(issues=issues, n_steps=100)
    >>> mechanism.add(BoulwareAgent(name='boulware'), preferences=ufun1)
    >>> mechanism.add(AspirationNegotiator(name='aspiration'), preferences=ufun2)
    >>> result = mechanism.run()
"""

from negmas_negolog.wrapper import (
    # Base wrapper class
    NegologNegotiatorWrapper,
    # Preference adapter
    NegologPreferenceAdapter,
    # Time-based agents
    BoulwareAgent,
    ConcederAgent,
    LinearAgent,
    # Competition agents
    MICROAgent,
    Atlas3Agent,
    NiceTitForTat,
    YXAgent,
    ParsCatAgent,
    PonPokoAgent,
    AgentGG,
    SAGAAgent,
    CUHKAgent,
    AgentKN,
    Rubick,
    AhBuNeAgent,
    ParsAgent,
    RandomDance,
    AgentBuyog,
    Kawaii,
    Caduceus2015,
    Caduceus,
    HardHeaded,
    IAMhaggler,
    LuckyAgent2022,
    HybridAgent,
)

__all__ = [
    # Base wrapper class
    "NegologNegotiatorWrapper",
    # Preference adapter
    "NegologPreferenceAdapter",
    # Time-based agents
    "BoulwareAgent",
    "ConcederAgent",
    "LinearAgent",
    # Competition agents
    "MICROAgent",
    "Atlas3Agent",
    "NiceTitForTat",
    "YXAgent",
    "ParsCatAgent",
    "PonPokoAgent",
    "AgentGG",
    "SAGAAgent",
    "CUHKAgent",
    "AgentKN",
    "Rubick",
    "AhBuNeAgent",
    "ParsAgent",
    "RandomDance",
    "AgentBuyog",
    "Kawaii",
    "Caduceus2015",
    "Caduceus",
    "HardHeaded",
    "IAMhaggler",
    "LuckyAgent2022",
    "HybridAgent",
]

__version__ = "0.1.0"

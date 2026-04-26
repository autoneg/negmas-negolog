"""
Agent wrapper classes for bridging NegoLog agents to NegMAS.

This package provides individual wrapper classes for each NegoLog agent,
all inheriting from NegologNegotiatorWrapper.
"""

from negmas_negolog.agents.boulware import BoulwareAgent
from negmas_negolog.agents.conceder import ConcederAgent
from negmas_negolog.agents.linear import LinearAgent
from negmas_negolog.agents.micro import MICROAgent
from negmas_negolog.agents.atlas3 import Atlas3Agent
from negmas_negolog.agents.nice_tit_for_tat import NiceTitForTat
from negmas_negolog.agents.yx import YXAgent
from negmas_negolog.agents.parscat import ParsCatAgent
from negmas_negolog.agents.ponpoko import PonPokoAgent
from negmas_negolog.agents.agent_gg import AgentGG
from negmas_negolog.agents.saga import SAGAAgent
from negmas_negolog.agents.cuhk import CUHKAgent
from negmas_negolog.agents.agent_kn import AgentKN
from negmas_negolog.agents.rubick import Rubick
from negmas_negolog.agents.ahbune import AhBuNeAgent
from negmas_negolog.agents.pars import ParsAgent
from negmas_negolog.agents.random_dance import RandomDance
from negmas_negolog.agents.agent_buyog import AgentBuyog
from negmas_negolog.agents.kawaii import Kawaii
from negmas_negolog.agents.caduceus2015 import Caduceus2015
from negmas_negolog.agents.caduceus import Caduceus
from negmas_negolog.agents.hardheaded import HardHeaded
from negmas_negolog.agents.iamhaggler import IAMhaggler
from negmas_negolog.agents.lucky2022 import LuckyAgent2022
from negmas_negolog.agents.hybrid import HybridAgent

__all__ = [
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

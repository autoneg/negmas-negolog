"""Registration module for negmas-negolog agents in the negmas registry.

This module registers all negmas-negolog agent wrappers in the negmas registry system,
allowing them to be discovered and queried alongside built-in negmas negotiators.

The registration happens automatically when negmas_negolog is imported (if negmas
registry is available).

Naming Convention:
    Agents that have the same name as Genius agents are prefixed with "NL" (NegoLog)
    to avoid conflicts. For example:
    - AgentGG (Genius) vs NLAgentGG (NegoLog)
    - HardHeaded (Genius) vs NLHardHeaded (NegoLog)

    Agents unique to negolog keep their original names (e.g., Atlas3Agent, BoulwareAgent).

Example:
    # After importing negmas_negolog, agents are registered
    from negmas_negolog import Atlas3Agent
    from negmas import negotiator_registry

    # Query all negolog agents
    negolog_agents = negotiator_registry.query(tags={"negolog"})

    # Query ANAC 2019 agents (including negolog ones)
    anac_2019 = negotiator_registry.query(anac_year=2019)

    # Query by specific tag combinations
    negolog_anac = negotiator_registry.query(tags={"negolog", "anac"})

    # Get negolog version of AgentGG specifically
    nl_agent_gg = negotiator_registry.get("NLAgentGG")
"""

from __future__ import annotations

__all__: list[str] = []

# Agents that conflict with Genius agent names - use "NL" prefix
# These are agents that exist in both Genius and NegoLog
_GENIUS_CONFLICTING_NAMES = {
    "AgentGG",
    "AgentKN",
    "AgentBuyog",
    "Caduceus",
    "CUHKAgent",
    "HardHeaded",
    "IAMhaggler",
    "Kawaii",
    "NiceTitForTat",
    "ParsAgent",
    "PonPokoAgent",
    "RandomDance",
    "Rubick",
    "YXAgent",
}


def _get_short_name(class_name: str) -> str:
    """Get the short name for registration, adding NL prefix if needed."""
    if class_name in _GENIUS_CONFLICTING_NAMES:
        return f"NL{class_name}"
    return class_name


def _register_negolog_agents() -> None:
    """Register all negmas-negolog agents in the negmas registry.

    This function registers all NegoLog agent wrappers with appropriate metadata
    including:
    - short_name: The class name (with "NL" prefix for Genius conflicts)
    - bilateral_only: True (all NegoLog agents are bilateral)
    - anac_year: The ANAC competition year (if applicable)
    - tags: Set of tags for categorization and filtering

    Tags used:
    - "negolog": All agents from this package
    - "sao": Works with SAO protocol
    - "propose": Can propose offers
    - "respond": Can respond to offers
    - "time-based": Time-based concession strategy (Boulware, Conceder, Linear)
    - "anac": Competed in ANAC competition
    - "anac-YYYY": Specific ANAC year
    - "learning": Uses opponent modeling/learning
    - "frequency": Uses frequency-based opponent model
    - "bayesian": Uses Bayesian opponent model
    - "tit-for-tat": Uses tit-for-tat strategy
    """
    try:
        from negmas.registry import negotiator_registry
    except ImportError:
        # negmas registry not available, skip registration
        return

    # Import all agent classes
    from negmas_negolog.agents import (
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

    # Base tags for all negolog agents
    base_tags = {"negolog", "sao", "propose", "respond"}

    # =========================================================================
    # Time-based agents (no specific ANAC year)
    # =========================================================================

    negotiator_registry.register(
        BoulwareAgent,
        short_name="BoulwareAgent",
        bilateral_only=True,
        tags=base_tags | {"time-based", "boulware"},
    )

    negotiator_registry.register(
        ConcederAgent,
        short_name="ConcederAgent",
        bilateral_only=True,
        tags=base_tags | {"time-based", "conceder"},
    )

    negotiator_registry.register(
        LinearAgent,
        short_name="LinearAgent",
        bilateral_only=True,
        tags=base_tags | {"time-based", "linear"},
    )

    # =========================================================================
    # ANAC 2010 agents
    # =========================================================================

    negotiator_registry.register(
        IAMhaggler,
        short_name=_get_short_name("IAMhaggler"),
        bilateral_only=True,
        anac_year=2010,
        tags=base_tags | {"anac", "anac-2010", "learning", "bayesian"},
    )

    # =========================================================================
    # ANAC 2011 agents
    # =========================================================================

    negotiator_registry.register(
        HardHeaded,
        short_name=_get_short_name("HardHeaded"),
        bilateral_only=True,
        anac_year=2011,
        tags=base_tags | {"anac", "anac-2011", "learning", "frequency"},
    )

    negotiator_registry.register(
        NiceTitForTat,
        short_name=_get_short_name("NiceTitForTat"),
        bilateral_only=True,
        anac_year=2011,
        tags=base_tags | {"anac", "anac-2011", "tit-for-tat"},
    )

    # =========================================================================
    # ANAC 2012 agents
    # =========================================================================

    negotiator_registry.register(
        CUHKAgent,
        short_name=_get_short_name("CUHKAgent"),
        bilateral_only=True,
        anac_year=2012,
        tags=base_tags | {"anac", "anac-2012", "learning", "frequency"},
    )

    # =========================================================================
    # ANAC 2015 agents
    # =========================================================================

    negotiator_registry.register(
        Atlas3Agent,
        short_name="Atlas3Agent",
        bilateral_only=True,
        anac_year=2015,
        tags=base_tags | {"anac", "anac-2015", "learning", "frequency"},
    )

    negotiator_registry.register(
        ParsAgent,
        short_name=_get_short_name("ParsAgent"),
        bilateral_only=True,
        anac_year=2015,
        tags=base_tags | {"anac", "anac-2015", "learning"},
    )

    negotiator_registry.register(
        RandomDance,
        short_name=_get_short_name("RandomDance"),
        bilateral_only=True,
        anac_year=2015,
        tags=base_tags | {"anac", "anac-2015", "random"},
    )

    negotiator_registry.register(
        AgentBuyog,
        short_name=_get_short_name("AgentBuyog"),
        bilateral_only=True,
        anac_year=2015,
        tags=base_tags | {"anac", "anac-2015", "learning"},
    )

    negotiator_registry.register(
        Kawaii,
        short_name=_get_short_name("Kawaii"),
        bilateral_only=True,
        anac_year=2015,
        tags=base_tags | {"anac", "anac-2015", "learning", "frequency"},
    )

    negotiator_registry.register(
        Caduceus2015,
        short_name="Caduceus2015",
        bilateral_only=True,
        anac_year=2015,
        tags=base_tags | {"anac", "anac-2015", "learning"},
    )

    # =========================================================================
    # ANAC 2016 agents
    # =========================================================================

    negotiator_registry.register(
        YXAgent,
        short_name=_get_short_name("YXAgent"),
        bilateral_only=True,
        anac_year=2016,
        tags=base_tags | {"anac", "anac-2016", "learning", "frequency"},
    )

    negotiator_registry.register(
        ParsCatAgent,
        short_name="ParsCatAgent",
        bilateral_only=True,
        anac_year=2016,
        tags=base_tags | {"anac", "anac-2016", "learning"},
    )

    negotiator_registry.register(
        Caduceus,
        short_name=_get_short_name("Caduceus"),
        bilateral_only=True,
        anac_year=2016,
        tags=base_tags | {"anac", "anac-2016", "learning"},
    )

    # =========================================================================
    # ANAC 2017 agents
    # =========================================================================

    negotiator_registry.register(
        PonPokoAgent,
        short_name=_get_short_name("PonPokoAgent"),
        bilateral_only=True,
        anac_year=2017,
        tags=base_tags | {"anac", "anac-2017", "learning", "frequency"},
    )

    negotiator_registry.register(
        AgentKN,
        short_name=_get_short_name("AgentKN"),
        bilateral_only=True,
        anac_year=2017,
        tags=base_tags | {"anac", "anac-2017", "learning"},
    )

    negotiator_registry.register(
        Rubick,
        short_name=_get_short_name("Rubick"),
        bilateral_only=True,
        anac_year=2017,
        tags=base_tags | {"anac", "anac-2017", "learning"},
    )

    # =========================================================================
    # ANAC 2019 agents
    # =========================================================================

    negotiator_registry.register(
        AgentGG,
        short_name=_get_short_name("AgentGG"),
        bilateral_only=True,
        anac_year=2019,
        tags=base_tags | {"anac", "anac-2019", "learning", "frequency"},
    )

    negotiator_registry.register(
        SAGAAgent,
        short_name="SAGAAgent",
        bilateral_only=True,
        anac_year=2019,
        tags=base_tags | {"anac", "anac-2019", "learning"},
    )

    # =========================================================================
    # ANAC 2022 agents
    # =========================================================================

    negotiator_registry.register(
        LuckyAgent2022,
        short_name="LuckyAgent2022",
        bilateral_only=True,
        anac_year=2022,
        tags=base_tags | {"anac", "anac-2022", "learning"},
    )

    # =========================================================================
    # Other competition agents (year uncertain or multi-year)
    # =========================================================================

    negotiator_registry.register(
        MICROAgent,
        short_name="MICROAgent",
        bilateral_only=True,
        tags=base_tags | {"micro", "learning"},
    )

    negotiator_registry.register(
        AhBuNeAgent,
        short_name="AhBuNeAgent",
        bilateral_only=True,
        tags=base_tags | {"learning"},
    )

    negotiator_registry.register(
        HybridAgent,
        short_name="HybridAgent",
        bilateral_only=True,
        tags=base_tags | {"hybrid", "learning"},
    )


# Auto-register when this module is imported
_register_negolog_agents()

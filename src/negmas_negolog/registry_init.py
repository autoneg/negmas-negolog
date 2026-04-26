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
    anac_2019 = negotiator_registry.query(tags={"anac-2019"})

    # Query by specific tag combinations
    negolog_anac = negotiator_registry.query(tags={"negolog", "anac"})

    # Get negolog version of AgentGG specifically
    nl_agent_gg = negotiator_registry.get_class("NLAgentGG")
"""

from __future__ import annotations

from typing import Any

__all__: list[str] = []

# Source identifier for all negolog registrations
_SOURCE = "negolog"

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


def _register_negotiator(
    registry: Any,
    cls: type,
    short_name: str,
    tags: set[str],
) -> None:
    """Register a negotiator with backward compatibility.

    Tries to register with the new API (source parameter and tags for booleans).
    If that fails due to unexpected keyword argument, falls back to the old API.

    Args:
        registry: The negotiator registry to register with.
        cls: The negotiator class to register.
        short_name: The short name for registration.
        tags: Set of tags for the negotiator.
    """
    try:
        # New API: use source parameter and pass boolean features as tags
        registry.register(
            cls,
            short_name=short_name,
            source=_SOURCE,
            tags=tags,
        )
    except TypeError:
        # Old API: no source parameter, use bilateral_only as keyword arg
        # Extract anac_year from tags if present
        anac_year = None
        for tag in tags:
            if tag.startswith("anac-") and tag != "anac":
                try:
                    anac_year = int(tag.split("-")[1])
                except (ValueError, IndexError):
                    pass

        registry.register(
            cls,
            short_name=short_name,
            bilateral_only=True,
            anac_year=anac_year,
            tags=tags,
        )


def _register_negolog_agents() -> None:
    """Register all negmas-negolog agents in the negmas registry.

    This function registers all NegoLog agent wrappers with appropriate metadata
    including:
    - short_name: The class name (with "NL" prefix for Genius conflicts)
    - source: "negolog" to identify the origin of these agents
    - tags: Set of tags for categorization and filtering

    Tags used:
    - "negolog": All agents from this package
    - "sao": Works with SAO protocol
    - "propose": Can propose offers
    - "respond": Can respond to offers
    - "bilateral-only": Only works in bilateral negotiations
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
    base_tags = {"negolog", "sao", "propose", "respond", "bilateral-only"}

    # =========================================================================
    # Time-based agents (no specific ANAC year)
    # =========================================================================

    _register_negotiator(
        negotiator_registry,
        BoulwareAgent,
        short_name="BoulwareAgent",
        tags=base_tags | {"time-based", "boulware"},
    )

    _register_negotiator(
        negotiator_registry,
        ConcederAgent,
        short_name="ConcederAgent",
        tags=base_tags | {"time-based", "conceder"},
    )

    _register_negotiator(
        negotiator_registry,
        LinearAgent,
        short_name="LinearAgent",
        tags=base_tags | {"time-based", "linear"},
    )

    # =========================================================================
    # ANAC 2010 agents
    # =========================================================================

    _register_negotiator(
        negotiator_registry,
        IAMhaggler,
        short_name=_get_short_name("IAMhaggler"),
        tags=base_tags | {"anac", "anac-2010", "learning", "bayesian"},
    )

    # =========================================================================
    # ANAC 2011 agents
    # =========================================================================

    _register_negotiator(
        negotiator_registry,
        HardHeaded,
        short_name=_get_short_name("HardHeaded"),
        tags=base_tags | {"anac", "anac-2011", "learning", "frequency"},
    )

    _register_negotiator(
        negotiator_registry,
        NiceTitForTat,
        short_name=_get_short_name("NiceTitForTat"),
        tags=base_tags | {"anac", "anac-2011", "tit-for-tat"},
    )

    # =========================================================================
    # ANAC 2012 agents
    # =========================================================================

    _register_negotiator(
        negotiator_registry,
        CUHKAgent,
        short_name=_get_short_name("CUHKAgent"),
        tags=base_tags | {"anac", "anac-2012", "learning", "frequency"},
    )

    # =========================================================================
    # ANAC 2015 agents
    # =========================================================================

    _register_negotiator(
        negotiator_registry,
        Atlas3Agent,
        short_name="Atlas3Agent",
        tags=base_tags | {"anac", "anac-2015", "learning", "frequency"},
    )

    _register_negotiator(
        negotiator_registry,
        ParsAgent,
        short_name=_get_short_name("ParsAgent"),
        tags=base_tags | {"anac", "anac-2015", "learning"},
    )

    _register_negotiator(
        negotiator_registry,
        RandomDance,
        short_name=_get_short_name("RandomDance"),
        tags=base_tags | {"anac", "anac-2015", "random"},
    )

    _register_negotiator(
        negotiator_registry,
        AgentBuyog,
        short_name=_get_short_name("AgentBuyog"),
        tags=base_tags | {"anac", "anac-2015", "learning"},
    )

    _register_negotiator(
        negotiator_registry,
        Kawaii,
        short_name=_get_short_name("Kawaii"),
        tags=base_tags | {"anac", "anac-2015", "learning", "frequency"},
    )

    _register_negotiator(
        negotiator_registry,
        Caduceus2015,
        short_name="Caduceus2015",
        tags=base_tags | {"anac", "anac-2015", "learning"},
    )

    # =========================================================================
    # ANAC 2016 agents
    # =========================================================================

    _register_negotiator(
        negotiator_registry,
        YXAgent,
        short_name=_get_short_name("YXAgent"),
        tags=base_tags | {"anac", "anac-2016", "learning", "frequency"},
    )

    _register_negotiator(
        negotiator_registry,
        ParsCatAgent,
        short_name="ParsCatAgent",
        tags=base_tags | {"anac", "anac-2016", "learning"},
    )

    _register_negotiator(
        negotiator_registry,
        Caduceus,
        short_name=_get_short_name("Caduceus"),
        tags=base_tags | {"anac", "anac-2016", "learning"},
    )

    # =========================================================================
    # ANAC 2017 agents
    # =========================================================================

    _register_negotiator(
        negotiator_registry,
        PonPokoAgent,
        short_name=_get_short_name("PonPokoAgent"),
        tags=base_tags | {"anac", "anac-2017", "learning", "frequency"},
    )

    _register_negotiator(
        negotiator_registry,
        AgentKN,
        short_name=_get_short_name("AgentKN"),
        tags=base_tags | {"anac", "anac-2017", "learning"},
    )

    _register_negotiator(
        negotiator_registry,
        Rubick,
        short_name=_get_short_name("Rubick"),
        tags=base_tags | {"anac", "anac-2017", "learning"},
    )

    # =========================================================================
    # ANAC 2019 agents
    # =========================================================================

    _register_negotiator(
        negotiator_registry,
        AgentGG,
        short_name=_get_short_name("AgentGG"),
        tags=base_tags | {"anac", "anac-2019", "learning", "frequency"},
    )

    _register_negotiator(
        negotiator_registry,
        SAGAAgent,
        short_name="SAGAAgent",
        tags=base_tags | {"anac", "anac-2019", "learning"},
    )

    # =========================================================================
    # ANAC 2022 agents
    # =========================================================================

    _register_negotiator(
        negotiator_registry,
        LuckyAgent2022,
        short_name="LuckyAgent2022",
        tags=base_tags | {"anac", "anac-2022", "learning"},
    )

    # =========================================================================
    # Other competition agents (year uncertain or multi-year)
    # =========================================================================

    _register_negotiator(
        negotiator_registry,
        MICROAgent,
        short_name="MICROAgent",
        tags=base_tags | {"micro", "learning"},
    )

    _register_negotiator(
        negotiator_registry,
        AhBuNeAgent,
        short_name="AhBuNeAgent",
        tags=base_tags | {"learning"},
    )

    _register_negotiator(
        negotiator_registry,
        HybridAgent,
        short_name="HybridAgent",
        tags=base_tags | {"hybrid", "learning"},
    )


# Auto-register when this module is imported
_register_negolog_agents()

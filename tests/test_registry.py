"""
Tests for the registry integration with negmas.

These tests verify that:
1. All negmas-negolog agents are properly registered in the negmas registry
2. Agents can be queried by tags and properties
3. NL-prefixed names correctly avoid conflicts with Genius agents
4. Registry metadata is accurate
"""

import pytest

# Skip all tests if negmas registry is not available
try:
    from negmas.registry import negotiator_registry

    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not REGISTRY_AVAILABLE, reason="negmas registry not available"
)


class TestRegistration:
    """Test that all agents are properly registered."""

    def test_all_agents_registered(self):
        """Verify all 25 negmas-negolog agents are registered."""
        from negmas_negolog import (
            BoulwareAgent,
            ConcederAgent,
            LinearAgent,
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

        # All agents should be registered
        agents = [
            BoulwareAgent,
            ConcederAgent,
            LinearAgent,
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
        ]

        for agent_cls in agents:
            assert negotiator_registry.is_registered(
                agent_cls
            ), f"{agent_cls.__name__} is not registered"

    def test_negolog_tag_count(self):
        """Verify the correct number of agents have the 'negolog' tag."""
        negolog_agents = negotiator_registry.query_by_tag("negolog")
        assert (
            len(negolog_agents) == 25
        ), f"Expected 25 agents, got {len(negolog_agents)}"


class TestNamingConvention:
    """Test the NL-prefix naming convention for conflicting agents."""

    def test_nl_prefixed_agents_exist(self):
        """Agents that conflict with Genius should have NL prefix."""
        nl_prefixed = [
            "NLAgentGG",
            "NLAgentKN",
            "NLAgentBuyog",
            "NLCaduceus",
            "NLCUHKAgent",
            "NLHardHeaded",
            "NLIAMhaggler",
            "NLKawaii",
            "NLNiceTitForTat",
            "NLParsAgent",
            "NLPonPokoAgent",
            "NLRandomDance",
            "NLRubick",
            "NLYXAgent",
        ]

        for name in nl_prefixed:
            infos = negotiator_registry.get_by_short_name(name)
            assert len(infos) > 0, f"{name} not found in registry"
            info = infos[0]
            assert info.has_tag("negolog"), f"{name} missing 'negolog' tag"

    def test_non_conflicting_agents_no_prefix(self):
        """Agents unique to negolog should not have NL prefix."""
        non_prefixed = [
            "Atlas3Agent",
            "BoulwareAgent",
            "ConcederAgent",
            "LinearAgent",
            "Caduceus2015",
            "ParsCatAgent",
            "SAGAAgent",
            "LuckyAgent2022",
            "MICROAgent",
            "AhBuNeAgent",
            "HybridAgent",
        ]

        for name in non_prefixed:
            infos = negotiator_registry.get_by_short_name(name)
            assert len(infos) > 0, f"{name} not found in registry"
            info = infos[0]
            assert info.has_tag("negolog"), f"{name} missing 'negolog' tag"

    def test_genius_vs_negolog_distinction(self):
        """NL-prefixed agents should be distinct from Genius agents."""
        comparisons = [
            ("AgentGG", "NLAgentGG"),
            ("HardHeaded", "NLHardHeaded"),
            ("CUHKAgent", "NLCUHKAgent"),
        ]

        for genius_name, negolog_name in comparisons:
            genius_infos = negotiator_registry.get_by_short_name(genius_name)
            negolog_infos = negotiator_registry.get_by_short_name(negolog_name)

            # Both should exist (but genius may not be available in test env)
            # At minimum, negolog should exist
            assert len(negolog_infos) > 0, f"NegoLog {negolog_name} not found"
            negolog_info = negolog_infos[0]
            assert negolog_info.has_tag(
                "negolog"
            ), f"{negolog_name} missing 'negolog' tag"

            # If genius version exists, they should be different classes
            if len(genius_infos) > 0:
                genius_info = genius_infos[0]
                assert genius_info.cls is not negolog_info.cls
                assert genius_info.has_tag(
                    "genius"
                ), f"{genius_name} missing 'genius' tag"


class TestMetadata:
    """Test that registry metadata is correct."""

    def test_all_negolog_agents_bilateral_only(self):
        """All negolog agents should be marked as bilateral-only via tag."""
        negolog_agents = negotiator_registry.query_by_tag("negolog")

        for name, info in negolog_agents.items():
            assert info.has_tag(
                "bilateral-only"
            ), f"{name} should have 'bilateral-only' tag"

    def test_base_tags_present(self):
        """All negolog agents should have the base tags."""
        base_tags = {"negolog", "sao", "propose", "respond", "bilateral-only"}
        negolog_agents = negotiator_registry.query_by_tag("negolog")

        for name, info in negolog_agents.items():
            for tag in base_tags:
                assert info.has_tag(tag), f"{name} missing '{tag}' tag"

    def test_anac_year_tags(self):
        """ANAC agents should have correct year tags."""
        expected_years = {
            "NLIAMhaggler": "anac-2010",
            "NLHardHeaded": "anac-2011",
            "NLNiceTitForTat": "anac-2011",
            "NLCUHKAgent": "anac-2012",
            "Atlas3Agent": "anac-2015",
            "Caduceus2015": "anac-2015",
            "NLYXAgent": "anac-2016",
            "ParsCatAgent": "anac-2016",
            "NLAgentKN": "anac-2017",
            "NLPonPokoAgent": "anac-2017",
            "NLAgentGG": "anac-2019",
            "SAGAAgent": "anac-2019",
            "LuckyAgent2022": "anac-2022",
        }

        for name, expected_tag in expected_years.items():
            infos = negotiator_registry.get_by_short_name(name)
            assert len(infos) > 0, f"{name} not found"
            info = infos[0]
            assert info.has_tag(
                expected_tag
            ), f"{name} should have tag '{expected_tag}', got tags: {info.tags}"

    def test_time_based_agents_tagged(self):
        """Time-based agents should have the 'time-based' tag."""
        time_based_agents = ["BoulwareAgent", "ConcederAgent", "LinearAgent"]

        for name in time_based_agents:
            infos = negotiator_registry.get_by_short_name(name)
            assert len(infos) > 0, f"{name} not found"
            info = infos[0]
            assert info.has_tag("time-based"), f"{name} missing 'time-based' tag"

    def test_source_is_negolog(self):
        """All negolog agents should have source='negolog'."""
        negolog_agents = negotiator_registry.query_by_tag("negolog")

        for name, info in negolog_agents.items():
            assert (
                info.source == "negolog"
            ), f"{name} should have source='negolog', got '{info.source}'"


class TestQueries:
    """Test registry query functionality with negolog agents."""

    def test_query_by_anac_year_tag(self):
        """Query agents by ANAC year tag."""
        for year in [2010, 2011, 2012, 2015, 2016, 2017, 2019, 2022]:
            year_agents = negotiator_registry.query(tags=["negolog", f"anac-{year}"])
            assert len(year_agents) > 0, f"No negolog agents for ANAC {year}"

            for name, info in year_agents.items():
                assert info.has_tag(f"anac-{year}"), f"{name} missing anac-{year} tag"
                assert info.has_tag("negolog"), f"{name} missing negolog tag"

    def test_query_learning_agents(self):
        """Query agents with learning capability."""
        learning_agents = negotiator_registry.query(tags=["negolog", "learning"])

        # Should find multiple learning agents
        assert len(learning_agents) > 0, "No learning agents found"

        for name, info in learning_agents.items():
            assert info.has_tag("learning"), f"{name} missing 'learning' tag"
            assert info.has_tag("negolog"), f"{name} missing 'negolog' tag"

    def test_query_frequency_based_agents(self):
        """Query agents using frequency-based opponent model."""
        freq_agents = negotiator_registry.query(tags=["negolog", "frequency"])

        expected_freq_agents = [
            "Atlas3Agent",
            "NLAgentGG",
            "NLCUHKAgent",
            "NLHardHeaded",
            "NLKawaii",
            "NLPonPokoAgent",
            "NLYXAgent",
        ]

        found_names = [info.short_name for info in freq_agents.values()]
        for name in expected_freq_agents:
            assert (
                name in found_names
            ), f"{name} should be in frequency-based agents query"

    def test_exclude_genius_query(self):
        """Query negolog agents excluding genius."""
        negolog_only = negotiator_registry.query(
            tags=["negolog"], exclude_tags=["genius"]
        )

        # All results should have negolog tag but not genius
        for name, info in negolog_only.items():
            assert info.has_tag("negolog")
            assert not info.has_tag("genius"), f"{name} should not have genius tag"

    def test_combined_query(self):
        """Test complex combined query."""
        # ANAC agents from 2015-2019 with learning
        results = negotiator_registry.query(tags=["negolog", "anac", "learning"])

        for name, info in results.items():
            assert info.has_tag("negolog")
            assert info.has_tag("anac")
            assert info.has_tag("learning")


class TestGetClass:
    """Test getting actual class objects from registry."""

    def test_get_class_by_name(self):
        """Get agent class by short name."""
        from negmas_negolog import Atlas3Agent

        cls = negotiator_registry.get_class("Atlas3Agent")
        assert cls is Atlas3Agent

    def test_get_class_nl_prefixed(self):
        """Get NL-prefixed agent class."""
        from negmas_negolog import AgentGG

        cls = negotiator_registry.get_class("NLAgentGG")
        assert cls is AgentGG

    def test_get_info_by_class(self):
        """Get registration info by class object."""
        from negmas_negolog import BoulwareAgent

        info = negotiator_registry.get_by_class(BoulwareAgent)
        assert info is not None
        assert info.short_name == "BoulwareAgent"
        assert info.has_tag("negolog")
        assert info.has_tag("time-based")
        assert info.source == "negolog"

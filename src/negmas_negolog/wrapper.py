"""
Wrapper classes to bridge NegoLog negotiating agents to NegMAS SAONegotiator interface.

This module provides the NegologNegotiatorWrapper base class and concrete wrapper
classes for all NegoLog agents. Wrapper classes share the same names as their
NegoLog counterparts for ease of use.
"""

from __future__ import annotations

import sys
from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Type

# Add vendored NegoLog to the path BEFORE any imports that depend on it
NEGOLOG_PATH = Path(__file__).parent.parent.parent / "vendor" / "NegoLog"
if str(NEGOLOG_PATH) not in sys.path:
    sys.path.insert(0, str(NEGOLOG_PATH))

# Import NegoLog types (must be after path is added)
from nenv import Bid, Issue, Preference, Accept  # noqa: E402
from nenv.Agent import AbstractAgent  # noqa: E402
from nenv.OpponentModel.EstimatedPreference import EstimatedPreference  # noqa: E402

# Monkey-patch EstimatedPreference to handle preferences without JSON files
_original_estimated_preference_init = EstimatedPreference.__init__


def _patched_estimated_preference_init(self, reference: Preference):
    """
    Patched __init__ for EstimatedPreference that handles preferences
    without a profile_json_path (i.e., programmatically created preferences).
    """
    # Get profile_json_path, handling None case
    profile_json_path = reference.profile_json_path

    # If profile_json_path is None or empty, we need to manually copy
    # the domain structure from the reference
    if not profile_json_path:
        # Initialize with None to skip file loading
        Preference.__init__(self, profile_json_path=None, generate_bids=False)

        # Copy issues from reference
        self._issues = reference.issues.copy() if hasattr(reference, "_issues") else []

        # Copy and invert weights from reference
        ref_issue_weights = reference.issue_weights
        ref_value_weights = reference.value_weights

        self._issue_weights = {}
        self._value_weights = {}

        for issue in self._issues:
            # Invert issue weight
            self._issue_weights[issue] = 1.0 - ref_issue_weights.get(issue, 0.5)

            # Invert value weights
            self._value_weights[issue] = {}
            ref_vals = ref_value_weights.get(issue, {})
            for value in issue.values:
                self._value_weights[issue][value] = 1.0 - ref_vals.get(value, 0.5)

        self.normalize()
    else:
        # Use original implementation for JSON-based preferences
        _original_estimated_preference_init(self, reference)


EstimatedPreference.__init__ = _patched_estimated_preference_init

from negmas.outcomes import Outcome
from negmas.preferences import BaseUtilityFunction
from negmas.sao.common import ResponseType, SAOState
from negmas.sao.negotiators.base import SAONegotiator

if TYPE_CHECKING:
    from negmas.situated import Agent
    from negmas.negotiators import Controller

__all__ = [
    "NegologNegotiatorWrapper",
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


class NegologPreferenceAdapter(Preference):
    """
    Adapter that wraps a NegMAS utility function to provide NegoLog Preference interface.

    This allows NegoLog agents to use NegMAS utility functions transparently.
    """

    def __init__(
        self,
        ufun: BaseUtilityFunction,
        issues: List[Issue],
        issue_names: List[str],
        reservation_value: float = 0.0,
    ):
        """
        Initialize the preference adapter.

        Args:
            ufun: NegMAS utility function
            issues: List of NegoLog Issue objects
            issue_names: List of issue names (for mapping)
            reservation_value: Reservation value (utility if negotiation fails)
        """
        # Initialize parent without loading from JSON
        super().__init__(profile_json_path=None, generate_bids=False)

        # IMPORTANT: Keep profile_json_path as None (not empty string) so that
        # EstimatedPreference and opponent models don't try to open a file.
        # The parent constructor sets it to "" but we override it here.
        self.profile_json_path = None

        self._ufun = ufun
        self._issues = issues
        self._reservation_value = reservation_value
        self._issue_names = issue_names

        # Build issue weights from the NegMAS ufun if it's a LinearAdditive type
        # This is needed for opponent models that use these weights
        self._issue_weights = {}
        self._value_weights = {}

        # Try to extract weights from the NegMAS ufun
        if hasattr(ufun, "weights") and hasattr(ufun, "values"):
            ufun_weights = ufun.weights
            ufun_values = ufun.values
            for i, issue in enumerate(issues):
                self._issue_weights[issue] = float(ufun_weights[i])
                self._value_weights[issue] = {}
                # ufun_values[i] is a TableFun with a 'mapping' attribute
                val_fun = ufun_values[i]
                if hasattr(val_fun, "mapping"):
                    mapping = val_fun.mapping
                elif callable(val_fun):
                    # Try to call it for each value
                    mapping = {v: val_fun(v) for v in issue.values}
                else:
                    mapping = {}
                for value in issue.values:
                    val_weight = mapping.get(value, 0.5)
                    self._value_weights[issue][value] = float(val_weight)
        else:
            # Fall back to equal weights
            for issue in issues:
                self._issue_weights[issue] = 1.0 / len(issues)
                self._value_weights[issue] = {}
                for value in issue.values:
                    self._value_weights[issue][value] = 0.5

    def get_utility(self, bid: Bid) -> float:
        """
        Calculate utility using the NegMAS ufun.

        Args:
            bid: NegoLog Bid object

        Returns:
            Utility value from the NegMAS ufun
        """
        # Convert NegoLog Bid to NegMAS Outcome (tuple)
        outcome = self._bid_to_outcome(bid)
        return float(self._ufun(outcome))

    def _bid_to_outcome(self, bid: Bid) -> Outcome:
        """Convert a NegoLog Bid to a NegMAS Outcome tuple."""
        values = []
        for issue_name in self._issue_names:
            # Find the issue by name
            for issue in self._issues:
                if issue.name == issue_name:
                    values.append(bid[issue])
                    break
        return tuple(values)

    def _outcome_to_bid(self, outcome: Outcome) -> Bid:
        """Convert a NegMAS Outcome tuple to a NegoLog Bid."""
        content = {}
        for i, issue in enumerate(self._issues):
            content[issue] = outcome[i]
        bid = Bid(content)
        bid.utility = self.get_utility(bid)
        return bid

    @property
    def bids(self) -> List[Bid]:
        """
        Generate all possible bids lazily.

        Returns:
            Sorted list of all possible bids (descending by utility)
        """
        if len(self._bids) > 0:
            return self._bids

        # Generate all bid combinations
        bids = [Bid({}, -1)]

        for issue in self._issues:
            new_bids = []
            for value_name in issue.values:
                for bid in bids:
                    _bid = bid.copy()
                    _bid[issue] = value_name
                    new_bids.append(_bid)
            bids = new_bids

        # Assign utilities and sort
        for bid in bids:
            bid.utility = self.get_utility(bid)

        bids = sorted(bids, reverse=True)
        self._bids = bids

        return bids


class NegologNegotiatorWrapper(SAONegotiator, ABC):
    """
    Base wrapper class that bridges NegoLog agents to NegMAS SAONegotiator.

    This wrapper translates between the two frameworks:
    - Converts NegMAS state/offers to NegoLog format
    - Converts NegoLog actions to NegMAS responses
    - Manages the lifecycle of the wrapped NegoLog agent

    Subclasses should set the `negolog_agent_class` class attribute to the
    NegoLog agent class they wrap.
    """

    # Subclasses must set this to the NegoLog agent class
    negolog_agent_class: Type[AbstractAgent]

    def __init__(
        self,
        preferences: BaseUtilityFunction | None = None,
        ufun: BaseUtilityFunction | None = None,
        name: str | None = None,
        parent: Controller | None = None,
        owner: Agent | None = None,
        id: str | None = None,
        type_name: str | None = None,
        session_time: int = 180,  # Default 3 minutes
        **kwargs,
    ):
        """
        Initialize the wrapper.

        Args:
            preferences: NegMAS preferences/utility function
            ufun: Utility function (overrides preferences if given)
            name: Negotiator name
            parent: Parent controller
            owner: Agent that owns this negotiator
            id: Unique identifier
            type_name: Type name for serialization
            session_time: Session time in seconds for NegoLog agent
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(
            preferences=preferences,
            ufun=ufun,
            name=name,
            parent=parent,
            owner=owner,
            id=id,
            type_name=type_name,
            **kwargs,
        )

        self._session_time = session_time
        self._negolog_agent: Optional[AbstractAgent] = None
        self._preference_adapter: Optional[NegologPreferenceAdapter] = None
        self._issues: List[Issue] = []
        self._issue_names: List[str] = []
        self._initialized = False
        self._step_count = 0

    def on_negotiation_start(self, state: SAOState) -> None:
        """
        Called when negotiation starts. Initialize the NegoLog agent.

        Args:
            state: Initial negotiation state
        """
        super().on_negotiation_start(state)
        self._initialize_negolog_agent()

    def _initialize_negolog_agent(self) -> None:
        """Initialize the wrapped NegoLog agent with the current negotiation context."""
        if self._initialized:
            return

        if not self.ufun:
            raise ValueError("Utility function must be set before negotiation starts")

        if not self.nmi:
            raise ValueError("NMI must be available before negotiation starts")

        # Build NegoLog Issues from NegMAS outcome space
        outcome_space = self.nmi.outcome_space
        if hasattr(outcome_space, "issues"):
            negmas_issues = outcome_space.issues
        else:
            raise ValueError("Outcome space must have issues defined")

        self._issues = []
        self._issue_names = []

        for i, negmas_issue in enumerate(negmas_issues):
            issue_name = getattr(negmas_issue, "name", f"issue_{i}")
            self._issue_names.append(issue_name)

            # Get all possible values for this issue
            if hasattr(negmas_issue, "all"):
                values = list(negmas_issue.all)
            elif hasattr(negmas_issue, "values"):
                values = list(negmas_issue.values)
            else:
                # Try to enumerate
                values = list(negmas_issue)

            # Convert values to strings if needed
            values = [str(v) if not isinstance(v, str) else v for v in values]

            negolog_issue = Issue(issue_name, values)
            self._issues.append(negolog_issue)

        # Create preference adapter
        reservation_value = getattr(self.ufun, "reserved_value", 0.0)
        if reservation_value == float("-inf"):
            reservation_value = 0.0

        self._preference_adapter = NegologPreferenceAdapter(
            ufun=self.ufun,
            issues=self._issues,
            issue_names=self._issue_names,
            reservation_value=reservation_value,
        )

        # Create the NegoLog agent
        self._negolog_agent = self.negolog_agent_class(
            preference=self._preference_adapter,
            session_time=self._session_time,
            estimators=[],  # No opponent models by default
        )

        # Initialize the agent
        self._negolog_agent.initiate(opponent_name=None)
        self._initialized = True
        self._step_count = 0

    def _get_relative_time(self, state: SAOState) -> float:
        """
        Get the relative time (0 to 1) for the NegoLog agent.

        Args:
            state: Current negotiation state

        Returns:
            Relative time between 0 and 1
        """
        return state.relative_time

    def _outcome_to_bid(self, outcome: Outcome) -> Bid:
        """Convert a NegMAS Outcome to a NegoLog Bid."""
        if self._preference_adapter is None:
            raise ValueError("Preference adapter not initialized")
        return self._preference_adapter._outcome_to_bid(outcome)

    def _bid_to_outcome(self, bid: Bid) -> Outcome:
        """Convert a NegoLog Bid to a NegMAS Outcome."""
        if self._preference_adapter is None:
            raise ValueError("Preference adapter not initialized")
        return self._preference_adapter._bid_to_outcome(bid)

    def propose(self, state: SAOState, dest: str | None = None) -> Outcome | None:
        """
        Generate a proposal using the wrapped NegoLog agent.

        Args:
            state: Current negotiation state
            dest: Destination negotiator ID (ignored)

        Returns:
            Outcome tuple to propose, or None
        """
        if not self._initialized:
            self._initialize_negolog_agent()

        if self._negolog_agent is None:
            return None

        t = self._get_relative_time(state)

        # Get action from NegoLog agent
        action = self._negolog_agent.act(t)

        if action is None:
            return None

        # Convert NegoLog bid to NegMAS outcome
        return self._bid_to_outcome(action.bid)

    def respond(self, state: SAOState, source: str | None = None) -> ResponseType:
        """
        Respond to an offer using the wrapped NegoLog agent.

        Args:
            state: Current negotiation state (access offer via state.current_offer)
            source: ID of negotiator who made the offer

        Returns:
            ResponseType indicating acceptance/rejection
        """
        if not self._initialized:
            self._initialize_negolog_agent()

        if self._negolog_agent is None:
            return ResponseType.REJECT_OFFER

        offer = state.current_offer
        if offer is None:
            return ResponseType.REJECT_OFFER

        t = self._get_relative_time(state)

        # Convert offer to NegoLog bid and notify agent
        bid = self._outcome_to_bid(offer)
        self._negolog_agent.receive_bid(bid, t)

        # Get action from NegoLog agent
        action = self._negolog_agent.act(t)

        if action is None:
            return ResponseType.REJECT_OFFER

        # Check if action is Accept
        if isinstance(action, Accept):
            return ResponseType.ACCEPT_OFFER

        return ResponseType.REJECT_OFFER

    def on_negotiation_end(self, state: SAOState) -> None:
        """
        Called when negotiation ends. Clean up the NegoLog agent.

        Args:
            state: Final negotiation state
        """
        super().on_negotiation_end(state)

        if self._negolog_agent is not None:
            is_accept = state.agreement is not None
            t = self._get_relative_time(state)
            self._negolog_agent.terminate(is_accept, "opponent", t)

        # Reset state
        self._negolog_agent = None
        self._preference_adapter = None
        self._initialized = False


# =============================================================================
# Concrete Wrapper Classes for NegoLog Agents
# =============================================================================

# Import NegoLog agents (with correct module and class names)
# Aliased with _NL suffix to avoid naming conflicts with wrapper classes
from agents.boulware.Boulware import BoulwareAgent as _NLBoulwareAgent
from agents.conceder.Conceder import ConcederAgent as _NLConcederAgent
from agents.LinearAgent.LinearAgent import LinearAgent as _NLLinearAgent
from agents.MICRO.MICRO import MICROAgent as _NLMICROAgent
from agents.Atlas3.Atlas3Agent import Atlas3Agent as _NLAtlas3Agent
from agents.NiceTitForTat.NiceTitForTat import NiceTitForTat as _NLNiceTitForTat
from agents.YXAgent.YXAgent import YXAgent as _NLYXAgent
from agents.ParsCat.ParsCat import ParsCatAgent as _NLParsCatAgent
from agents.PonPoko.PonPoko import PonPokoAgent as _NLPonPokoAgent
from agents.AgentGG.AgentGG import AgentGG as _NLAgentGG
from agents.SAGA.SAGAAgent import SAGAAgent as _NLSAGAAgent
from agents.CUHKAgent.CUHKAgent import CUHKAgent as _NLCUHKAgent
from agents.AgentKN.AgentKN import AgentKN as _NLAgentKN
from agents.Rubick.Rubick import Rubick as _NLRubick
from agents.AhBuNeAgent.AhBuNeAgent import AhBuNeAgent as _NLAhBuNeAgent
from agents.ParsAgent.ParsAgent import ParsAgent as _NLParsAgent
from agents.RandomDance.RandomDance import RandomDance as _NLRandomDance
from agents.AgentBuyog.AgentBuyog import AgentBuyog as _NLAgentBuyog
from agents.Kawaii.Kawaii import Kawaii as _NLKawaii
from agents.Caduceus2015.Caduceus import Caduceus2015 as _NLCaduceus2015
from agents.Caduceus.Caduceus import Caduceus as _NLCaduceus
from agents.HardHeaded.KLH import HardHeaded as _NLHardHeaded
from agents.IAMhaggler.IAMhaggler import IAMhaggler as _NLIAMhaggler
from agents.LuckyAgent2022.LuckyAgent2022 import LuckyAgent2022 as _NLLuckyAgent2022
from agents.HybridAgent.HybridAgent import HybridAgent as _NLHybridAgent


class BoulwareAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's BoulwareAgent.

    Time-based concession agent that concedes slowly (sub-linearly).
    Uses Bezier curve-based target utility calculation.
    """

    negolog_agent_class = _NLBoulwareAgent


class ConcederAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's ConcederAgent.

    Time-based concession agent that concedes quickly (super-linearly).
    """

    negolog_agent_class = _NLConcederAgent


class LinearAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's LinearAgent.

    Time-based concession agent that concedes linearly.
    """

    negolog_agent_class = _NLLinearAgent


class MICROAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's MICROAgent.

    ANAC competition agent using opponent modeling.
    """

    negolog_agent_class = _NLMICROAgent


class Atlas3Agent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's Atlas3Agent.

    ANAC 2015 competition winner agent.
    """

    negolog_agent_class = _NLAtlas3Agent


class NiceTitForTat(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's NiceTitForTat agent.

    Plays tit-for-tat strategy with respect to utility,
    aiming for the Nash point. Uses Bayesian opponent modeling.
    """

    negolog_agent_class = _NLNiceTitForTat


class YXAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's YXAgent.

    ANAC competition agent.
    """

    negolog_agent_class = _NLYXAgent


class ParsCatAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's ParsCatAgent.

    ANAC competition agent from Amirkabir University.
    """

    negolog_agent_class = _NLParsCatAgent


class PonPokoAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's PonPokoAgent.

    ANAC competition agent.
    """

    negolog_agent_class = _NLPonPokoAgent


class AgentGG(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's AgentGG.

    ANAC competition agent.
    """

    negolog_agent_class = _NLAgentGG


class SAGAAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's SAGAAgent.

    Uses genetic algorithm for bid selection.
    """

    negolog_agent_class = _NLSAGAAgent


class CUHKAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's CUHKAgent.

    ANAC competition agent from Chinese University of Hong Kong.
    """

    negolog_agent_class = _NLCUHKAgent


class AgentKN(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's AgentKN.

    ANAC competition agent.
    """

    negolog_agent_class = _NLAgentKN


class Rubick(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's Rubick agent.

    ANAC competition agent.
    """

    negolog_agent_class = _NLRubick


class AhBuNeAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's AhBuNeAgent.

    ANAC competition agent.
    """

    negolog_agent_class = _NLAhBuNeAgent


class ParsAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's ParsAgent.

    ANAC competition agent from Amirkabir University.
    """

    negolog_agent_class = _NLParsAgent


class RandomDance(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's RandomDance agent.

    ANAC competition agent.
    """

    negolog_agent_class = _NLRandomDance


class AgentBuyog(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's AgentBuyog.

    ANAC competition agent.
    """

    negolog_agent_class = _NLAgentBuyog


class Kawaii(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's Kawaii agent.

    ANAC competition agent.
    """

    negolog_agent_class = _NLKawaii


class Caduceus2015(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's Caduceus2015 agent.

    ANAC 2015 competition agent.
    """

    negolog_agent_class = _NLCaduceus2015


class Caduceus(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's Caduceus agent.

    ANAC competition agent.
    """

    negolog_agent_class = _NLCaduceus


class HardHeaded(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's HardHeaded agent.

    ANAC 2011 competition winner. Uses frequency-based opponent modeling.
    """

    negolog_agent_class = _NLHardHeaded


class IAMhaggler(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's IAMhaggler agent.

    ANAC competition agent from University of Southampton.
    """

    negolog_agent_class = _NLIAMhaggler


class LuckyAgent2022(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's LuckyAgent2022.

    ANAC 2022 competition agent.
    """

    negolog_agent_class = _NLLuckyAgent2022


class HybridAgent(NegologNegotiatorWrapper):
    """
    NegMAS wrapper for NegoLog's HybridAgent.

    Agent that combines multiple negotiation strategies.
    """

    negolog_agent_class = _NLHybridAgent

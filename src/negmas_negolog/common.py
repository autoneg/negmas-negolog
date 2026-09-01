"""
Common classes and utilities for bridging NegoLog agents to NegMAS.

This module provides:
- NegologPreferenceAdapter: Adapts NegMAS utility functions to NegoLog Preference interface
- NegologNegotiatorWrapper: Base class for all NegoLog agent wrappers
"""

from __future__ import annotations

import sys
from abc import ABC
from array import array
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Type

# Add vendored NegoLog to the path BEFORE any imports that depend on it.
# The NegoLog framework (top-level ``nenv`` and ``agents`` packages) is bundled
# INSIDE this package at ``_vendor/NegoLog`` so it ships in the built wheel and
# resolves identically in both editable and installed (PyPI) modes.
NEGOLOG_PATH = Path(__file__).parent / "_vendor" / "NegoLog"
if str(NEGOLOG_PATH) not in sys.path:
    sys.path.insert(0, str(NEGOLOG_PATH))

# Import NegoLog types (must be after path is added)
from nenv import Bid, Issue, Preference, Accept  # noqa: E402
from nenv.Agent import AbstractAgent  # noqa: E402

from negmas.outcomes import Outcome  # noqa: E402
from negmas.preferences import BaseUtilityFunction  # noqa: E402
from negmas.sao.common import ResponseType, SAOState  # noqa: E402
from negmas.sao.negotiators.base import SAONegotiator  # noqa: E402

if TYPE_CHECKING:
    from negmas.situated import Agent
    from negmas.negotiators import Controller

__all__ = [
    "NegologPreferenceAdapter",
    "NegologNegotiatorWrapper",
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
        native_values: dict[str, list] | None = None,
    ):
        """
        Initialize the preference adapter.

        Args:
            ufun: NegMAS utility function
            issues: List of NegoLog Issue objects
            issue_names: List of issue names (for mapping)
            reservation_value: Reservation value (utility if negotiation fails)
            native_values: Per-issue-name list of the *NegMAS* values, in the same
                order as the corresponding NegoLog issue's (stringified) values.
                NegoLog issues can only hold strings, so without this the adapter
                would hand strings to a NegMAS value function or use them as
                outcome elements -- which silently breaks every issue whose values
                are not strings (any integer/contiguous issue, for instance).
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
        # str -> native and native -> str, per issue name. Falls back to identity
        # when the caller did not supply the NegMAS values (the values are then
        # already strings, which is the only case the old code handled).
        self._to_native: dict[str, dict] = {}
        self._to_negolog: dict[str, dict] = {}
        # name -> Issue object, first occurrence wins (same as the linear scan it
        # replaces in ``_bid_to_outcome``, which is on the per-round hot path).
        self._issue_by_name: dict[str, Issue] = {}
        for issue in issues:
            self._issue_by_name.setdefault(issue.name, issue)
            natives = (native_values or {}).get(issue.name, list(issue.values))
            self._to_native[issue.name] = dict(zip(issue.values, natives))
            self._to_negolog[issue.name] = {
                n: v for v, n in zip(issue.values, natives)
            }

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
                # A TableFun exposes its `mapping`; anything else (AffineFun,
                # LambdaFun, ...) has to be called. Either way it is keyed by /
                # called with the *NegMAS* value, never the NegoLog string.
                val_fun = ufun_values[i]
                table = getattr(val_fun, "mapping", None)
                for value in issue.values:
                    native = self._to_native[issue.name].get(value, value)
                    if table is not None:
                        val_weight = table.get(native, table.get(value, 0.5))
                    elif callable(val_fun):
                        try:
                            val_weight = val_fun(native)
                        except Exception:
                            val_weight = 0.5
                    else:
                        val_weight = 0.5
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
        """Convert a NegoLog Bid to a NegMAS Outcome tuple.

        NegoLog values are always strings, so they are mapped back to the NegMAS
        values here. Skipping that step yields an outcome like ``("1", "5")`` for
        an integer-valued domain, which is not a member of the outcome space at
        all -- the utility function and the mechanism both reject it.
        """
        values = []
        for issue_name in self._issue_names:
            issue = self._issue_by_name.get(issue_name)
            if issue is None:
                continue
            value = bid[issue]
            values.append(self._to_native[issue_name].get(value, value))
        return tuple(values)

    def _outcome_to_bid(self, outcome: Outcome) -> Bid:
        """Convert a NegMAS Outcome tuple to a NegoLog Bid."""
        content = {}
        for i, issue in enumerate(self._issues):
            value = outcome[i]
            content[issue] = self._to_negolog[issue.name].get(value, value)
        bid = Bid(content)
        bid.utility = self.get_utility(bid)
        return bid

    def _reuse_allowed(self) -> bool:
        """Whether one utility per outcome may be computed once and reused.

        Ruled out by a non-stationary (e.g. discounted) ufun, which has no single
        utility per outcome, and by a ufun that reports itself as modified. The
        ``modified`` flag is newer than ``invert()``; where it is missing the ufun
        is treated as unmodified, which is exactly what NegMAS' own inverter cache
        on the ufun already assumes.
        """
        if getattr(self._ufun, "modified", False):
            return False
        is_stationary = getattr(self._ufun, "is_stationary", None)
        if not callable(is_stationary):
            return True
        try:
            return bool(is_stationary())
        except Exception:
            return False

    def _existing_inverse(self):
        """A NegMAS inverse of this ufun that exists *without* building one.

        Deliberately does not force construction: an inverter presorts the whole
        outcome space itself, so building one merely to read its utilities would
        cost more than evaluating the ufun directly. It is worth reading when
        someone has already paid for it --

        - a ufun already carrying a memoized inverter (``invert()`` caches on the
          ufun, so another negotiator, an earlier negotiation, or the caller may
          have built it), or
        - a saved inverse on disk attached by ``Scenario.load``, which is the
          expensive-to-construct case the NegMAS-side cache exists for.

        Returns ``None`` on anything else, and on any version of NegMAS whose
        ``invert()`` does not expose these internals.
        """
        try:
            from negmas.preferences.inv_ufun import PresortingInverseUtilityFunction
        except ImportError:
            return None

        cached = getattr(self._ufun, "_cached_inverse", None)
        if cached is not None:
            # Only the presorting family holds raw per-outcome utilities in
            # ``outcomes``/``utils``; another inverter could expose same-named
            # arrays meaning something else (normalized, sampled, partial).
            return (
                cached
                if isinstance(cached, PresortingInverseUtilityFunction)
                else None
            )
        if getattr(self._ufun, "_inverse_cache_name", None) is None:
            return None
        try:
            return self._ufun.invert(PresortingInverseUtilityFunction)
        except Exception:
            return None

    def _inverse_utilities(self) -> dict | None:
        """``{outcome: utility}`` for the whole outcome space, via the NegMAS inverse.

        A presorting inverter has already evaluated the ufun over every outcome,
        so when one is available (see ``_existing_inverse``) its utilities are
        reused instead of evaluating the ufun a second time.

        Only the *utilities* are taken from the inverter; the bid order is still
        produced by the enumeration in ``bids`` below, so switching the source of
        the numbers cannot reorder equal-utility bids.

        Returns ``None`` (fall back to direct evaluation) whenever no inverse is
        at hand, it does not expose its presorted arrays, or it would not cover
        the outcome space exactly -- e.g. a continuous issue that ``to_discrete``
        subsamples to fewer levels than the NegoLog issue holds.
        """
        if not self._reuse_allowed():
            return None
        inverse = self._existing_inverse()
        if inverse is None:
            return None

        outcomes = getattr(inverse, "outcomes", None)
        utils = getattr(inverse, "utils", None)
        if not outcomes or utils is None or len(outcomes) != len(utils):
            return None

        expected = 1
        for issue in self._issues:
            expected *= len(issue.values)
        try:
            table = {tuple(o): float(u) for o, u in zip(outcomes, utils)}
        except TypeError:
            # Unhashable outcome values.
            return None
        if len(table) != expected:
            return None
        return table

    def _domain_signature(self) -> tuple:
        """Identifies the domain the presorted order belongs to.

        Covers the NegMAS values as well as the NegoLog strings: the strings fix
        the enumeration the cached order indexes into, and the NegMAS values fix
        the utilities. Two adapters over one ufun whose values merely *stringify*
        the same (``[0, 1]`` vs ``["0", "1"]``) must not share a cache entry.
        """
        return tuple(
            (
                issue.name,
                tuple(issue.values),
                tuple(repr(v) for v in self._to_native[issue.name].values()),
            )
            for issue in self._issues
        )

    def _enumerate_bids(self) -> List[Bid]:
        """Every bid in the domain, in NegoLog's own enumeration order (unsorted)."""
        bids = [Bid({}, -1)]

        for issue in self._issues:
            new_bids = []
            for value_name in issue.values:
                for bid in bids:
                    _bid = bid.copy()
                    _bid[issue] = value_name
                    new_bids.append(_bid)
            bids = new_bids

        return bids

    def _cached_presorted(self):
        """The presorted order previously computed for this ufun, or ``None``.

        Stashed on the ufun (not on the adapter) because the wrapper creates a
        fresh adapter per negotiation, while the ufun typically outlives all of
        them -- so a tournament pays the evaluate-and-sort cost once per ufun
        instead of once per negotiation. See ``_reuse_allowed``.
        """
        if not self._reuse_allowed():
            return None
        cache = getattr(self._ufun, "_negolog_presorted", None)
        if not isinstance(cache, dict):
            return None
        return cache.get(self._domain_signature())

    def _store_presorted(self, order, utils) -> None:
        """Records the presorted order against this ufun. Best-effort.

        Stored as two flat arrays -- a permutation of the enumeration and the
        utility of each enumerated bid -- rather than as outcomes or Bid objects:
        16 bytes per outcome (512KB for a 32768-outcome domain) instead of the
        few hundred a list of outcome tuples would cost. Worth the care because
        this is retained for the ufun's whole lifetime, where the per-negotiation
        bid list it replaces was garbage once the negotiation ended.
        """
        if not self._reuse_allowed():
            return
        cache = getattr(self._ufun, "_negolog_presorted", None)
        if not isinstance(cache, dict):
            cache = {}
            try:
                object.__setattr__(self._ufun, "_negolog_presorted", cache)
            except Exception:
                return
        try:
            cache[self._domain_signature()] = (
                array("l", order),
                array("d", utils),
            )
        except (TypeError, OverflowError, ValueError):
            return

    def _bids_from_presorted(self, presorted) -> List[Bid] | None:
        """Rebuilds the sorted bid list from a cached order.

        Re-runs the (cheap) enumeration and applies the recorded permutation and
        utilities, skipping the ufun evaluations and the sort. Bid objects are
        rebuilt rather than shared: NegoLog agents hand the very objects from this
        list around and some mutate them in place, so reusing them across
        negotiations would leak state between sessions.

        Returns ``None`` if the entry no longer matches the ufun, in which case
        ``bids`` recomputes and overwrites it.
        """
        order, utils = presorted
        bids = self._enumerate_bids()
        n = len(bids)
        if n != len(order) or n != len(utils):
            return None

        # The entry outlives the adapter, so re-check a few utilities against the
        # live ufun before trusting it: a ufun rescaled or normalized between
        # negotiations (``Scenario.normalize()`` and friends) would otherwise be
        # served stale numbers. Four evaluations rather than ``n``, and unlike the
        # ``modified`` flag -- which older NegMAS releases do not have -- this
        # works on every version. The comparison is exact because ``array("d")``
        # round-trips a Python float losslessly.
        for i in sorted({0, n // 3, (2 * n) // 3, n - 1}):
            if utils[i] != float(self._ufun(self._bid_to_outcome(bids[i]))):
                return None

        for i, bid in enumerate(bids):
            bid.utility = utils[i]
        return [bids[i] for i in order]

    @property
    def bids(self) -> List[Bid]:
        """
        Generate all possible bids lazily.

        Returns:
            Sorted list of all possible bids (descending by utility)
        """
        if len(self._bids) > 0:
            return self._bids

        # Reuse the order computed for this ufun in an earlier negotiation, if any.
        presorted = self._cached_presorted()
        if presorted is not None:
            bids = self._bids_from_presorted(presorted)
            if bids is not None:
                self._bids = bids
                return bids

        # Generate all bid combinations
        bids = self._enumerate_bids()

        # Assign utilities. They come from an already-built NegMAS inverse when
        # one covers the space, and from the ufun directly otherwise (which is
        # what ``get_utility`` does, inlined here to convert each bid once).
        table = self._inverse_utilities()
        for bid in bids:
            outcome = self._bid_to_outcome(bid)
            util = None if table is None else table.get(outcome)
            bid.utility = float(self._ufun(outcome)) if util is None else util

        # Sorting the *indices* by bid is the same stable, utility-only
        # comparison as sorting the bids directly, so equal-utility bids keep
        # their enumeration order -- and it yields the permutation to cache.
        order = sorted(range(len(bids)), key=bids.__getitem__, reverse=True)
        self._store_presorted(order, [bid.utility for bid in bids])
        bids = [bids[i] for i in order]
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
        # Track the current negotiation step and cache act() results
        # This prevents calling act() multiple times per step (which corrupts
        # agent state for agents like AgentBuyog that increment round counters in act())
        self._current_step: int = -1
        self._cached_action = None

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
        native_values: dict[str, list] = {}

        for i, negmas_issue in enumerate(negmas_issues):
            issue_name = getattr(negmas_issue, "name", f"issue_{i}")
            self._issue_names.append(issue_name)

            # Get all possible values for this issue. `.all` enumerates a discrete
            # issue; `.values` is only a (min, max) pair for a contiguous one, so
            # it must not be preferred over `.all`.
            if hasattr(negmas_issue, "all"):
                values = list(negmas_issue.all)
            elif hasattr(negmas_issue, "values"):
                values = list(negmas_issue.values)
            else:
                # Try to enumerate
                values = list(negmas_issue)

            # NegoLog issues hold strings, so keep the NegMAS values alongside
            # them to translate back (see NegologPreferenceAdapter).
            native_values[issue_name] = values
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
            native_values=native_values,
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
        self._current_step = -1
        self._cached_action = None

    def _get_relative_time(self, state: SAOState) -> float:
        """
        Get the relative time (0 to 1) for the NegoLog agent.

        Args:
            state: Current negotiation state

        Returns:
            Relative time between 0 and 1
        """
        return state.relative_time

    def _get_action_for_step(self, state: SAOState):
        """
        Get the NegoLog action for the current step, with caching.

        This method ensures act() is only called once per negotiation step,
        which is critical because some NegoLog agents (like AgentBuyog) maintain
        internal round counters that increment on each act() call.

        Args:
            state: Current negotiation state

        Returns:
            The cached or newly computed action from the NegoLog agent
        """
        current_step = state.step
        if current_step != self._current_step:
            # New step - call act() and cache the result
            self._current_step = current_step
            t = self._get_relative_time(state)
            self._cached_action = self._negolog_agent.act(t)
        return self._cached_action

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

        # Get action (cached per step to avoid multiple act() calls)
        action = self._get_action_for_step(state)

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

        # Invalidate the cached action since we received a new bid
        # The agent may now decide differently (e.g., to accept)
        self._current_step = -1
        self._cached_action = None

        # Get action from NegoLog agent (will be cached for this step)
        action = self._get_action_for_step(state)

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

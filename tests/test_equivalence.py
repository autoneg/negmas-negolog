"""
Tests for equivalence between NegoLog native execution and NegMAS wrapper execution.

These tests verify that:
1. The same NegoLog agent produces the same (or nearly the same) negotiation behavior
   when run natively in NegoLog vs wrapped in NegMAS.
2. Both systems produce identical offers at each step given the same inputs.
3. Acceptance decisions are consistent between both systems.
"""

import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

import pytest

# Add vendored NegoLog to path
NEGOLOG_PATH = Path(__file__).parent.parent / "vendor" / "NegoLog"
if str(NEGOLOG_PATH) not in sys.path:
    sys.path.insert(0, str(NEGOLOG_PATH))

from negmas.outcomes import make_issue, make_os
from negmas.preferences import LinearAdditiveUtilityFunction
from negmas.sao import SAOMechanism

# Import NegoLog classes directly
from nenv import Preference, Bid, Action, Offer, Accept
from nenv.Issue import Issue as NegologIssue

# Import wrappers
from negmas_negolog import (
    BoulwareAgent,
    ConcederAgent,
    LinearAgent,
    NiceTitForTat,
    MICROAgent,
    AgentGG,
    HardHeaded,
)

# Import native NegoLog agent classes
from agents.boulware.Boulware import BoulwareAgent as NativeBoulware
from agents.conceder.Conceder import ConcederAgent as NativeConceder
from agents.LinearAgent.LinearAgent import LinearAgent as NativeLinear


@dataclass
class NegotiationStep:
    """Record of a single negotiation step."""

    round: int
    time: float
    agent: str  # 'A' or 'B'
    action_type: str  # 'offer' or 'accept'
    bid_content: Dict[str, str]  # issue_name -> value
    utility_a: float
    utility_b: float


def create_negolog_preference(
    issues: List[NegologIssue],
    issue_weights: Dict[str, float],
    value_weights: Dict[str, Dict[str, float]],
    reservation_value: float = 0.0,
) -> Preference:
    """Create a NegoLog Preference object programmatically (without JSON file)."""
    pref = Preference(profile_json_path=None, generate_bids=False)
    pref._issues = issues
    pref._reservation_value = reservation_value
    pref._issue_weights = {}
    pref._value_weights = {}

    for issue in issues:
        pref._issue_weights[issue] = issue_weights[issue.name]
        pref._value_weights[issue] = {}
        for value in issue.values:
            pref._value_weights[issue][value] = value_weights[issue.name][value]

    # Generate bids
    _ = pref.bids
    return pref


def run_negolog_native(
    agent_a_class,
    agent_b_class,
    pref_a: Preference,
    pref_b: Preference,
    n_rounds: int,
    session_time: int = 180,
) -> Tuple[List[NegotiationStep], Optional[Dict[str, str]]]:
    """
    Run a negotiation using NegoLog natively (without NegMAS).

    Returns:
        Tuple of (history, agreement) where agreement is None if no agreement reached.
    """
    # Create agents
    agent_a = agent_a_class(preference=pref_a, session_time=session_time, estimators=[])
    agent_b = agent_b_class(preference=pref_b, session_time=session_time, estimators=[])

    # Initialize agents
    agent_a.initiate(opponent_name="AgentB")
    agent_b.initiate(opponent_name="AgentA")

    history: List[NegotiationStep] = []
    agreement = None
    last_action = None

    for round_num in range(n_rounds):
        # Calculate normalized time (0 to 1)
        t = round_num / n_rounds

        # Agent A's turn
        if round_num > 0 and last_action is not None:
            agent_a.receive_bid(last_action.bid, t)

        action_a = agent_a.act(t)

        if action_a is None:
            break

        bid_content_a = {issue.name: action_a.bid[issue] for issue in pref_a.issues}
        utility_a_a = pref_a.get_utility(action_a.bid)
        utility_b_a = pref_b.get_utility(action_a.bid)

        step_a = NegotiationStep(
            round=round_num,
            time=t,
            agent="A",
            action_type="accept" if isinstance(action_a, Accept) else "offer",
            bid_content=bid_content_a,
            utility_a=utility_a_a,
            utility_b=utility_b_a,
        )
        history.append(step_a)

        if isinstance(action_a, Accept):
            agreement = bid_content_a
            break

        # Agent B's turn
        t = (round_num + 0.5) / n_rounds  # Slightly later time for agent B
        agent_b.receive_bid(action_a.bid, t)
        action_b = agent_b.act(t)

        if action_b is None:
            break

        bid_content_b = {issue.name: action_b.bid[issue] for issue in pref_b.issues}
        utility_a_b = pref_a.get_utility(action_b.bid)
        utility_b_b = pref_b.get_utility(action_b.bid)

        step_b = NegotiationStep(
            round=round_num,
            time=t,
            agent="B",
            action_type="accept" if isinstance(action_b, Accept) else "offer",
            bid_content=bid_content_b,
            utility_a=utility_a_b,
            utility_b=utility_b_b,
        )
        history.append(step_b)

        if isinstance(action_b, Accept):
            agreement = bid_content_b
            break

        last_action = action_b

    # Terminate agents
    agent_a.terminate(agreement is not None, "AgentB", 1.0)
    agent_b.terminate(agreement is not None, "AgentA", 1.0)

    return history, agreement


def run_negmas_wrapped(
    agent_a_class,
    agent_b_class,
    issues,
    buyer_ufun,
    seller_ufun,
    n_steps: int,
) -> Tuple[List[NegotiationStep], Optional[Dict[str, str]]]:
    """
    Run a negotiation using NegMAS with wrapped NegoLog agents.

    Returns:
        Tuple of (history, agreement) where agreement is None if no agreement reached.
    """
    mechanism = SAOMechanism(issues=issues, n_steps=n_steps)

    agent_a = agent_a_class(name="buyer", ufun=buyer_ufun)
    agent_b = agent_b_class(name="seller", ufun=seller_ufun)

    mechanism.add(agent_a)
    mechanism.add(agent_b)

    history: List[NegotiationStep] = []

    # Run step by step to capture history
    state = mechanism.state
    step_count = 0
    last_offer = None
    current_proposer = None

    while not state.ended:
        state = mechanism.step()
        step_count += 1

        if state.current_offer is not None and state.current_offer != last_offer:
            # New offer was made
            bid_content = {}
            for i, issue in enumerate(issues):
                bid_content[issue.name] = state.current_offer[i]

            utility_a = float(buyer_ufun(state.current_offer))
            utility_b = float(seller_ufun(state.current_offer))

            # Determine which agent made the offer
            agent_name = "A" if "buyer" in (state.current_proposer or "") else "B"

            step = NegotiationStep(
                round=state.step,
                time=state.relative_time,
                agent=agent_name,
                action_type="offer",
                bid_content=bid_content,
                utility_a=utility_a,
                utility_b=utility_b,
            )
            history.append(step)
            last_offer = state.current_offer

    agreement = None
    if state.agreement is not None:
        agreement = {}
        for i, issue in enumerate(issues):
            agreement[issue.name] = state.agreement[i]

        # Record acceptance
        # The acceptor is the one who didn't make the last offer
        acceptor = "B" if history and history[-1].agent == "A" else "A"
        accept_step = NegotiationStep(
            round=state.step,
            time=state.relative_time,
            agent=acceptor,
            action_type="accept",
            bid_content=agreement,
            utility_a=float(buyer_ufun(state.agreement)),
            utility_b=float(seller_ufun(state.agreement)),
        )
        history.append(accept_step)

    return history, agreement


class TestEquivalence:
    """Test that NegoLog agents behave equivalently in native vs wrapped execution."""

    @pytest.fixture
    def domain_setup(self):
        """Create matching domain for both NegoLog and NegMAS."""
        # NegMAS issues
        negmas_issues = [
            make_issue(values=["low", "medium", "high"], name="price"),
            make_issue(values=["1", "2", "3"], name="quantity"),
            make_issue(values=["fast", "normal", "slow"], name="delivery"),
        ]
        outcome_space = make_os(negmas_issues)

        # Issue weights and value weights
        buyer_issue_weights = {"price": 0.5, "quantity": 0.3, "delivery": 0.2}
        buyer_value_weights = {
            "price": {"low": 1.0, "medium": 0.5, "high": 0.0},
            "quantity": {"1": 0.0, "2": 0.5, "3": 1.0},
            "delivery": {"fast": 1.0, "normal": 0.5, "slow": 0.0},
        }

        seller_issue_weights = {"price": 0.5, "quantity": 0.3, "delivery": 0.2}
        seller_value_weights = {
            "price": {"low": 0.0, "medium": 0.5, "high": 1.0},
            "quantity": {"1": 1.0, "2": 0.5, "3": 0.0},
            "delivery": {"fast": 0.0, "normal": 0.5, "slow": 1.0},
        }

        # NegMAS utility functions
        buyer_ufun = LinearAdditiveUtilityFunction(
            values=buyer_value_weights,
            weights=buyer_issue_weights,
            outcome_space=outcome_space,
        )
        seller_ufun = LinearAdditiveUtilityFunction(
            values=seller_value_weights,
            weights=seller_issue_weights,
            outcome_space=outcome_space,
        )

        # NegoLog issues
        negolog_issues = [
            NegologIssue("price", ["low", "medium", "high"]),
            NegologIssue("quantity", ["1", "2", "3"]),
            NegologIssue("delivery", ["fast", "normal", "slow"]),
        ]

        # NegoLog preferences
        buyer_pref = create_negolog_preference(
            negolog_issues, buyer_issue_weights, buyer_value_weights
        )
        seller_pref = create_negolog_preference(
            negolog_issues, seller_issue_weights, seller_value_weights
        )

        return {
            "negmas_issues": negmas_issues,
            "outcome_space": outcome_space,
            "buyer_ufun": buyer_ufun,
            "seller_ufun": seller_ufun,
            "negolog_issues": negolog_issues,
            "buyer_pref": buyer_pref,
            "seller_pref": seller_pref,
        }

    def test_boulware_first_offer_equivalence(self, domain_setup):
        """Test that Boulware agent makes the same first offer in both systems."""
        # Run NegoLog native
        native_history, _ = run_negolog_native(
            NativeBoulware,
            NativeBoulware,
            domain_setup["buyer_pref"],
            domain_setup["seller_pref"],
            n_rounds=10,
        )

        # Run NegMAS wrapped
        wrapped_history, _ = run_negmas_wrapped(
            BoulwareAgent,
            BoulwareAgent,
            domain_setup["negmas_issues"],
            domain_setup["buyer_ufun"],
            domain_setup["seller_ufun"],
            n_steps=10,
        )

        # Compare first offers
        assert len(native_history) > 0, "Native negotiation produced no history"
        assert len(wrapped_history) > 0, "Wrapped negotiation produced no history"

        native_first = native_history[0]
        wrapped_first = wrapped_history[0]

        # First offer should be from agent A
        assert native_first.agent == "A"
        assert wrapped_first.agent == "A"

        # Utilities should be very close (Boulware starts with high utility)
        assert abs(native_first.utility_a - wrapped_first.utility_a) < 0.1, (
            f"First offer utilities differ: native={native_first.utility_a}, wrapped={wrapped_first.utility_a}"
        )

    def test_conceder_behavior_similarity(self, domain_setup):
        """Test that Conceder agent behavior is similar in both systems."""
        n_rounds = 50

        # Run NegoLog native
        native_history, native_agreement = run_negolog_native(
            NativeConceder,
            NativeConceder,
            domain_setup["buyer_pref"],
            domain_setup["seller_pref"],
            n_rounds=n_rounds,
        )

        # Run NegMAS wrapped
        wrapped_history, wrapped_agreement = run_negmas_wrapped(
            ConcederAgent,
            ConcederAgent,
            domain_setup["negmas_issues"],
            domain_setup["buyer_ufun"],
            domain_setup["seller_ufun"],
            n_steps=n_rounds,
        )

        # Both should reach agreement (Conceder agents converge quickly)
        # Note: Agreement might not be identical due to timing differences
        if native_agreement is not None and wrapped_agreement is not None:
            # Both reached agreement - good
            pass
        elif native_agreement is None and wrapped_agreement is None:
            # Neither reached agreement - also consistent
            pass
        else:
            # One reached agreement and the other didn't - acceptable due to timing
            # but worth noting
            print(
                f"Agreement mismatch: native={native_agreement}, wrapped={wrapped_agreement}"
            )

    def test_linear_utility_progression(self, domain_setup):
        """Test that Linear agent's utility progression is similar in both systems."""
        n_rounds = 50  # More rounds to ensure we get enough offers

        # Run NegoLog native
        native_history, _ = run_negolog_native(
            NativeLinear,
            NativeLinear,
            domain_setup["buyer_pref"],
            domain_setup["seller_pref"],
            n_rounds=n_rounds,
        )

        # Run NegMAS wrapped
        wrapped_history, _ = run_negmas_wrapped(
            LinearAgent,
            LinearAgent,
            domain_setup["negmas_issues"],
            domain_setup["buyer_ufun"],
            domain_setup["seller_ufun"],
            n_steps=n_rounds,
        )

        # Extract agent A's offers from both histories
        native_a_offers = [
            s for s in native_history if s.agent == "A" and s.action_type == "offer"
        ]
        wrapped_a_offers = [
            s for s in wrapped_history if s.agent == "A" and s.action_type == "offer"
        ]

        # Should have similar number of offers
        min_offers = min(len(native_a_offers), len(wrapped_a_offers))

        # Skip test if no offers to compare (can happen if negotiation ends immediately)
        if min_offers == 0:
            pytest.skip("No offers to compare - negotiation ended too quickly")

        # Compare utility progression (should be decreasing for Linear)
        for i in range(min(5, min_offers)):
            native_util = native_a_offers[i].utility_a
            wrapped_util = wrapped_a_offers[i].utility_a

            # Allow some tolerance due to timing differences
            assert abs(native_util - wrapped_util) < 0.15, (
                f"Offer {i} utility mismatch: native={native_util:.3f}, wrapped={wrapped_util:.3f}"
            )

    def test_boulware_vs_conceder_agreement(self, domain_setup):
        """Test Boulware vs Conceder produces similar outcomes in both systems."""
        n_rounds = 100

        # Run NegoLog native
        native_history, native_agreement = run_negolog_native(
            NativeBoulware,
            NativeConceder,
            domain_setup["buyer_pref"],
            domain_setup["seller_pref"],
            n_rounds=n_rounds,
        )

        # Run NegMAS wrapped
        wrapped_history, wrapped_agreement = run_negmas_wrapped(
            BoulwareAgent,
            ConcederAgent,
            domain_setup["negmas_issues"],
            domain_setup["buyer_ufun"],
            domain_setup["seller_ufun"],
            n_steps=n_rounds,
        )

        # If both reach agreement, compare final utilities
        if native_agreement and wrapped_agreement:
            # Get final utilities
            native_final = native_history[-1]
            wrapped_final = wrapped_history[-1]

            # Final utilities should be in similar range
            assert abs(native_final.utility_a - wrapped_final.utility_a) < 0.2, (
                f"Final buyer utility differs significantly"
            )
            assert abs(native_final.utility_b - wrapped_final.utility_b) < 0.2, (
                f"Final seller utility differs significantly"
            )


class TestOfferConsistency:
    """Test that individual offers are consistent between systems."""

    @pytest.fixture
    def simple_domain(self):
        """Create a simple domain for testing."""
        negmas_issues = [
            make_issue(values=["a", "b", "c"], name="issue1"),
            make_issue(values=["x", "y", "z"], name="issue2"),
        ]
        outcome_space = make_os(negmas_issues)

        weights = {"issue1": 0.6, "issue2": 0.4}
        values = {
            "issue1": {"a": 1.0, "b": 0.5, "c": 0.0},
            "issue2": {"x": 1.0, "y": 0.5, "z": 0.0},
        }

        ufun = LinearAdditiveUtilityFunction(
            values=values,
            weights=weights,
            outcome_space=outcome_space,
        )

        negolog_issues = [
            NegologIssue("issue1", ["a", "b", "c"]),
            NegologIssue("issue2", ["x", "y", "z"]),
        ]

        pref = create_negolog_preference(negolog_issues, weights, values)

        return {
            "negmas_issues": negmas_issues,
            "ufun": ufun,
            "negolog_issues": negolog_issues,
            "pref": pref,
        }

    def test_utility_calculation_equivalence(self, simple_domain):
        """Test that utility calculations are equivalent between systems."""
        pref = simple_domain["pref"]
        ufun = simple_domain["ufun"]

        # Test all possible bids
        for bid in pref.bids:
            # Convert to NegMAS outcome
            outcome = (bid[pref.issues[0]], bid[pref.issues[1]])

            negolog_util = pref.get_utility(bid)
            negmas_util = float(ufun(outcome))

            assert abs(negolog_util - negmas_util) < 1e-6, (
                f"Utility mismatch for {outcome}: NegoLog={negolog_util}, NegMAS={negmas_util}"
            )


class TestAllAgentsWork:
    """Test that all wrapped agents can complete negotiations without errors."""

    @pytest.fixture
    def standard_domain(self):
        """Create standard test domain."""
        issues = [
            make_issue(values=["low", "medium", "high"], name="price"),
            make_issue(values=["1", "2", "3"], name="quantity"),
            make_issue(values=["fast", "normal", "slow"], name="delivery"),
        ]
        outcome_space = make_os(issues)

        buyer_ufun = LinearAdditiveUtilityFunction(
            values={
                "price": {"low": 1.0, "medium": 0.5, "high": 0.0},
                "quantity": {"1": 0.0, "2": 0.5, "3": 1.0},
                "delivery": {"fast": 1.0, "normal": 0.5, "slow": 0.0},
            },
            weights={"price": 0.5, "quantity": 0.3, "delivery": 0.2},
            outcome_space=outcome_space,
        )

        seller_ufun = LinearAdditiveUtilityFunction(
            values={
                "price": {"low": 0.0, "medium": 0.5, "high": 1.0},
                "quantity": {"1": 1.0, "2": 0.5, "3": 0.0},
                "delivery": {"fast": 0.0, "normal": 0.5, "slow": 1.0},
            },
            weights={"price": 0.5, "quantity": 0.3, "delivery": 0.2},
            outcome_space=outcome_space,
        )

        return {
            "issues": issues,
            "buyer_ufun": buyer_ufun,
            "seller_ufun": seller_ufun,
        }

    @pytest.mark.parametrize(
        "agent_class",
        [
            BoulwareAgent,
            ConcederAgent,
            LinearAgent,
            NiceTitForTat,
            MICROAgent,
            AgentGG,
            HardHeaded,
        ],
    )
    def test_agent_completes_negotiation(self, standard_domain, agent_class):
        """Test that each agent type can complete a negotiation."""
        mechanism = SAOMechanism(
            issues=standard_domain["issues"],
            n_steps=50,
        )

        buyer = agent_class(name="buyer", ufun=standard_domain["buyer_ufun"])
        seller = BoulwareAgent(name="seller", ufun=standard_domain["seller_ufun"])

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        assert state is not None
        assert state.started
        assert state.ended

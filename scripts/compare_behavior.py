#!/usr/bin/env python3
"""
Comprehensive comparison of NegoLog agents' behavior when run natively vs wrapped in NegMAS.

This script:
1. Runs each agent pair in both native NegoLog and NegMAS wrapper environments
2. Compares offer sequences, utilities, and outcomes
3. Generates a detailed report

Usage:
    python scripts/compare_behavior.py
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

# Add vendored NegoLog to path
NEGOLOG_PATH = Path(__file__).parent.parent / "vendor" / "NegoLog"
if str(NEGOLOG_PATH) not in sys.path:
    sys.path.insert(0, str(NEGOLOG_PATH))

# NegMAS imports
from negmas.outcomes import make_issue, make_os
from negmas.preferences import LinearAdditiveUtilityFunction
from negmas.sao import SAOMechanism

# NegoLog imports
from nenv import Preference, Accept
from nenv.Issue import Issue as NegologIssue

# Import all wrapper classes
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

# Import native NegoLog agents
from agents.boulware.Boulware import BoulwareAgent as NativeBoulware
from agents.conceder.Conceder import ConcederAgent as NativeConceder
from agents.LinearAgent.LinearAgent import LinearAgent as NativeLinear
from agents.MICRO.MICRO import MICROAgent as NativeMICRO
from agents.Atlas3.Atlas3Agent import Atlas3Agent as NativeAtlas3
from agents.NiceTitForTat.NiceTitForTat import NiceTitForTat as NativeNiceTitForTat
from agents.YXAgent.YXAgent import YXAgent as NativeYXAgent
from agents.ParsCat.ParsCat import ParsCatAgent as NativeParsCat
from agents.PonPoko.PonPoko import PonPokoAgent as NativePonPoko
from agents.AgentGG.AgentGG import AgentGG as NativeAgentGG
from agents.SAGA.SAGAAgent import SAGAAgent as NativeSAGA
from agents.CUHKAgent.CUHKAgent import CUHKAgent as NativeCUHK
from agents.AgentKN.AgentKN import AgentKN as NativeAgentKN
from agents.Rubick.Rubick import Rubick as NativeRubick
from agents.AhBuNeAgent.AhBuNeAgent import AhBuNeAgent as NativeAhBuNe
from agents.ParsAgent.ParsAgent import ParsAgent as NativeParsAgent
from agents.RandomDance.RandomDance import RandomDance as NativeRandomDance
from agents.AgentBuyog.AgentBuyog import AgentBuyog as NativeAgentBuyog
from agents.Kawaii.Kawaii import Kawaii as NativeKawaii
from agents.Caduceus2015.Caduceus import Caduceus2015 as NativeCaduceus2015
from agents.Caduceus.Caduceus import Caduceus as NativeCaduceus
from agents.HardHeaded.KLH import HardHeaded as NativeHardHeaded
from agents.IAMhaggler.IAMhaggler import IAMhaggler as NativeIAMhaggler
from agents.LuckyAgent2022.LuckyAgent2022 import LuckyAgent2022 as NativeLuckyAgent2022
from agents.HybridAgent.HybridAgent import HybridAgent as NativeHybridAgent


# Agent mapping: (WrapperClass, NativeClass, name)
AGENTS = [
    (BoulwareAgent, NativeBoulware, "Boulware"),
    (ConcederAgent, NativeConceder, "Conceder"),
    (LinearAgent, NativeLinear, "Linear"),
    (MICROAgent, NativeMICRO, "MICRO"),
    (Atlas3Agent, NativeAtlas3, "Atlas3"),
    (NiceTitForTat, NativeNiceTitForTat, "NiceTitForTat"),
    (YXAgent, NativeYXAgent, "YXAgent"),
    (ParsCatAgent, NativeParsCat, "ParsCat"),
    (PonPokoAgent, NativePonPoko, "PonPoko"),
    (AgentGG, NativeAgentGG, "AgentGG"),
    (SAGAAgent, NativeSAGA, "SAGA"),
    (CUHKAgent, NativeCUHK, "CUHK"),
    (AgentKN, NativeAgentKN, "AgentKN"),
    (Rubick, NativeRubick, "Rubick"),
    (AhBuNeAgent, NativeAhBuNe, "AhBuNe"),
    (ParsAgent, NativeParsAgent, "ParsAgent"),
    (RandomDance, NativeRandomDance, "RandomDance"),
    (AgentBuyog, NativeAgentBuyog, "AgentBuyog"),
    (Kawaii, NativeKawaii, "Kawaii"),
    (Caduceus2015, NativeCaduceus2015, "Caduceus2015"),
    (Caduceus, NativeCaduceus, "Caduceus"),
    (HardHeaded, NativeHardHeaded, "HardHeaded"),
    (IAMhaggler, NativeIAMhaggler, "IAMhaggler"),
    (LuckyAgent2022, NativeLuckyAgent2022, "LuckyAgent2022"),
    (HybridAgent, NativeHybridAgent, "HybridAgent"),
]


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


@dataclass
class NegotiationResult:
    """Result of a negotiation session."""

    history: List[NegotiationStep] = field(default_factory=list)
    agreement: Optional[Dict[str, str]] = None
    final_utility_a: float = 0.0
    final_utility_b: float = 0.0
    num_rounds: int = 0
    error: Optional[str] = None


@dataclass
class ComparisonResult:
    """Comparison between native and wrapped execution."""

    agent_a_name: str
    agent_b_name: str
    native_result: NegotiationResult
    wrapped_result: NegotiationResult

    # Comparison metrics
    both_agreed: bool = False
    neither_agreed: bool = False
    agreement_mismatch: bool = False
    utility_diff_a: float = 0.0
    utility_diff_b: float = 0.0
    round_diff: int = 0
    first_offer_utility_diff: float = 0.0
    behavior_similarity_score: float = 0.0


def create_negolog_preference(
    issues: List[NegologIssue],
    issue_weights: Dict[str, float],
    value_weights: Dict[str, Dict[str, float]],
    reservation_value: float = 0.0,
) -> Preference:
    """Create a NegoLog Preference object programmatically."""
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
) -> NegotiationResult:
    """Run a negotiation using NegoLog natively."""
    result = NegotiationResult()

    try:
        # Create agents
        agent_a = agent_a_class(
            preference=pref_a, session_time=session_time, estimators=[]
        )
        agent_b = agent_b_class(
            preference=pref_b, session_time=session_time, estimators=[]
        )

        # Initialize agents
        agent_a.initiate(opponent_name="AgentB")
        agent_b.initiate(opponent_name="AgentA")

        last_action = None
        round_num = 0

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
            result.history.append(step_a)

            if isinstance(action_a, Accept):
                result.agreement = bid_content_a
                result.final_utility_a = utility_a_a
                result.final_utility_b = utility_b_a
                break

            # Agent B's turn
            t_b = (round_num + 0.5) / n_rounds
            agent_b.receive_bid(action_a.bid, t_b)
            action_b = agent_b.act(t_b)

            if action_b is None:
                break

            bid_content_b = {issue.name: action_b.bid[issue] for issue in pref_b.issues}
            utility_a_b = pref_a.get_utility(action_b.bid)
            utility_b_b = pref_b.get_utility(action_b.bid)

            step_b = NegotiationStep(
                round=round_num,
                time=t_b,
                agent="B",
                action_type="accept" if isinstance(action_b, Accept) else "offer",
                bid_content=bid_content_b,
                utility_a=utility_a_b,
                utility_b=utility_b_b,
            )
            result.history.append(step_b)

            if isinstance(action_b, Accept):
                result.agreement = bid_content_b
                result.final_utility_a = utility_a_b
                result.final_utility_b = utility_b_b
                break

            last_action = action_b

        result.num_rounds = round_num + 1

        # Terminate agents
        agent_a.terminate(result.agreement is not None, "AgentB", 1.0)
        agent_b.terminate(result.agreement is not None, "AgentA", 1.0)

    except Exception as e:
        result.error = str(e)

    return result


def run_negmas_wrapped(
    agent_a_class,
    agent_b_class,
    issues,
    ufun_a,
    ufun_b,
    n_steps: int,
) -> NegotiationResult:
    """Run a negotiation using NegMAS with wrapped NegoLog agents."""
    result = NegotiationResult()

    try:
        mechanism = SAOMechanism(issues=issues, n_steps=n_steps)

        agent_a = agent_a_class(name="AgentA", ufun=ufun_a)
        agent_b = agent_b_class(name="AgentB", ufun=ufun_b)

        mechanism.add(agent_a)
        mechanism.add(agent_b)

        last_offer = None
        state = mechanism.state

        while not state.ended:
            state = mechanism.step()

            if state.current_offer is not None and state.current_offer != last_offer:
                bid_content = {}
                for i, issue in enumerate(issues):
                    bid_content[issue.name] = state.current_offer[i]

                utility_a = float(ufun_a(state.current_offer))
                utility_b = float(ufun_b(state.current_offer))

                # Determine which agent made the offer
                agent_name = (
                    "A"
                    if state.current_proposer and "AgentA" in state.current_proposer
                    else "B"
                )

                step = NegotiationStep(
                    round=state.step,
                    time=state.relative_time,
                    agent=agent_name,
                    action_type="offer",
                    bid_content=bid_content,
                    utility_a=utility_a,
                    utility_b=utility_b,
                )
                result.history.append(step)
                last_offer = state.current_offer

        result.num_rounds = state.step

        if state.agreement is not None:
            result.agreement = {}
            for i, issue in enumerate(issues):
                result.agreement[issue.name] = state.agreement[i]
            result.final_utility_a = float(ufun_a(state.agreement))
            result.final_utility_b = float(ufun_b(state.agreement))

            # Record acceptance
            acceptor = (
                "B" if result.history and result.history[-1].agent == "A" else "A"
            )
            accept_step = NegotiationStep(
                round=state.step,
                time=state.relative_time,
                agent=acceptor,
                action_type="accept",
                bid_content=result.agreement,
                utility_a=result.final_utility_a,
                utility_b=result.final_utility_b,
            )
            result.history.append(accept_step)

    except Exception as e:
        result.error = str(e)

    return result


def compare_negotiations(
    native_result: NegotiationResult,
    wrapped_result: NegotiationResult,
    agent_a_name: str,
    agent_b_name: str,
) -> ComparisonResult:
    """Compare native and wrapped negotiation results."""
    comparison = ComparisonResult(
        agent_a_name=agent_a_name,
        agent_b_name=agent_b_name,
        native_result=native_result,
        wrapped_result=wrapped_result,
    )

    # Agreement comparison
    native_agreed = native_result.agreement is not None
    wrapped_agreed = wrapped_result.agreement is not None

    comparison.both_agreed = native_agreed and wrapped_agreed
    comparison.neither_agreed = not native_agreed and not wrapped_agreed
    comparison.agreement_mismatch = native_agreed != wrapped_agreed

    # Utility differences (if both agreed)
    if comparison.both_agreed:
        comparison.utility_diff_a = abs(
            native_result.final_utility_a - wrapped_result.final_utility_a
        )
        comparison.utility_diff_b = abs(
            native_result.final_utility_b - wrapped_result.final_utility_b
        )

    # Round difference
    comparison.round_diff = abs(native_result.num_rounds - wrapped_result.num_rounds)

    # First offer utility comparison
    if native_result.history and wrapped_result.history:
        native_first = native_result.history[0]
        wrapped_first = wrapped_result.history[0]
        comparison.first_offer_utility_diff = abs(
            native_first.utility_a - wrapped_first.utility_a
        )

    # Calculate behavior similarity score (0 to 1)
    score = 0.0
    factors = 0

    # Same agreement outcome
    if comparison.both_agreed or comparison.neither_agreed:
        score += 1.0
    factors += 1

    # Similar number of rounds (within 20%)
    if native_result.num_rounds > 0 and wrapped_result.num_rounds > 0:
        round_ratio = min(native_result.num_rounds, wrapped_result.num_rounds) / max(
            native_result.num_rounds, wrapped_result.num_rounds
        )
        score += round_ratio
        factors += 1

    # Similar first offer utility (within 0.1)
    if comparison.first_offer_utility_diff < 0.1:
        score += 1.0
    elif comparison.first_offer_utility_diff < 0.2:
        score += 0.5
    factors += 1

    # Similar final utilities (if both agreed)
    if comparison.both_agreed:
        if comparison.utility_diff_a < 0.1 and comparison.utility_diff_b < 0.1:
            score += 1.0
        elif comparison.utility_diff_a < 0.2 and comparison.utility_diff_b < 0.2:
            score += 0.5
        factors += 1

    comparison.behavior_similarity_score = score / factors if factors > 0 else 0.0

    return comparison


def create_test_domain():
    """Create test domain for both NegoLog and NegMAS."""
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


def run_comparison_for_agent(
    wrapper_class,
    native_class,
    agent_name: str,
    domain: dict,
    n_rounds: int = 100,
) -> ComparisonResult:
    """Run comparison for a single agent against Boulware opponent."""
    print(f"  Testing {agent_name}...", end=" ", flush=True)

    # Run native NegoLog
    native_result = run_negolog_native(
        native_class,
        NativeBoulware,  # Use Boulware as standard opponent
        domain["buyer_pref"],
        domain["seller_pref"],
        n_rounds=n_rounds,
    )

    # Run NegMAS wrapped
    wrapped_result = run_negmas_wrapped(
        wrapper_class,
        BoulwareAgent,  # Use wrapped Boulware as standard opponent
        domain["negmas_issues"],
        domain["buyer_ufun"],
        domain["seller_ufun"],
        n_steps=n_rounds,
    )

    # Compare results
    comparison = compare_negotiations(
        native_result,
        wrapped_result,
        agent_name,
        "Boulware",
    )

    status = "OK" if comparison.behavior_similarity_score >= 0.5 else "DIFF"
    if native_result.error:
        status = f"NATIVE_ERR: {native_result.error[:30]}"
    elif wrapped_result.error:
        status = f"WRAPPED_ERR: {wrapped_result.error[:30]}"

    print(f"[{status}] (similarity: {comparison.behavior_similarity_score:.2f})")

    return comparison


def generate_report(comparisons: List[ComparisonResult], output_path: Path):
    """Generate detailed comparison report in Markdown format."""
    lines = []

    # Header
    lines.append("# NegoLog vs NegMAS Wrapper Behavior Comparison Report")
    lines.append("")
    lines.append(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Summary statistics
    total = len(comparisons)
    both_agreed = sum(1 for c in comparisons if c.both_agreed)
    neither_agreed = sum(1 for c in comparisons if c.neither_agreed)
    mismatch = sum(1 for c in comparisons if c.agreement_mismatch)
    native_errors = sum(1 for c in comparisons if c.native_result.error)
    wrapped_errors = sum(1 for c in comparisons if c.wrapped_result.error)

    high_similarity = sum(1 for c in comparisons if c.behavior_similarity_score >= 0.75)
    medium_similarity = sum(
        1 for c in comparisons if 0.5 <= c.behavior_similarity_score < 0.75
    )
    low_similarity = sum(
        1
        for c in comparisons
        if c.behavior_similarity_score < 0.5
        and not c.native_result.error
        and not c.wrapped_result.error
    )

    avg_similarity = sum(
        c.behavior_similarity_score
        for c in comparisons
        if not c.native_result.error and not c.wrapped_result.error
    )
    valid_count = sum(
        1
        for c in comparisons
        if not c.native_result.error and not c.wrapped_result.error
    )
    avg_similarity = avg_similarity / valid_count if valid_count > 0 else 0

    # Summary section
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total agents tested | {total} |")
    lines.append(f"| Both agreed | {both_agreed} |")
    lines.append(f"| Neither agreed | {neither_agreed} |")
    lines.append(f"| Agreement mismatch | {mismatch} |")
    lines.append(f"| Native errors | {native_errors} |")
    lines.append(f"| Wrapper errors | {wrapped_errors} |")
    lines.append("")

    # Similarity breakdown
    lines.append("### Behavior Similarity")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| High (>= 0.75) | {high_similarity} |")
    lines.append(f"| Medium (0.5 - 0.75) | {medium_similarity} |")
    lines.append(f"| Low (< 0.5) | {low_similarity} |")
    lines.append(f"| **Average** | **{avg_similarity:.2f}** |")
    lines.append("")

    # Results table
    lines.append("## Results by Agent")
    lines.append("")
    lines.append("| Agent | Similarity | Native | Wrapped | Agreement | Utility Diff |")
    lines.append("|-------|------------|--------|---------|-----------|--------------|")

    for c in comparisons:
        # Similarity with visual indicator
        sim = c.behavior_similarity_score
        if sim >= 0.75:
            sim_indicator = f"**{sim:.2f}**"
        elif sim >= 0.5:
            sim_indicator = f"{sim:.2f}"
        else:
            sim_indicator = f"*{sim:.2f}*"

        # Handle errors
        if c.native_result.error:
            native_info = "Error"
        else:
            native_info = f"{c.native_result.num_rounds}r"

        if c.wrapped_result.error:
            wrapped_info = "Error"
        else:
            wrapped_info = f"{c.wrapped_result.num_rounds}r"

        # Agreement status
        if c.native_result.error or c.wrapped_result.error:
            agreement = "N/A"
        elif c.both_agreed:
            agreement = "Both"
        elif c.neither_agreed:
            agreement = "Neither"
        else:
            agreement = "Mismatch"

        # Utility diff
        if c.both_agreed:
            util_diff = f"A:{c.utility_diff_a:.2f}, B:{c.utility_diff_b:.2f}"
        else:
            util_diff = "-"

        lines.append(
            f"| {c.agent_a_name} | {sim_indicator} | {native_info} | {wrapped_info} | {agreement} | {util_diff} |"
        )

    lines.append("")

    # Detailed results for agents with agreements
    lines.append("## Detailed Results")
    lines.append("")

    # Group by similarity
    high_sim = [c for c in comparisons if c.behavior_similarity_score >= 0.75]
    med_sim = [c for c in comparisons if 0.5 <= c.behavior_similarity_score < 0.75]
    low_sim = [
        c
        for c in comparisons
        if c.behavior_similarity_score < 0.5
        and not c.native_result.error
        and not c.wrapped_result.error
    ]
    errors = [c for c in comparisons if c.native_result.error or c.wrapped_result.error]

    if high_sim:
        lines.append("### High Similarity Agents (>= 0.75)")
        lines.append("")
        for c in high_sim:
            lines.append(f"#### {c.agent_a_name}")
            lines.append("")
            _add_agent_details(lines, c)
            lines.append("")

    if med_sim:
        lines.append("### Medium Similarity Agents (0.5 - 0.75)")
        lines.append("")
        for c in med_sim:
            lines.append(f"#### {c.agent_a_name}")
            lines.append("")
            _add_agent_details(lines, c)
            lines.append("")

    if low_sim:
        lines.append("### Low Similarity Agents (< 0.5)")
        lines.append("")
        lines.append("> These agents require investigation.")
        lines.append("")
        for c in low_sim:
            lines.append(f"#### {c.agent_a_name}")
            lines.append("")
            _add_agent_details(lines, c)
            lines.append("")

    if errors:
        lines.append("### Agents with Errors")
        lines.append("")
        for c in errors:
            lines.append(f"#### {c.agent_a_name}")
            lines.append("")
            if c.native_result.error:
                lines.append(f"- **Native error:** `{c.native_result.error}`")
            if c.wrapped_result.error:
                lines.append(f"- **Wrapper error:** `{c.wrapped_result.error}`")
            lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by `scripts/compare_behavior.py`*")

    # Write report
    report_text = "\n".join(lines)
    # Change extension to .md
    md_output_path = output_path.with_suffix(".md")
    md_output_path.write_text(report_text)
    print(f"\nReport saved to: {md_output_path}")


def _add_agent_details(lines: List[str], c: ComparisonResult):
    """Add detailed agent comparison info to report lines."""
    lines.append(f"- **Similarity Score:** {c.behavior_similarity_score:.2f}")
    lines.append(f"- **Opponent:** {c.agent_b_name}")
    lines.append("")

    if not c.native_result.error and not c.wrapped_result.error:
        # Comparison table
        lines.append("| | Native | Wrapped | Diff |")
        lines.append("|---|--------|---------|------|")
        lines.append(
            f"| Rounds | {c.native_result.num_rounds} | {c.wrapped_result.num_rounds} | {c.round_diff} |"
        )

        native_agreed = "Yes" if c.native_result.agreement else "No"
        wrapped_agreed = "Yes" if c.wrapped_result.agreement else "No"
        agreement_match = "=" if native_agreed == wrapped_agreed else "!="
        lines.append(
            f"| Agreement | {native_agreed} | {wrapped_agreed} | {agreement_match} |"
        )

        if c.both_agreed:
            lines.append(
                f"| Utility A | {c.native_result.final_utility_a:.3f} | {c.wrapped_result.final_utility_a:.3f} | {c.utility_diff_a:.3f} |"
            )
            lines.append(
                f"| Utility B | {c.native_result.final_utility_b:.3f} | {c.wrapped_result.final_utility_b:.3f} | {c.utility_diff_b:.3f} |"
            )

        lines.append(f"| First Offer Util | - | - | {c.first_offer_utility_diff:.3f} |")


def generate_json_report(comparisons: List[ComparisonResult], output_path: Path):
    """Generate JSON report for programmatic access."""
    total = len(comparisons)
    both_agreed = sum(1 for c in comparisons if c.both_agreed)
    neither_agreed = sum(1 for c in comparisons if c.neither_agreed)
    mismatch = sum(1 for c in comparisons if c.agreement_mismatch)
    native_errors = sum(1 for c in comparisons if c.native_result.error)
    wrapped_errors = sum(1 for c in comparisons if c.wrapped_result.error)

    high_similarity = sum(1 for c in comparisons if c.behavior_similarity_score >= 0.75)
    medium_similarity = sum(
        1 for c in comparisons if 0.5 <= c.behavior_similarity_score < 0.75
    )
    low_similarity = sum(
        1
        for c in comparisons
        if c.behavior_similarity_score < 0.5
        and not c.native_result.error
        and not c.wrapped_result.error
    )

    avg_similarity = sum(
        c.behavior_similarity_score
        for c in comparisons
        if not c.native_result.error and not c.wrapped_result.error
    )
    valid_count = sum(
        1
        for c in comparisons
        if not c.native_result.error and not c.wrapped_result.error
    )
    avg_similarity = avg_similarity / valid_count if valid_count > 0 else 0

    json_data = {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "native_errors": native_errors,
            "wrapped_errors": wrapped_errors,
            "both_agreed": both_agreed,
            "neither_agreed": neither_agreed,
            "agreement_mismatch": mismatch,
            "high_similarity": high_similarity,
            "medium_similarity": medium_similarity,
            "low_similarity": low_similarity,
            "average_similarity": avg_similarity,
        },
        "results": [
            {
                "agent_a": c.agent_a_name,
                "agent_b": c.agent_b_name,
                "similarity_score": c.behavior_similarity_score,
                "native_error": c.native_result.error,
                "wrapped_error": c.wrapped_result.error,
                "native_rounds": c.native_result.num_rounds,
                "wrapped_rounds": c.wrapped_result.num_rounds,
                "native_agreement": c.native_result.agreement is not None,
                "wrapped_agreement": c.wrapped_result.agreement is not None,
                "both_agreed": c.both_agreed,
                "utility_diff_a": c.utility_diff_a,
                "utility_diff_b": c.utility_diff_b,
            }
            for c in comparisons
        ],
    }

    json_path = output_path.with_suffix(".json")
    json_path.write_text(json.dumps(json_data, indent=2))
    print(f"JSON data saved to: {json_path}")


def main():
    """Main function to run all comparisons."""
    print("NegoLog vs NegMAS Wrapper Behavior Comparison")
    print("=" * 50)
    print()

    # Create test domain
    print("Creating test domain...")
    domain = create_test_domain()

    # Run comparisons for all agents
    print("\nRunning comparisons:")
    comparisons = []

    for wrapper_class, native_class, name in AGENTS:
        try:
            comparison = run_comparison_for_agent(
                wrapper_class,
                native_class,
                name,
                domain,
                n_rounds=100,
            )
            comparisons.append(comparison)
        except Exception as e:
            print(f"  {name}: FATAL ERROR - {e}")
            # Create error result
            comparison = ComparisonResult(
                agent_a_name=name,
                agent_b_name="Boulware",
                native_result=NegotiationResult(error=str(e)),
                wrapped_result=NegotiationResult(error=str(e)),
            )
            comparisons.append(comparison)

    # Generate report
    print("\nGenerating report...")
    output_dir = Path(__file__).parent.parent / "reports"
    output_dir.mkdir(exist_ok=True)
    report_path = output_dir / "behavior_comparison_report"
    generate_report(comparisons, report_path)
    generate_json_report(comparisons, report_path)

    # Print summary
    print("\n" + "=" * 50)
    print("QUICK SUMMARY")
    print("=" * 50)

    valid = [
        c
        for c in comparisons
        if not c.native_result.error and not c.wrapped_result.error
    ]
    if valid:
        avg = sum(c.behavior_similarity_score for c in valid) / len(valid)
        print(f"Average behavior similarity: {avg:.2f}")
        print(
            f"Agents with high similarity (>=0.75): {sum(1 for c in valid if c.behavior_similarity_score >= 0.75)}/{len(valid)}"
        )

    errors = [c for c in comparisons if c.native_result.error or c.wrapped_result.error]
    if errors:
        print(f"Agents with errors: {len(errors)}")
        for c in errors:
            if c.native_result.error:
                print(f"  - {c.agent_a_name} (native): {c.native_result.error[:50]}")
            if c.wrapped_result.error:
                print(f"  - {c.agent_a_name} (wrapped): {c.wrapped_result.error[:50]}")


if __name__ == "__main__":
    main()

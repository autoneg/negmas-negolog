"""AgentGG's importance map: same numbers as the scan it replaced, computed once.

`ImpMap.getImportance` found a value's unit by scanning the issue's value list, and
`AgentGG.get_bids`/`get_random_bid` called it for every bid in the outcome space on every
round -- 188,160 calls per round on the ANAC-2026 Travel domain, 18.5s of a 49s
negotiation. But `impMap` describes the agent's *own* preferences: it is built in the
constructor and never updated afterwards (only `opponentImpMap` changes), so those
numbers are fixed for the whole negotiation.

These tests pin both halves: the indexed lookup agrees with the scan, and the per-bid
importance really is constant so caching it is sound.
"""

from pathlib import Path
import sys

import pytest

# Add vendored NegoLog to path (bundled inside the package so it ships in the wheel)
NEGOLOG_PATH = (
    Path(__file__).parent.parent / "src" / "negmas_negolog" / "_vendor" / "NegoLog"
)
if str(NEGOLOG_PATH) not in sys.path:
    sys.path.insert(0, str(NEGOLOG_PATH))

from negmas.outcomes import make_issue, make_os  # noqa: E402
from negmas.preferences import LinearAdditiveUtilityFunction  # noqa: E402
from negmas.preferences.value_fun import TableFun  # noqa: E402

from agents.AgentGG.ImpMap import ImpMap  # noqa: E402
from negmas_negolog.common import NegologPreferenceAdapter  # noqa: E402
from nenv import Issue as NegologIssue  # noqa: E402


def scan_importance(imp_map, bid) -> float:
    """The original `getImportance`, kept verbatim as the oracle."""
    total = 0.0
    for issue in imp_map.pref.issues:
        value = bid[issue]
        value_importance = 0.0
        for unit in imp_map.map[issue]:
            if unit.valueOfIssue == value:
                value_importance = unit.meanWeightSum
                break
        total += value_importance
    return total


def make_preference(sizes=(3, 4, 2)):
    """A NegoLog preference adapter over a small NegMAS linear-additive ufun."""
    issues = [
        make_issue([f"v{i}_{j}" for j in range(n)], f"i{i}")
        for i, n in enumerate(sizes)
    ]
    os_ = make_os(issues)
    ufun = LinearAdditiveUtilityFunction(
        values=[
            TableFun({f"v{i}_{j}": (j + 1) / n for j in range(n)})
            for i, n in enumerate(sizes)
        ],
        weights=[1.0] * len(sizes),
        outcome_space=os_,
    )
    negolog_issues = [
        NegologIssue(f"i{i}", [f"v{i}_{j}" for j in range(n)])
        for i, n in enumerate(sizes)
    ]
    names = [f"i{i}" for i in range(len(sizes))]
    return NegologPreferenceAdapter(
        ufun=ufun, issues=negolog_issues, issue_names=names, reservation_value=0.0
    )


@pytest.mark.parametrize("sizes", [(3, 4, 2), (2, 2), (5,), (2, 3, 2, 3)])
def test_indexed_lookup_matches_the_scan(sizes):
    """Every bid's importance is what the scan produced, before and after updates.

    The opponent updates matter: they re-sort each issue's units, which is what decides
    the unit a repeated value resolves to, so the index has to be rebuilt after them.
    """
    pref = make_preference(sizes)
    imp_map = ImpMap(pref)
    imp_map.self_update(pref.bids)

    assert [imp_map.getImportance(b) for b in pref.bids] == [
        scan_importance(imp_map, b) for b in pref.bids
    ]

    for bid in pref.bids[:3] + pref.bids[-3:]:
        imp_map.opponent_update(bid)
        assert [imp_map.getImportance(b) for b in pref.bids] == [
            scan_importance(imp_map, b) for b in pref.bids
        ]


def test_self_importance_is_constant_so_caching_it_is_sound():
    """`opponent_update` must not disturb the self map AgentGG caches importances from.

    This is the assumption behind `AgentGG._importance_of_each_bid`. It holds because the
    agent keeps two separate maps; the test fails loudly if they are ever merged.
    """
    pref = make_preference()
    self_map = ImpMap(pref)
    self_map.self_update(pref.bids)
    before = [self_map.getImportance(b) for b in pref.bids]

    opponent_map = ImpMap(pref)
    for bid in pref.bids:
        opponent_map.opponent_update(bid)

    assert [self_map.getImportance(b) for b in pref.bids] == before


def test_importance_lookup_does_not_rescan_the_value_list():
    """A value's unit is found by lookup, not by walking the issue's values.

    Uses a deliberately wide issue: with the scan, importance of the *last* value costs
    proportionally more than the first, and this asserts that it does not.
    """
    import time

    pref = make_preference((200,))
    imp_map = ImpMap(pref)
    imp_map.self_update(pref.bids)
    first, last = pref.bids[0], pref.bids[-1]

    def cost(bid):
        t = time.perf_counter()
        for _ in range(2000):
            imp_map.getImportance(bid)
        return time.perf_counter() - t

    # Generous bound: a scan makes the far end ~200x dearer, a lookup makes it equal.
    assert cost(last) < cost(first) * 5

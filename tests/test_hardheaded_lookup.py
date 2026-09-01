"""HardHeaded's TreeMap lookups: same answers as the scan they replaced, without the sort.

`floorEntry`/`lowerEntry` are Java `TreeMap` methods the original agent called on a sorted
map. Ported onto a plain `dict` they re-sorted every key on every call, which is
O(n log n) per lookup with n the size of the whole outcome space -- and both sit inside
loops that walk the bid list one entry at a time. On the 188,160-outcome ANAC-2026 Travel
domain that came to roughly 870 full sorts per received offer.

These tests pin the two properties the rewrite has to have: identical answers (including
the fallback the scan reached by running off the end of its list), and a cost that stops
growing with the outcome space.
"""

from pathlib import Path
import random
import sys

import pytest

# Add vendored NegoLog to path (bundled inside the package so it ships in the wheel)
NEGOLOG_PATH = (
    Path(__file__).parent.parent / "src" / "negmas_negolog" / "_vendor" / "NegoLog"
)
if str(NEGOLOG_PATH) not in sys.path:
    sys.path.insert(0, str(NEGOLOG_PATH))


def scan_floor(d: dict, target_key: float) -> tuple:
    """The original `floorEntry`, kept here verbatim as the oracle."""
    all_keys = list(d.keys())
    all_keys.sort(reverse=True)
    for key in all_keys:
        if key <= target_key:
            return key, d[key]
    return all_keys[-1], d[all_keys[-1]]


def scan_lower(d: dict, target_key: float) -> tuple:
    """The original `lowerEntry`, kept here verbatim as the oracle."""
    all_keys = list(d.keys())
    all_keys.sort(reverse=True)
    for key in all_keys:
        if key < target_key:
            return key, d[key]
    return all_keys[-1], d[all_keys[-1]]


def _agent_with(bid_list: dict):
    """A HardHeaded whose `BSelector` holds `bid_list`, without running a negotiation."""
    from agents.HardHeaded.KLH import HardHeaded

    agent = HardHeaded.__new__(HardHeaded)
    selector = type("S", (), {})()
    selector.BidList = bid_list
    selector.sorted_keys = sorted(bid_list.keys())
    agent.BSelector = selector
    return agent


@pytest.mark.parametrize("seed", range(20))
def test_lookups_match_the_scan_they_replaced(seed):
    """Every probe returns exactly what the linear scan returned.

    The keys mix coarse and fine rounding so that exact hits and near-ties both occur,
    and the probes deliberately include values below the minimum and above the maximum --
    the two cases where the scan falls off its list and returns the *smallest* key.
    """
    rng = random.Random(seed)
    for _ in range(50):
        n = rng.randint(1, 60)
        keys = [round(rng.uniform(-1, 2), rng.choice([1, 2, 12])) for _ in range(n)]
        d = {k: f"bid{i}" for i, k in enumerate(keys)}
        agent = _agent_with(d)
        probes = list(d) + [min(d) - 1, max(d) + 1, min(d), max(d)]
        probes += [rng.uniform(-2, 3) for _ in range(5)]
        for t in probes:
            assert agent.floorEntry(d, t) == scan_floor(d, t)
            assert agent.lowerEntry(d, t) == scan_lower(d, t)


def test_a_dictionary_that_is_not_the_bid_list_still_works():
    """Only `BidList`'s order is known, so anything else must fall back to the scan."""
    agent = _agent_with({0.1: "a", 0.5: "b", 0.9: "c"})
    other = {0.2: "x", 0.4: "y", 0.8: "z"}
    for t in (0.0, 0.2, 0.3, 0.8, 1.0):
        assert agent.floorEntry(other, t) == scan_floor(other, t)
        assert agent.lowerEntry(other, t) == scan_lower(other, t)


def test_a_stale_key_order_is_not_trusted():
    """A BidList that changed size is re-sorted rather than served from a stale order.

    `BidSelector` never mutates `BidList` after building it, so this cannot happen today;
    the guard is here so that if some later edit does mutate it, the result is merely slow
    rather than silently wrong.
    """
    d = {0.1: "a", 0.5: "b", 0.9: "c"}
    agent = _agent_with(d)
    d[0.7] = "d"  # behind the cached order's back
    assert agent.floorEntry(d, 0.8) == (0.7, "d")


def test_lookup_cost_does_not_grow_with_the_outcome_space():
    """A lookup on a 200x larger bid list must not cost 200x more.

    This is the regression that matters: the scan was O(n log n) per call, so on a large
    domain a single received offer spent seconds inside these two methods.
    """
    import time

    def elapsed(n: int) -> float:
        d = {i / n: f"bid{i}" for i in range(n)}
        agent = _agent_with(d)
        probes = [(i % n) / n for i in range(2000)]
        t = time.perf_counter()
        for p in probes:
            agent.floorEntry(d, p)
            agent.lowerEntry(d, p)
        return time.perf_counter() - t

    small, large = elapsed(1_000), elapsed(200_000)
    # Binary search grows with log n, so the true ratio is ~1.5x; 10x leaves ample room
    # for a loaded machine while still failing outright if the sort ever comes back.
    assert large < small * 10, f"{small:.4f}s at n=1,000 but {large:.4f}s at n=200,000"

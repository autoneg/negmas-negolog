"""Iterating a bid: the same pairs in the same order, without the quadratic rebuild.

`IssueIterator.__next__` used to evaluate `list(self.content.keys())` *twice* on every
step, so `for issue, value in bid` -- which every NegoLog agent, opponent model and the
vendored `Preference.get_utility` runs -- cost O(k^2) key-list constructions in the number
of issues, with a hash of every `Issue` each time. In the NiceTitForTat profile it was the
single largest entry: 19,569,168 calls, 17.1s of 46.7s, and it is the reason
`Issue.__hash__` shows tens of millions of calls across nearly every agent profile.

This is the highest blast-radius change of the three, so the tests here are about the
contract rather than about any one agent: the sequence of pairs, its order, the
`StopIteration` at the end, and the one mutation an agent can actually perform -- writing
to an issue the bid already has, via `Bid.__setitem__` -- all measured against the
original iterator kept verbatim as the oracle.
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

from nenv import Bid  # noqa: E402
from nenv import Issue as NegologIssue  # noqa: E402


class OracleIssueIterator:
    """The original `IssueIterator`, kept verbatim as the oracle."""

    def __init__(self, content: dict):
        self.content = content
        self.index = 0

    def __next__(self):
        if self.index < len(self.content):
            self.index += 1

            return list(self.content.keys())[self.index - 1], self.content[list(self.content.keys())[self.index - 1]]

        raise StopIteration


def drain(iterator):
    """Everything an iterator yields, as a list, stopping at `StopIteration`."""
    out = []

    while True:
        try:
            out.append(next(iterator))
        except StopIteration:
            return out


def random_content(rng: random.Random):
    """An issue -> value dict of a random shape, sometimes empty or single-issue."""
    n_issues = rng.choice([0, 1, 1, 2, 3, 7, 12])

    return {
        NegologIssue(f"i{i}", [f"v{i}_{j}" for j in range(rng.randint(1, 3))]): (
            f"v{i}_{rng.randint(0, 2)}"
        )
        for i in range(n_issues)
    }


@pytest.mark.parametrize("seed", range(300))
def test_iteration_yields_exactly_what_the_original_yielded(seed):
    """Same pairs, same order, over randomly shaped bids including the empty one.

    Order is the whole point: `Caduceus2015.vectorizeBid` walks a bid and writes into a
    positional vector by counting the steps, so a reordering would silently permute its
    opponent model.
    """
    rng = random.Random(seed)
    content = random_content(rng)
    bid = Bid(dict(content))

    assert drain(iter(bid)) == drain(OracleIssueIterator(dict(content)))


def test_iteration_stops_and_stays_stopped():
    """`StopIteration` at the end, and again on every later call, as before.

    Nothing in the codebase re-uses an exhausted iterator, but the original raised rather
    than restarting, and a rewrite that silently restarted would loop an agent forever.
    """
    issue = NegologIssue("i0", ["a"])
    content = {issue: "a"}

    fast, oracle = iter(Bid(dict(content))), OracleIssueIterator(dict(content))
    assert next(fast) == next(oracle)

    for _ in range(3):
        with pytest.raises(StopIteration):
            next(fast)
        with pytest.raises(StopIteration):
            next(oracle)


@pytest.mark.parametrize("seed", range(50))
def test_assigning_to_an_issue_mid_iteration_behaves_as_before(seed):
    """A value written during iteration is still seen by the steps that follow it.

    `Bid.__setitem__` on an issue the bid already carries is the only mutation available
    to an agent mid-iteration -- no caller in the tree does it, but the rewrite must not
    quietly change what would happen if one did, so values are still read live from the
    bid rather than snapshotted alongside the keys.
    """
    rng = random.Random(seed)
    content = {
        NegologIssue(f"i{i}", ["a", "b"]): "a" for i in range(rng.randint(1, 6))
    }
    at = rng.randrange(len(content))

    def walk(iterator, bid):
        seen = []
        for step, (issue, value) in enumerate(drain_lazily(iterator)):
            seen.append((issue, value))
            if step == at:
                for other in bid.content:
                    bid[other] = "b"
        return seen

    def drain_lazily(iterator):
        while True:
            try:
                yield next(iterator)
            except StopIteration:
                return

    fast_bid, oracle_bid = Bid(dict(content)), Bid(dict(content))

    assert walk(iter(fast_bid), fast_bid) == walk(
        OracleIssueIterator(oracle_bid.content), oracle_bid
    )


def test_iteration_cost_is_linear_in_the_number_of_issues():
    """Twice the issues costs about twice as much, not four times as much.

    The quadratic rebuild is what this change exists to remove, and a large domain such as
    ANAC-2026 Travel has enough issues for the difference to dominate whole profiles.
    """
    import time

    def cost(n_issues):
        bid = Bid({NegologIssue(f"i{i}", ["a"]): "a" for i in range(n_issues)})

        t = time.perf_counter()
        for _ in range(2000):
            for _issue, _value in bid:
                pass
        return time.perf_counter() - t

    # Generous bound: quadratic makes 8x the issues ~64x dearer, linear makes it ~8x.
    assert cost(80) < cost(10) * 24

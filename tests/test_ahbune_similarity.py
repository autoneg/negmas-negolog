"""AhBuNe's similarity map: the same available/forbidden sets, without the value scans.

`SimilarityMap.createConditionLists` rebuilds the agent's available and forbidden value
sets once per round from the whole estimated bid ranking, which for AhBuNe *is* the whole
outcome space -- 188,160 bids on the ANAC-2026 Travel domain. For every bid it then
scanned that issue's `IssueValueUnit` list to decide whether the bid's value was known.
On Travel that came to 32 calls costing 33.6s of a 40.7s negotiation, driving 62.9M
`Bid.__getitem__` and 26.9M `Issue.__eq__` calls; `extract_issue_value_imp` scans the same
way.

The replacement does two things, and this file pins both against the original kept
verbatim as the oracle:

* the scan becomes a lookup in a value -> unit index, which must resolve a repeated value
  to the same unit the scan's first match picked, and must still ignore a value that has
  no unit at all;
* the bid loops stop once every value the map can hold has been recorded, because from
  that point on each remaining bid is a no-op. That is a fixed point, not a truncation:
  the sets it produces are the sets the full walk produced.
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

import nenv  # noqa: E402
from nenv import Issue as NegologIssue  # noqa: E402

from agents.AhBuNeAgent.impmap.SimilarityMap import SimilarityMap  # noqa: E402
from agents.AhBuNeAgent.linearorder.SimpleLinearOrdering import (  # noqa: E402
    SimpleLinearOrdering,
)


class OracleSimilarityMap(SimilarityMap):
    """`SimilarityMap` with the two rewritten methods restored verbatim.

    Subclassing rather than copying the whole class keeps the oracle to exactly the code
    under test: everything else -- `renewMaps`, `renewLists`, `update`, `stdev`,
    `sortByValueBid` -- is shared with the real map, so a difference can only come from
    the scans.
    """

    def createConditionLists(self, numFirstBids: int, numLastBids: int):
        # Initiate lists
        self.renewLists()

        # Get estimated bids
        sortedBids = self.estimatedProfile.getBids()
        firstStartIndex = (len(sortedBids) - 1) - numFirstBids

        # Start index must be >= 0
        if firstStartIndex < 0:
            firstStartIndex = 0

        # Find available values
        for bidIndex in range(firstStartIndex, len(sortedBids)):
            currentBid = sortedBids[bidIndex]

            for issue in currentBid.content.keys():
                currentIssueList = self.issueValueImpMap[issue]

                for currentUnit in currentIssueList:
                    if currentUnit.valueOfIssue == currentBid[issue]:
                        if currentBid[issue] not in self.availableValues[issue]:
                            self.availableValues[issue].add(currentBid[issue])
                        break

        # Number of last bids cannot exceed the number of total bids
        if numLastBids >= len(sortedBids):
            numLastBids = len(sortedBids) - 1

        # Find forbidden values
        for bidIndex in range(0, numLastBids):
            currentBid = sortedBids[bidIndex]

            for issue in currentBid.content.keys():
                currentIssueList = self.issueValueImpMap[issue]

                for currentUnit in currentIssueList:
                    if currentUnit.valueOfIssue == currentBid[issue]:
                        if currentBid[issue] not in self.forbiddenValues[issue]:
                            self.forbiddenValues[issue].add(currentBid[issue])
                        break

    def extract_issue_value_imp(self, sortedBids: list, issueValueImpMap: dict):
        # Iterate over sorted bids to extract the Issue-Value importance dictionary
        for bidIndex in range(len(sortedBids)):
            currentBid = sortedBids[bidIndex]
            bidImportance = float(bidIndex) + 1.

            for issue in currentBid.content.keys():
                currentIssueList = issueValueImpMap[issue]

                for currentUnit in currentIssueList:
                    if currentBid[issue] == currentUnit.valueOfIssue:
                        currentUnit.importanceList.append(bidImportance)
                        break


class StubPreference:
    """The slice of `nenv.Preference` the similarity map touches: its issue list.

    A stub rather than a real preference because the awkward cases this file has to reach
    -- an issue whose value list repeats a value, a bid carrying a value no issue declares
    -- cannot be expressed through a NegMAS utility function, which would collapse the
    duplicate and reject the stray value. The map itself never consults utilities in the
    code under test.
    """

    def __init__(self, issues):
        self._issues = issues

    @property
    def issues(self):
        return list(self._issues)


def random_domain(rng: random.Random):
    """An issue list of a random shape, sometimes with repeated or unused values."""
    n_issues = rng.randint(1, 4)
    issues = []

    for i in range(n_issues):
        n_values = rng.randint(1, 4)
        values = [f"v{i}_{rng.randint(0, n_values)}" for _ in range(n_values)]

        issues.append(NegologIssue(f"i{i}", values))

    return issues


def random_bids(rng: random.Random, issues, n_bids: int):
    """Bids over those issues -- occasionally with a stray value or a missing issue."""
    bids = []

    for _ in range(n_bids):
        content = {}

        for issue in issues:
            if rng.random() < 0.05:
                continue  # a bid that simply does not mention this issue

            if rng.random() < 0.1:
                content[issue] = "stray"  # a value no unit was created for
            else:
                content[issue] = rng.choice(issue.values)

        bids.append(nenv.Bid(content))

    return bids


def sets_of(imp_map):
    return (
        {k: set(v) for k, v in imp_map.availableValues.items()},
        {k: set(v) for k, v in imp_map.forbiddenValues.items()},
    )


def floats(mapping):
    """Compare float maps by repr, so that a NaN equals a NaN.

    An issue no bid ever gave a value to has an empty average list, and `numpy.std([])` is
    NaN -- which does not compare equal to itself, so the raw dicts would differ even when
    both sides produced exactly the same number.
    """
    return {k: repr(v) for k, v in mapping.items()}


def importance_lists(imp_map):
    return {
        name: [list(unit.importanceList) for unit in units]
        for name, units in imp_map.issueValueImpMap.items()
    }


@pytest.mark.parametrize("seed", range(60))
def test_condition_lists_match_the_scan(seed):
    """Available and forbidden sets equal the scan's, over random domains and cut points.

    The cut points are the interesting part: `numFirstBids`/`numLastBids` come from a
    time-varying formula and routinely fall outside the bid list at both ends, so they are
    drawn to include negatives, zero, and values past the end of the ranking.
    """
    rng = random.Random(seed)
    issues = random_domain(rng)
    pref = StubPreference(issues)
    n_bids = rng.choice([1, 2, 5, 40])
    bids = random_bids(rng, issues, n_bids)
    ordering = SimpleLinearOrdering(pref, bids)

    fast, oracle = SimilarityMap(pref), OracleSimilarityMap(pref)
    fast.update(ordering)
    oracle.update(ordering)

    for num_first, num_last in [
        (rng.randint(-3, n_bids + 3), rng.randint(-3, n_bids + 3)) for _ in range(6)
    ] + [(0, 0), (-1, -1), (n_bids, n_bids), (10**6, 10**6)]:
        fast.createConditionLists(num_first, num_last)
        oracle.createConditionLists(num_first, num_last)

        assert sets_of(fast) == sets_of(oracle), (num_first, num_last)


@pytest.mark.parametrize("seed", range(60))
def test_issue_value_importances_match_the_scan(seed):
    """`update` assigns each importance to the unit the scan would have chosen.

    Which unit matters when an issue's value list repeats a value: the scan stopped at the
    first, and so must the index. The issue importances derived from those lists, and
    their sort order, are compared too, since that order is what the offering strategy
    walks.
    """
    rng = random.Random(seed)
    issues = random_domain(rng)
    pref = StubPreference(issues)
    bids = random_bids(rng, issues, rng.choice([1, 3, 25]))
    ordering = SimpleLinearOrdering(pref, bids)

    fast, oracle = SimilarityMap(pref), OracleSimilarityMap(pref)
    fast.update(ordering)
    oracle.update(ordering)

    assert importance_lists(fast) == importance_lists(oracle)
    assert floats(fast.issueImpMap) == floats(oracle.issueImpMap)
    assert list(floats(fast.sortedIssueImpMap).items()) == list(
        floats(oracle.sortedIssueImpMap).items()
    )


def test_repeated_values_resolve_to_the_first_unit():
    """The explicit duplicate case, spelled out rather than left to the random search.

    An issue declaring the same value twice gets two units; the scan always credited the
    first and left the second empty, and the index has to do the same.
    """
    issue = NegologIssue("i0", ["a", "a", "b"])
    pref = StubPreference([issue])
    bids = [nenv.Bid({issue: "a"}), nenv.Bid({issue: "b"})]

    imp_map = SimilarityMap(pref)
    imp_map.update(SimpleLinearOrdering(pref, bids))

    units = imp_map.issueValueImpMap["i0"]
    assert [unit.importanceList for unit in units] == [[1.0], [], [2.0]]


def test_saturated_sets_are_the_full_walks_sets():
    """The early exit is a fixed point: stopping early yields the full walk's answer.

    With every value of every issue already recorded there is nothing left for the tail of
    the ranking to add, so the loop stops -- and the sets still hold every declared value.
    """
    issues = [NegologIssue("i0", ["a", "b"]), NegologIssue("i1", ["x", "y"])]
    pref = StubPreference(issues)
    rng = random.Random(0)
    bids = [
        nenv.Bid({issues[0]: rng.choice(["a", "b"]), issues[1]: rng.choice(["x", "y"])})
        for _ in range(500)
    ]
    ordering = SimpleLinearOrdering(pref, bids)

    fast, oracle = SimilarityMap(pref), OracleSimilarityMap(pref)
    fast.update(ordering)
    oracle.update(ordering)
    fast.createConditionLists(len(bids), len(bids))
    oracle.createConditionLists(len(bids), len(bids))

    assert sets_of(fast) == sets_of(oracle)
    assert fast.availableValues == {"i0": {"a", "b"}, "i1": {"x", "y"}}


def test_condition_lists_do_not_walk_the_whole_ranking_once_saturated():
    """Cost stops growing with the ranking once every value has been seen.

    This is the property the Travel domain needed: the sets saturate within the first
    handful of bids, so a ranking ten times longer must not cost ten times as much.
    """
    import time

    issues = [NegologIssue("i0", ["a", "b"]), NegologIssue("i1", ["x", "y"])]
    pref = StubPreference(issues)

    def cost(n_bids):
        rng = random.Random(1)
        bids = [
            nenv.Bid(
                {issues[0]: rng.choice(["a", "b"]), issues[1]: rng.choice(["x", "y"])}
            )
            for _ in range(n_bids)
        ]
        imp_map = SimilarityMap(pref)
        imp_map.update(SimpleLinearOrdering(pref, bids))

        t = time.perf_counter()
        for _ in range(50):
            imp_map.createConditionLists(n_bids, n_bids)
        return time.perf_counter() - t

    # Generous bound: the full walk is ~10x dearer at 10x the bids, the early exit is flat.
    assert cost(20000) < cost(2000) * 3

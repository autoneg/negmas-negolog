"""Equivalence tests for the presorted bid space in ``NegologPreferenceAdapter``.

``NegologPreferenceAdapter.bids`` is the hand-rolled utility inverse every NegoLog
agent sees: the full outcome space, evaluated and sorted descending by utility.
It now reuses NegMAS' presorted inverse when one already exists, and caches the
resulting order on the ufun so a second negotiation with the same ufun skips the
evaluate-and-sort entirely.

Those are pure performance changes, so every test here pins *behaviour*: the bid
list, the utilities, the tie order, and every accessor the vendored ``Preference``
derives from them must equal what the original algorithm produced. That original
algorithm is reproduced verbatim in ``reference_bids`` below and used as the
oracle -- an embedded reference rather than an import of the old module, so what
is being compared against is visible in the same file.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

# Add vendored NegoLog to path (bundled inside the package so it ships in the wheel)
NEGOLOG_PATH = (
    Path(__file__).parent.parent / "src" / "negmas_negolog" / "_vendor" / "NegoLog"
)
if str(NEGOLOG_PATH) not in sys.path:
    sys.path.insert(0, str(NEGOLOG_PATH))

from negmas.outcomes import make_issue, make_os  # noqa: E402
from negmas.preferences import LinearAdditiveUtilityFunction  # noqa: E402
from negmas.preferences.inv_ufun import (  # noqa: E402
    PresortingInverseUtilityFunction,
)
from negmas.preferences.value_fun import TableFun  # noqa: E402
from negmas.sao import SAOMechanism  # noqa: E402

from nenv import Bid  # noqa: E402
from nenv import Issue as NegologIssue  # noqa: E402

import negmas_negolog as nn  # noqa: E402
from negmas_negolog.common import NegologPreferenceAdapter  # noqa: E402


# --------------------------------------------------------------------------- #
# The oracle: the original ``bids`` algorithm, reproduced verbatim.
# --------------------------------------------------------------------------- #


def reference_bids(adapter: NegologPreferenceAdapter) -> list[Bid]:
    """The pre-change ``NegologPreferenceAdapter.bids`` implementation.

    Kept character-for-character equivalent to the code it replaced: enumerate
    every value combination, evaluate ``get_utility`` on each, then a single
    stable ``sorted(..., reverse=True)``. The stability is what fixes the order
    of equal-utility bids, which several agents index into positionally.
    """
    bids = [Bid({}, -1)]

    for issue in adapter._issues:
        new_bids = []
        for value_name in issue.values:
            for bid in bids:
                _bid = bid.copy()
                _bid[issue] = value_name
                new_bids.append(_bid)
        bids = new_bids

    for bid in bids:
        bid.utility = adapter.get_utility(bid)

    return sorted(bids, reverse=True)


def snapshot(bids: list[Bid]) -> list[tuple]:
    """A comparable view of a bid list.

    ``Bid.__hash__`` and ``__str__`` hash ``str(self.content)``, so the *insertion
    order* of the content dict is part of a bid's identity to the agents, not an
    implementation detail -- hence a list of pairs rather than a dict.
    """
    return [
        (tuple((issue.name, value) for issue, value in bid.content.items()), bid.utility)
        for bid in bids
    ]


# --------------------------------------------------------------------------- #
# Domain matrix
# --------------------------------------------------------------------------- #


class Domain:
    """A NegMAS scenario plus the NegoLog view of it the wrapper would build."""

    def __init__(
        self,
        name: str,
        issues: list[tuple[str, Any]],
        weight_fn: Callable[[random.Random, list], dict] | None = None,
        reserved_value: float = 0.0,
        seed: int = 7,
    ):
        self.name = name
        self.spec = issues
        self.reserved_value = reserved_value
        self.seed = seed
        self.weight_fn = weight_fn or (
            lambda rng, values: {v: rng.random() for v in values}
        )

        self.negmas_issues = [make_issue(spec, n) for n, spec in issues]
        self.outcome_space = make_os(self.negmas_issues)

        # Exactly what ``NegologNegotiatorWrapper._initialize_negolog_agent`` does.
        self.issue_names: list[str] = []
        self.negolog_issues: list[NegologIssue] = []
        self.native_values: dict[str, list] = {}
        for issue in self.negmas_issues:
            values = list(issue.all)
            self.issue_names.append(issue.name)
            self.native_values[issue.name] = values
            self.negolog_issues.append(
                NegologIssue(
                    issue.name,
                    [v if isinstance(v, str) else str(v) for v in values],
                )
            )

    @property
    def cardinality(self) -> int:
        return len(list(self.outcome_space.enumerate()))  # type: ignore[attr-defined]

    def ufun(
        self, scale: float = 1.0, seed: int | None = None
    ) -> LinearAdditiveUtilityFunction:
        """A fresh ufun. The same ``scale``/``seed`` always yields identical utilities.

        A different ``seed`` gives genuinely opposed preferences -- ``scale`` alone
        would only rescale one ranking, and two agents ranking the outcomes
        identically agree on the first round, which exercises almost nothing.
        """
        rng = random.Random(self.seed if seed is None else seed)
        n = len(self.negmas_issues)
        return LinearAdditiveUtilityFunction(
            values=[
                TableFun(
                    {k: scale * v for k, v in self.weight_fn(rng, list(i.all)).items()}
                )
                for i in self.negmas_issues
            ],
            weights=[1.0 / n] * n,
            outcome_space=self.outcome_space,
            reserved_value=self.reserved_value,
        )

    def opposed_ufun(self) -> LinearAdditiveUtilityFunction:
        """An opponent whose ranking is the mirror image of ``ufun()``'s.

        Mapping every value weight ``v`` to ``1 - v`` reverses the preference over
        each issue, so the two sides genuinely disagree. Merely rescaling one ufun
        leaves both agents ranking the outcomes identically -- they then agree on
        the first round, and a three-step trace exercises almost nothing.
        """
        base = self.ufun()
        return LinearAdditiveUtilityFunction(
            values=[
                TableFun({k: 1.0 - v for k, v in value_fun.mapping.items()})
                for value_fun in base.values
            ],
            weights=list(base.weights),
            outcome_space=self.outcome_space,
            reserved_value=self.reserved_value,
        )

    def adapter(self, ufun) -> NegologPreferenceAdapter:
        return NegologPreferenceAdapter(
            ufun=ufun,
            issues=self.negolog_issues,
            issue_names=self.issue_names,
            reservation_value=self.reserved_value,
            native_values=self.native_values,
        )

    def __repr__(self) -> str:
        return self.name


def _binary(rng, values):
    """Value weights of 0.0/1.0 -- forces many bids onto identical utilities."""
    return {v: float(rng.randint(0, 1)) for v in values}


def _constant(rng, values):
    """Every bid in the domain gets exactly the same utility."""
    return {v: 0.5 for v in values}


def _signed(rng, values):
    """Utilities straddling zero, so ``min``/``max`` are not 0/1."""
    return {v: rng.random() * 2.0 - 1.0 for v in values}


DOMAINS = [
    # Degenerate sizes: the vendored binary search has ``>= 1`` and
    # ``< len(bids) - 2`` guards that only differ at these cardinalities.
    Domain("single-outcome", [("only", ["a"])]),
    Domain("two-outcomes", [("i", ["a", "b"])]),
    Domain("three-outcomes", [("i", ["a", "b", "c"])]),
    # Value types: NegoLog issues hold strings, so anything non-string exercises
    # the native<->string translation on the way to the NegMAS ufun.
    Domain("categorical", [("food", ["fish", "beef", "tofu", "eggs"])]),
    Domain("cardinal-int", [("qty", [1, 2, 3, 4, 5])]),
    Domain("contiguous", [("n", 12)]),
    Domain("ordinal-float", [("price", [0.5, 1.5, 2.5, 3.5])]),
    Domain(
        "mixed-types",
        [("food", ["fish", "beef"]), ("qty", [1, 2, 3]), ("price", [0.5, 1.5])],
    ),
    # Utility shapes.
    Domain(
        "tie-heavy",
        [("a", ["p", "q", "r", "s"]), ("b", [0, 1, 2, 3]), ("c", ["x", "y"])],
        weight_fn=_binary,
    ),
    Domain(
        "all-equal-utilities",
        [("a", ["p", "q", "r"]), ("b", [0, 1, 2])],
        weight_fn=_constant,
    ),
    Domain(
        "signed-utilities",
        [("a", ["p", "q", "r"]), ("b", [0, 1, 2, 3])],
        weight_fn=_signed,
    ),
    # Reserved value high enough that most outcomes are irrational, which is what
    # a ``rational_only`` inverter partitions on.
    Domain(
        "high-reserved-value",
        [("a", ["p", "q", "r", "s"]), ("b", [0, 1, 2, 3])],
        reserved_value=0.9,
    ),
    # Many issues, and a domain big enough that the presort actually costs
    # something.
    Domain("many-issues", [(f"i{k}", ["lo", "hi"]) for k in range(8)]),
    Domain(
        "larger",
        [("a", ["p", "q", "r", "s"]), ("b", list(range(6))), ("c", ["x", "y", "z"]),
         ("d", [0.5, 1.5])],
    ),
]

DOMAINS_BY_NAME = {d.name: d for d in DOMAINS}


@pytest.fixture(params=DOMAINS, ids=lambda d: d.name)
def domain(request) -> Domain:
    return request.param


@pytest.fixture
def expected(domain: Domain) -> list[tuple]:
    """The oracle's bid list for a pristine ufun of this domain."""
    return snapshot(reference_bids(domain.adapter(domain.ufun())))


# --------------------------------------------------------------------------- #
# The bid list itself, on every path that can produce it
# --------------------------------------------------------------------------- #


def test_reference_matches_a_pristine_ufun(domain: Domain, expected):
    """Guards the oracle: two independent ufuns of a domain must agree."""
    assert snapshot(reference_bids(domain.adapter(domain.ufun()))) == expected


def test_bids_cold(domain: Domain, expected):
    """No inverse built, no cached order: the fallback must reproduce the oracle."""
    ufun = domain.ufun()
    adapter = domain.adapter(ufun)
    assert adapter._existing_inverse() is None
    assert adapter._cached_presorted() is None
    assert snapshot(adapter.bids) == expected


def test_cold_path_does_not_build_an_inverse(domain: Domain):
    """Building an inverter to read its utilities would cost more than not to."""
    ufun = domain.ufun()
    domain.adapter(ufun).bids
    assert getattr(ufun, "_cached_inverse", None) is None


@pytest.mark.parametrize("inverter_kwargs", [{}, {"rational_only": True}])
def test_bids_with_an_existing_inverse(domain: Domain, expected, inverter_kwargs):
    """Utilities read from a presorting inverter someone else already built."""
    ufun = domain.ufun()
    ufun.invert(PresortingInverseUtilityFunction, **inverter_kwargs)
    adapter = domain.adapter(ufun)
    assert isinstance(adapter._existing_inverse(), PresortingInverseUtilityFunction)
    assert adapter._inverse_utilities() is not None, "inverse unexpectedly rejected"
    assert snapshot(adapter.bids) == expected


def test_bids_from_the_order_cache(domain: Domain, expected):
    """Second adapter over the same ufun: order replayed, not recomputed."""
    ufun = domain.ufun()
    domain.adapter(ufun).bids
    second = domain.adapter(ufun)
    assert second._cached_presorted() is not None, "order cache did not populate"
    assert snapshot(second.bids) == expected


def test_bids_with_both_an_inverse_and_a_cached_order(domain: Domain, expected):
    """The interaction: an inverse present *and* the order already cached."""
    ufun = domain.ufun()
    ufun.invert(PresortingInverseUtilityFunction)
    first = domain.adapter(ufun)
    assert first._inverse_utilities() is not None
    assert snapshot(first.bids) == expected

    second = domain.adapter(ufun)
    assert second._cached_presorted() is not None
    assert snapshot(second.bids) == expected


def test_repeated_adapters_stay_identical(domain: Domain, expected):
    """Many negotiations over one ufun must not drift."""
    ufun = domain.ufun()
    for _ in range(4):
        assert snapshot(domain.adapter(ufun).bids) == expected


def test_bids_are_cached_per_adapter(domain: Domain):
    """``bids`` is a lazy property: the same adapter must return the same list."""
    adapter = domain.adapter(domain.ufun())
    assert adapter.bids is adapter.bids


def test_bid_objects_are_not_shared_between_adapters(domain: Domain):
    """Agents mutate the bids they are handed; sharing would leak across sessions."""
    ufun = domain.ufun()
    first = domain.adapter(ufun).bids
    second = domain.adapter(ufun).bids
    assert all(a is not b for a, b in zip(first, second))


def test_bid_count_matches_cardinality(domain: Domain):
    """``len(bids)`` is agent-visible logic, not just a bid source.

    ``NiceTitForTat`` feeds it into a ``domain_size > 10000`` branch, so a
    truncated or subsampled bid space would change which code path agents take.
    """
    assert len(domain.adapter(domain.ufun()).bids) == domain.cardinality


def test_bid_hashes_are_preserved(domain: Domain):
    """``Bid.__hash__`` hashes ``str(content)``, so key order must be preserved."""
    ufun = domain.ufun()
    reference = reference_bids(domain.adapter(domain.ufun()))
    for path in (domain.adapter(ufun), domain.adapter(ufun)):
        assert [hash(b) for b in path.bids] == [hash(b) for b in reference]


def test_tie_order_is_the_enumeration_order(domain: Domain):
    """Equal-utility bids must keep the order NegoLog's enumeration gave them.

    Several agents index the list positionally (``MICRO`` walks ``bids[i]``,
    ``RandomDance`` takes ``bids[-1]``), so a different tie order is a different
    offer even though the utilities match.
    """
    ufun = domain.ufun()
    enumeration = [
        tuple((i.name, v) for i, v in bid.content.items())
        for bid in domain.adapter(ufun)._enumerate_bids()
    ]
    position = {content: i for i, content in enumerate(enumeration)}
    for adapter in (domain.adapter(ufun), domain.adapter(ufun)):
        bids = adapter.bids
        for earlier, later in zip(bids, bids[1:]):
            if earlier.utility == later.utility:
                a = tuple((i.name, v) for i, v in earlier.content.items())
                b = tuple((i.name, v) for i, v in later.content.items())
                assert position[a] < position[b], "tie order changed"


# --------------------------------------------------------------------------- #
# Everything the vendored ``Preference`` derives from the bid list
# --------------------------------------------------------------------------- #


def _utility_targets(reference: list[Bid], n: int = 200) -> list[float]:
    """A dense sweep over (and beyond) the domain's utility range."""
    lo, hi = reference[-1].utility, reference[0].utility
    span = (hi - lo) or 1.0
    return [lo - span * 0.25 + (span * 1.5) * k / (n - 1) for k in range(n)] + [lo, hi]


@pytest.fixture
def paths(domain: Domain):
    """One ready adapter per code path that can produce the bid list."""
    ufun = domain.ufun()
    cold = domain.adapter(ufun)
    cold.bids  # populates the order cache on `ufun`

    with_inverse_ufun = domain.ufun()
    with_inverse_ufun.invert(PresortingInverseUtilityFunction)
    with_inverse = domain.adapter(with_inverse_ufun)
    assert with_inverse._inverse_utilities() is not None, "inverse path not taken"

    cached_order = domain.adapter(ufun)
    assert cached_order._cached_presorted() is not None, "order-cache path not taken"

    return {
        "cold": cold,
        "with-inverse": with_inverse,
        "cached-order": cached_order,
    }


def test_get_bid_at_dense_sweep(domain: Domain, paths):
    reference = reference_bids(domain.adapter(domain.ufun()))
    targets = _utility_targets(reference)
    oracle = domain.adapter(domain.ufun())
    oracle._bids = list(reference)
    for name, adapter in paths.items():
        for target in targets:
            assert snapshot([adapter.get_bid_at(target)]) == snapshot(
                [oracle.get_bid_at(target)]
            ), f"{name} disagrees at target {target}"


def test_get_bids_at_range(domain: Domain, paths):
    reference = reference_bids(domain.adapter(domain.ufun()))
    oracle = domain.adapter(domain.ufun())
    oracle._bids = list(reference)
    bounds = _utility_targets(reference, n=24)
    for name, adapter in paths.items():
        for lower in bounds:
            for upper in bounds:
                assert snapshot(adapter.get_bids_at_range(lower, upper)) == snapshot(
                    oracle.get_bids_at_range(lower, upper)
                ), f"{name} disagrees on range ({lower}, {upper})"


def test_get_bids_at_window(domain: Domain, paths):
    reference = reference_bids(domain.adapter(domain.ufun()))
    oracle = domain.adapter(domain.ufun())
    oracle._bids = list(reference)
    for name, adapter in paths.items():
        for target in _utility_targets(reference, n=24):
            for width in (0.0, 0.01, 0.1, 0.5):
                assert snapshot(adapter.get_bids_at(target, width, width)) == snapshot(
                    oracle.get_bids_at(target, width, width)
                ), f"{name} disagrees on window ({target}, {width})"


def test_extreme_bids(domain: Domain, paths):
    reference = reference_bids(domain.adapter(domain.ufun()))
    for name, adapter in paths.items():
        assert snapshot([adapter.max_util_bid]) == snapshot([reference[0]]), name
        assert snapshot([adapter.min_util_bid]) == snapshot([reference[-1]]), name


def test_get_random_bid_stays_in_range(domain: Domain, paths):
    """RNG-driven, so pinned as a property rather than as a sequence."""
    reference = reference_bids(domain.adapter(domain.ufun()))
    allowed = {snapshot([bid])[0] for bid in reference}
    for name, adapter in paths.items():
        random.seed(4)
        for _ in range(25):
            bid = adapter.get_random_bid()
            assert snapshot([bid])[0] in allowed, f"{name} returned a foreign bid"


def test_utilities_match_get_utility(domain: Domain, paths):
    """The cached utilities must still be what evaluating the ufun would give."""
    for name, adapter in paths.items():
        for bid in adapter.bids:
            assert bid.utility == adapter.get_utility(bid), name


def test_bid_to_outcome_round_trips(domain: Domain):
    """The hot-path conversion rewrite must map every bid to its NegMAS outcome."""
    adapter = domain.adapter(domain.ufun())
    outcomes = set(domain.outcome_space.enumerate())  # type: ignore[attr-defined]
    converted = [adapter._bid_to_outcome(bid) for bid in adapter.bids]
    assert set(converted) == outcomes
    assert len(set(converted)) == len(converted)
    for bid, outcome in zip(adapter.bids, converted):
        assert adapter._outcome_to_bid(outcome).content == bid.content


# --------------------------------------------------------------------------- #
# Cache invalidation: the order cache outlives the adapter, so it has to be
# refused whenever it could be stale.
# --------------------------------------------------------------------------- #


def test_stale_order_cache_is_refused_after_the_ufun_is_rescaled():
    """A ufun rescaled in place between negotiations must not be served old numbers."""
    domain = DOMAINS_BY_NAME["larger"]
    ufun = domain.ufun()
    domain.adapter(ufun).bids
    assert domain.adapter(ufun)._cached_presorted() is not None

    ufun.values = [
        TableFun({k: 0.5 * v for k, v in value_fun.mapping.items()})
        for value_fun in ufun.values
    ]
    rescaled = snapshot(reference_bids(domain.adapter(domain.ufun(scale=0.5))))
    assert snapshot(domain.adapter(ufun).bids) == rescaled


def test_non_stationary_ufun_bypasses_both_caches(domain: Domain, expected):
    ufun = domain.ufun()
    adapter = domain.adapter(ufun)
    adapter.bids  # would populate the cache for a stationary ufun

    later = domain.adapter(ufun)
    later._ufun.is_stationary = lambda: False
    assert later._reuse_allowed() is False
    assert later._cached_presorted() is None
    assert later._inverse_utilities() is None
    assert snapshot(later.bids) == expected


def test_a_modified_ufun_bypasses_both_caches(domain: Domain, expected):
    ufun = domain.ufun()
    domain.adapter(ufun).bids

    later = domain.adapter(ufun)
    if not hasattr(type(later._ufun), "modified"):
        pytest.skip("this NegMAS release has no `modified` flag")
    later._ufun.mark_modified()  # type: ignore[attr-defined]
    assert later._reuse_allowed() is False
    assert snapshot(later.bids) == expected


def test_a_foreign_inverter_is_ignored_not_misread(domain: Domain, expected):
    """Only the presorting family holds raw per-outcome utilities in these arrays."""

    class Foreign:
        outcomes = list(domain.outcome_space.enumerate())  # type: ignore[attr-defined]
        utils = [0.0] * domain.cardinality

    ufun = domain.ufun()
    object.__setattr__(ufun, "_cached_inverse", Foreign())
    adapter = domain.adapter(ufun)
    assert adapter._existing_inverse() is None
    assert adapter._inverse_utilities() is None
    assert snapshot(adapter.bids) == expected


def test_an_inverse_that_does_not_cover_the_space_is_rejected(domain: Domain, expected):
    if domain.cardinality < 2:
        pytest.skip("nothing to truncate in a one-outcome domain")
    ufun = domain.ufun()
    inverse = ufun.invert(PresortingInverseUtilityFunction)
    inverse.outcomes = inverse.outcomes[:-1]  # type: ignore[attr-defined]
    inverse.utils = inverse.utils[:-1]  # type: ignore[attr-defined]
    adapter = domain.adapter(ufun)
    assert adapter._inverse_utilities() is None
    assert snapshot(adapter.bids) == expected


def test_an_order_cache_of_the_wrong_length_is_rejected(domain: Domain, expected):
    from array import array

    ufun = domain.ufun()
    adapter = domain.adapter(ufun)
    adapter.bids
    cache = getattr(ufun, "_negolog_presorted")
    key = next(iter(cache))
    cache[key] = (array("l", [0]), array("d", [0.0]))

    later = domain.adapter(ufun)
    if domain.cardinality != 1:
        assert later._bids_from_presorted(cache[key]) is None
    assert snapshot(later.bids) == expected


def test_duplicate_issue_names_resolve_to_the_first_issue():
    """NegMAS allows two issues to share a name, and ``nenv.Issue`` keys on the name.

    The original ``_bid_to_outcome`` scanned ``_issues`` linearly and stopped at the
    first name match. The dict that replaced that scan must resolve the same way
    (first wins) or such a domain silently maps to different outcomes. The domain is
    degenerate either way -- what is pinned is that it stays degenerate identically.
    """
    negmas_issues = [make_issue(["a", "b"], "dup"), make_issue(["a", "b"], "dup")]
    negolog_issues = [NegologIssue("dup", ["a", "b"]), NegologIssue("dup", ["a", "b"])]
    ufun = LinearAdditiveUtilityFunction(
        values=[TableFun({"a": 1.0, "b": 0.0}), TableFun({"a": 0.25, "b": 0.75})],
        weights=[0.5, 0.5],
        outcome_space=make_os(negmas_issues),
        reserved_value=0.0,
    )

    def build():
        return NegologPreferenceAdapter(
            ufun=ufun,
            issues=negolog_issues,
            issue_names=["dup", "dup"],
            reservation_value=0.0,
            native_values={"dup": ["a", "b"]},
        )

    adapter = build()
    assert adapter._issue_by_name["dup"] is negolog_issues[0], "first issue must win"

    def original_scan(a, bid):
        """``_bid_to_outcome`` as it was: a linear scan stopping at the first match."""
        values = []
        for issue_name in a._issue_names:
            for issue in a._issues:
                if issue.name == issue_name:
                    value = bid[issue]
                    values.append(a._to_native[issue_name].get(value, value))
                    break
        return tuple(values)

    for bid in adapter._enumerate_bids():
        assert adapter._bid_to_outcome(bid) == original_scan(adapter, bid)

    oracle = snapshot(reference_bids(build()))
    assert snapshot(build().bids) == oracle
    assert snapshot(build().bids) == oracle, "order cache diverges on this domain"


def test_domains_that_only_stringify_alike_do_not_share_a_cache_entry():
    """``[0, 1]`` and ``["0", "1"]`` give the same NegoLog strings, not the same ufun."""
    native = Domain("native-ints", [("i", [0, 1, 2, 3])])
    ufun = native.ufun()

    # A second adapter over the SAME ufun whose NegoLog values stringify
    # identically but which maps them to different NegMAS values.
    reversed_natives = {"i": [3, 2, 1, 0]}
    flipped = NegologPreferenceAdapter(
        ufun=ufun,
        issues=native.negolog_issues,
        issue_names=native.issue_names,
        reservation_value=0.0,
        native_values=reversed_natives,
    )
    straight = native.adapter(ufun)
    assert straight._domain_signature() != flipped._domain_signature()

    straight.bids
    flipped.bids
    # Pin the keying itself, not only its observable effect: with a single-entry
    # cache the staleness spot-check would usually reject the wrong entry and
    # recompute, hiding the bug until two domains happened to agree at the four
    # sampled indices.
    cache = getattr(ufun, "_negolog_presorted")
    assert len(cache) == 2, f"both domains collapsed onto one cache entry: {cache}"
    # ...and that each adapter *reads back* its own entry. Checking only the bids
    # would hide a mis-keyed read: the staleness spot-check usually rejects the
    # wrong entry and recomputes, so the bug would stay invisible until two
    # domains happened to agree at the four sampled indices.
    for adapter in (straight, flipped):
        assert adapter._cached_presorted() is cache[adapter._domain_signature()]
    assert snapshot(flipped.bids) == snapshot(reference_bids(flipped))
    assert snapshot(straight.bids) == snapshot(reference_bids(straight))


# --------------------------------------------------------------------------- #
# Wrapper level: real negotiations, every agent, cold then cache-hit.
# --------------------------------------------------------------------------- #

WRAPPERS = sorted(
    name
    for name in nn.__all__
    if isinstance(getattr(nn, name, None), type)
    and issubclass(getattr(nn, name), nn.NegologNegotiatorWrapper)
    and getattr(nn, name) is not nn.NegologNegotiatorWrapper
)


SEED = 20240101


def reseed() -> None:
    """Reset every RNG a NegoLog agent might draw from.

    Both are needed: the agents use the module-level ``random`` functions and
    some (``HardHeaded``) reach for NumPy. Note that constructing a NegMAS ufun
    or negotiator *also* consumes the global RNG (ids are randomly named), so
    reseeding has to happen after those objects exist and immediately before the
    run being compared -- otherwise two runs start from different RNG states and
    the comparison measures the harness, not the code.
    """
    random.seed(SEED)
    try:
        import numpy as np

        np.random.seed(SEED)
    except ImportError:
        pass


def freeze_mechanism_clock(monkeypatch=None) -> None:
    """Stop the NegMAS mechanism's wall-clock from perturbing the RNG stream.

    ``Mechanism.step`` draws an extra ``random.random()`` the first time the
    negotiation crosses a whole wall-clock second (the ``pend_per_second``
    bookkeeping at ``mechanisms.py``). That draw shifts the global RNG stream, and
    agents that lean on it -- ``AgentKN`` calls ``get_random_bid`` dozens of times
    per round -- then follow a different sequence of offers. So *how fast the code
    runs* is observable in a trace, which makes any before/after comparison of a
    performance change meaningless unless the clock is pinned. These negotiations
    are step-limited (``n_steps`` with no ``time_limit``), so reporting 0.0 elapsed
    changes nothing else about how they proceed.

    ``monkeypatch`` is required from tests: the patch is on ``Mechanism`` itself, so
    an unscoped assignment would leak into every later test in the session.
    Standalone scripts may omit it.
    """
    from negmas.mechanisms import Mechanism

    frozen = property(lambda self: 0.0)
    if monkeypatch is None:
        Mechanism.time = frozen  # type: ignore[assignment]
    else:
        monkeypatch.setattr(Mechanism, "time", frozen)


@pytest.fixture
def seeded_random(monkeypatch):
    """Make the NegoLog agents deterministic.

    Several of them build their own ``random.Random()`` with no seed (see
    ``NiceTitForTat.py:43``), which no amount of module-level seeding reaches, so
    the class itself is pinned for the duration of the test.
    """
    real = random.Random

    class Seeded(real):
        def __init__(self, *args, **kwargs):
            super().__init__(SEED)

    monkeypatch.setattr(random, "Random", Seeded)
    freeze_mechanism_clock(monkeypatch)
    reseed()
    return real


def _run(domain: Domain, cls, ufun_a, ufun_b, n_steps: int = 30):
    mechanism = SAOMechanism(outcome_space=domain.outcome_space, n_steps=n_steps)
    mechanism.add(cls(ufun=ufun_a, name="A"))
    mechanism.add(nn.BoulwareAgent(ufun=ufun_b, name="B"))
    mechanism.run()
    return [
        (state.step, state.current_offer, state.current_proposer_agent)
        for state in mechanism.history
    ] + [("agreement", mechanism.agreement)]


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_a_second_negotiation_over_the_same_ufun_is_identical(
    wrapper, seeded_random, monkeypatch
):
    """The order cache must not change what any agent does.

    The first negotiation populates it and the second replays it, so identical
    traces are what says the replay reproduces the presort exactly -- for all
    25 agents, through the real wrapper, mechanism and opponent-model paths.
    """
    domain = DOMAINS_BY_NAME["larger"]
    cls = getattr(nn, wrapper)
    ufun_a, ufun_b = domain.ufun(), domain.opposed_ufun()

    reseed()
    first = _run(domain, cls, ufun_a, ufun_b)

    replays = []
    original = NegologPreferenceAdapter._bids_from_presorted

    def spy(self, presorted):
        result = original(self, presorted)
        replays.append(result is not None)
        return result

    monkeypatch.setattr(NegologPreferenceAdapter, "_bids_from_presorted", spy)

    reseed()
    second = _run(domain, cls, ufun_a, ufun_b)
    assert first == second
    # The opponent is Boulware, which always reaches for the bid space, so the
    # replay path must have run at least once and must not have been refused.
    assert replays and all(replays), f"cached order not replayed: {replays}"


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_a_prebuilt_inverse_does_not_change_what_an_agent_does(wrapper, seeded_random):
    """Reading utilities off an existing inverse must be invisible to the agent."""
    domain = DOMAINS_BY_NAME["larger"]
    cls = getattr(nn, wrapper)

    plain_a, plain_b = domain.ufun(), domain.opposed_ufun()
    reseed()
    plain = _run(domain, cls, plain_a, plain_b)

    inverted_a, inverted_b = domain.ufun(), domain.opposed_ufun()
    inverted_a.invert(PresortingInverseUtilityFunction)
    inverted_b.invert(PresortingInverseUtilityFunction)
    reseed()
    assert _run(domain, cls, inverted_a, inverted_b) == plain


@pytest.mark.parametrize(
    "domain_name", ["single-outcome", "two-outcomes", "contiguous", "mixed-types",
                    "tie-heavy", "high-reserved-value", "many-issues"]
)
def test_negotiations_run_on_every_domain_shape(domain_name, seeded_random):
    """The domain shapes above, driven through the wrapper rather than the adapter."""
    domain = DOMAINS_BY_NAME[domain_name]
    ufun_a, ufun_b = domain.ufun(), domain.opposed_ufun()
    outcomes = set(domain.outcome_space.enumerate())  # type: ignore[attr-defined]

    reseed()
    first = _run(domain, nn.MICROAgent, ufun_a, ufun_b)
    reseed()
    second = _run(domain, nn.MICROAgent, ufun_a, ufun_b)
    assert first == second

    for step in first:
        offer = step[1]
        assert offer is None or offer in outcomes, "offered outside the outcome space"

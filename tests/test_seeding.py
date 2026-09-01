"""
Tests for hooking this package's private RNGs onto NegMAS's global seed.

These tests verify that:
1. Nothing is patched until NegMAS actually applies a seed
2. Unseeded ``random.Random()`` instances become reproducible once it does
3. Each such instance still gets its own distinct stream
4. An explicitly seeded ``random.Random(x)`` keeps its usual meaning
5. A wrapped agent's own private RNG replays under the same seed
"""

import random

import pytest
from negmas.outcomes import make_issue, make_os
from negmas.preferences import LinearAdditiveUtilityFunction
from negmas.sao import SAOMechanism

from negmas_negolog import NiceTitForTat, HardHeaded
from negmas_negolog import _seeding

seed_all = pytest.importorskip("negmas.helpers.rand").seed_all


@pytest.fixture(autouse=True)
def restore_random():
    """Undo the process-wide patch so it cannot leak into other test modules.

    ``_seeding`` swaps `random.Random` for the rest of the process once a seed
    is applied, and ``test_bids_equivalence`` patches the same attribute and
    compares negotiation traces, so leaving it installed would make the outcome
    of that module depend on test ordering.
    """
    saved = random.Random
    yield
    random.Random = saved


def test_nothing_is_patched_without_a_seed():
    """With no seed in effect the class is untouched, so behaviour is unchanged."""
    random.Random = _seeding._Random
    assert seed_all(None) is None
    assert random.Random is _seeding._Random


def test_unseeded_randoms_are_reproducible():
    """The whole point: ``random.Random()`` now replays under the same seed."""
    seed_all(42)
    first = [random.Random().random() for _ in range(5)]
    seed_all(42)
    second = [random.Random().random() for _ in range(5)]
    assert first == second


def test_each_instance_gets_its_own_stream():
    """HardHeaded holds two RNGs at once; they must not be identical."""
    seed_all(42)
    assert len(set(random.Random().random() for _ in range(5))) == 5


def test_a_different_seed_gives_a_different_stream():
    seed_all(42)
    first = [random.Random().random() for _ in range(5)]
    seed_all(43)
    assert [random.Random().random() for _ in range(5)] != first


def test_an_explicit_seed_is_still_honoured():
    """``random.Random(7)`` elsewhere in the process keeps meaning 7."""
    expected = _seeding._Random(7).random()
    seed_all(42)
    assert random.Random(7).random() == expected
    assert random.Random(x=7).random() == expected


def _domain():
    issues = [
        make_issue(values=["low", "medium", "high"], name="price"),
        make_issue(values=["1", "2", "3"], name="quantity"),
        make_issue(values=["fast", "normal", "slow"], name="delivery"),
    ]
    return make_os(issues)


def _ufun(outcome_space, reverse=False):
    high, low = (0.0, 1.0) if reverse else (1.0, 0.0)
    return LinearAdditiveUtilityFunction(
        values={
            "price": {"low": high, "medium": 0.5, "high": low},
            "quantity": {"1": low, "2": 0.5, "3": high},
            "delivery": {"fast": high, "normal": 0.5, "slow": low},
        },
        weights={"price": 0.5, "quantity": 0.3, "delivery": 0.2},
        outcome_space=outcome_space,
    )


def _private_rng_stream():
    """The stream of ``NiceTitForTat``'s own RNG, once the agent is built.

    ``NiceTitForTat.__init__`` does ``self.random100 = random.Random()``, one of
    the fourteen unseeded constructions this module exists to reach, so its
    stream is a direct read of whether the hook worked.
    """
    outcome_space = _domain()
    mechanism = SAOMechanism(outcome_space=outcome_space, n_steps=20)
    agent = NiceTitForTat(ufun=_ufun(outcome_space), name="A")
    mechanism.add(agent)
    mechanism.add(HardHeaded(ufun=_ufun(outcome_space, reverse=True), name="B"))
    mechanism.step()  # runs on_negotiation_start, which builds the NegoLog agent
    inner = agent._negolog_agent
    assert inner is not None, "the NegoLog agent was never initialised"
    return [inner.random100.random() for _ in range(5)]


def test_an_agents_private_rng_is_reproducible():
    """End to end: the same seed rebuilds the same private RNG stream."""
    seed_all(42)
    first = _private_rng_stream()
    seed_all(42)
    assert _private_rng_stream() == first


def test_an_agents_private_rng_is_unreachable_without_the_hook():
    """Guards the test above from passing for the wrong reason.

    Pinning the global generators is exactly what does *not* reach a private
    ``random.Random()``, so with the patch backed out the stream must differ.
    """
    random.Random = _seeding._Random
    random.seed(42)
    first = _private_rng_stream()
    random.Random = _seeding._Random
    random.seed(42)
    assert _private_rng_stream() != first

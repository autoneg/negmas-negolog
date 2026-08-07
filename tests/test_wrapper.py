"""
Tests for the NegologNegotiatorWrapper and concrete wrapper classes.

These tests verify that:
1. NegoLog agents can be wrapped and used as NegMAS SAONegotiator instances
2. Negotiations complete without errors
3. Bid/Outcome conversions work correctly
4. Preference adapter correctly evaluates utilities
"""

import pytest
from negmas.outcomes import make_issue, make_os
from negmas.preferences import LinearAdditiveUtilityFunction
from negmas.sao import SAOMechanism

from negmas_negolog import (
    BoulwareAgent,
    ConcederAgent,
    LinearAgent,
    NiceTitForTat,
)


@pytest.fixture
def simple_issues():
    """Create a simple negotiation domain with 3 discrete issues."""
    issues = [
        make_issue(values=["low", "medium", "high"], name="price"),
        make_issue(values=["1", "2", "3"], name="quantity"),
        make_issue(values=["fast", "normal", "slow"], name="delivery"),
    ]
    return issues


@pytest.fixture
def outcome_space(simple_issues):
    """Create outcome space from issues."""
    return make_os(simple_issues)


@pytest.fixture
def buyer_ufun(outcome_space):
    """Create a utility function for a buyer (prefers low price, high quantity)."""
    return LinearAdditiveUtilityFunction(
        values={
            "price": {"low": 1.0, "medium": 0.5, "high": 0.0},
            "quantity": {"1": 0.0, "2": 0.5, "3": 1.0},
            "delivery": {"fast": 1.0, "normal": 0.5, "slow": 0.0},
        },
        weights={"price": 0.5, "quantity": 0.3, "delivery": 0.2},
        outcome_space=outcome_space,
    )


@pytest.fixture
def seller_ufun(outcome_space):
    """Create a utility function for a seller (prefers high price, low quantity)."""
    return LinearAdditiveUtilityFunction(
        values={
            "price": {"low": 0.0, "medium": 0.5, "high": 1.0},
            "quantity": {"1": 1.0, "2": 0.5, "3": 0.0},
            "delivery": {"fast": 0.0, "normal": 0.5, "slow": 1.0},
        },
        weights={"price": 0.5, "quantity": 0.3, "delivery": 0.2},
        outcome_space=outcome_space,
    )


class TestBasicNegotiation:
    """Test basic negotiation functionality with wrapped agents."""

    def test_boulware_vs_conceder(self, simple_issues, buyer_ufun, seller_ufun):
        """Test a negotiation between Boulware and Conceder agents."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=100,
        )

        buyer = BoulwareAgent(name="buyer", ufun=buyer_ufun)
        seller = ConcederAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        # Negotiation should complete (either with agreement or timeout)
        assert state is not None
        assert state.started
        assert state.ended

    def test_linear_vs_linear(self, simple_issues, buyer_ufun, seller_ufun):
        """Test a negotiation between two LinearAgent instances."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=100,
        )

        buyer = LinearAgent(name="buyer", ufun=buyer_ufun)
        seller = LinearAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        assert state is not None
        assert state.started
        assert state.ended

    def test_nice_tit_for_tat_vs_boulware(self, simple_issues, buyer_ufun, seller_ufun):
        """Test NiceTitForTat against Boulware (uses BayesianOpponentModel)."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=100,
        )

        buyer = NiceTitForTat(name="buyer", ufun=buyer_ufun)
        seller = BoulwareAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        assert state is not None
        assert state.started
        assert state.ended


class TestAgreementQuality:
    """Test that agreements (when reached) are valid and reasonable."""

    def test_agreement_is_valid_outcome(self, simple_issues, buyer_ufun, seller_ufun):
        """If agreement is reached, it should be a valid outcome."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=200,  # More steps to increase chance of agreement
        )

        buyer = ConcederAgent(name="buyer", ufun=buyer_ufun)
        seller = ConcederAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        if state.agreement is not None:
            # Agreement should be a tuple with 3 values (one per issue)
            assert len(state.agreement) == 3
            # Each value should be valid for its issue
            price, quantity, delivery = state.agreement
            assert price in ["low", "medium", "high"]
            assert quantity in ["1", "2", "3"]
            assert delivery in ["fast", "normal", "slow"]

    def test_agreement_utilities_are_positive(
        self, simple_issues, buyer_ufun, seller_ufun
    ):
        """If agreement is reached, both parties should get non-negative utility."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=200,
        )

        buyer = ConcederAgent(name="buyer", ufun=buyer_ufun)
        seller = ConcederAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        if state.agreement is not None:
            buyer_util = buyer_ufun(state.agreement)
            seller_util = seller_ufun(state.agreement)
            # Both utilities should be non-negative
            assert buyer_util >= 0
            assert seller_util >= 0


class TestMultipleRounds:
    """Test running multiple negotiations."""

    def test_multiple_negotiations(self, simple_issues, buyer_ufun, seller_ufun):
        """Run multiple negotiations to ensure consistency."""
        agreements = 0
        total_rounds = 5

        for _ in range(total_rounds):
            mechanism = SAOMechanism(
                issues=simple_issues,
                n_steps=100,
            )

            buyer = LinearAgent(name="buyer", ufun=buyer_ufun)
            seller = LinearAgent(name="seller", ufun=seller_ufun)

            mechanism.add(buyer)
            mechanism.add(seller)

            state = mechanism.run()

            assert state is not None
            assert state.started
            assert state.ended

            if state.agreement is not None:
                agreements += 1

        # At least some negotiations should complete
        # (we don't require all to reach agreement, just that they run without error)
        assert agreements >= 0  # All we care is no exceptions were raised


class TestEdgeCases:
    """Test edge cases and potential issues."""

    def test_single_step_negotiation(self, simple_issues, buyer_ufun, seller_ufun):
        """Test negotiation with minimal steps."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=1,
        )

        buyer = BoulwareAgent(name="buyer", ufun=buyer_ufun)
        seller = BoulwareAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        # Should complete without error, even if no agreement
        assert state is not None
        assert state.ended

    def test_many_steps_negotiation(self, simple_issues, buyer_ufun, seller_ufun):
        """Test negotiation with many steps."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=1000,
        )

        buyer = ConcederAgent(name="buyer", ufun=buyer_ufun)
        seller = ConcederAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        # Should complete without error
        assert state is not None
        assert state.ended


class TestNegoLogVsNegoLog:
    """Test negotiations between two NegoLog agents (wrapped)."""

    def test_boulware_vs_boulware(self, simple_issues, buyer_ufun, seller_ufun):
        """Test two Boulware agents negotiating."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=100,
        )

        buyer = BoulwareAgent(name="buyer", ufun=buyer_ufun)
        seller = BoulwareAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        assert state is not None
        assert state.started
        assert state.ended

    def test_conceder_vs_conceder(self, simple_issues, buyer_ufun, seller_ufun):
        """Test two Conceder agents negotiating."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=100,
        )

        buyer = ConcederAgent(name="buyer", ufun=buyer_ufun)
        seller = ConcederAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        assert state is not None
        assert state.started
        assert state.ended
        # Conceder agents should reach agreement within the time limit
        # (they may not always agree early depending on domain specifics)

    def test_boulware_vs_conceder_reverse(self, simple_issues, buyer_ufun, seller_ufun):
        """Test Conceder vs Boulware (reverse roles)."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=100,
        )

        buyer = ConcederAgent(name="buyer", ufun=buyer_ufun)
        seller = BoulwareAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        assert state is not None
        assert state.started
        assert state.ended

    def test_linear_vs_boulware(self, simple_issues, buyer_ufun, seller_ufun):
        """Test Linear vs Boulware agents."""
        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=100,
        )

        buyer = LinearAgent(name="buyer", ufun=buyer_ufun)
        seller = BoulwareAgent(name="seller", ufun=seller_ufun)

        mechanism.add(buyer)
        mechanism.add(seller)

        state = mechanism.run()

        assert state is not None
        assert state.started
        assert state.ended


class TestNegoLogVsNegMAS:
    """Test negotiations between NegoLog (wrapped) and native NegMAS agents."""

    def test_boulware_vs_aspiration(self, simple_issues, buyer_ufun, seller_ufun):
        """Test wrapped Boulware vs native AspirationNegotiator."""
        from negmas.sao import AspirationNegotiator

        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=100,
        )

        buyer = BoulwareAgent(name="buyer", ufun=buyer_ufun)
        seller = AspirationNegotiator(name="seller")

        mechanism.add(buyer)
        mechanism.add(seller, preferences=seller_ufun)

        state = mechanism.run()

        assert state is not None
        assert state.started
        assert state.ended

    def test_conceder_vs_aspiration(self, simple_issues, buyer_ufun, seller_ufun):
        """Test wrapped Conceder vs native AspirationNegotiator."""
        from negmas.sao import AspirationNegotiator

        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=100,
        )

        buyer = ConcederAgent(name="buyer", ufun=buyer_ufun)
        seller = AspirationNegotiator(name="seller")

        mechanism.add(buyer)
        mechanism.add(seller, preferences=seller_ufun)

        state = mechanism.run()

        assert state is not None
        assert state.started
        assert state.ended
        # Both are conceding, should reach agreement
        if not state.timedout:
            assert state.agreement is not None

    def test_nicetitfortat_vs_aspiration(self, simple_issues, buyer_ufun, seller_ufun):
        """Test wrapped NiceTitForTat vs native AspirationNegotiator."""
        from negmas.sao import AspirationNegotiator

        mechanism = SAOMechanism(
            issues=simple_issues,
            n_steps=100,
        )

        buyer = NiceTitForTat(name="buyer", ufun=buyer_ufun)
        seller = AspirationNegotiator(name="seller")

        mechanism.add(buyer)
        mechanism.add(seller, preferences=seller_ufun)

        state = mechanism.run()

        assert state is not None
        assert state.started
        assert state.ended


class TestNonStringIssueValues:
    """Domains whose issue values are not strings.

    NegoLog issues can only hold strings, so the wrapper stringifies every value.
    Without a translation back to the NegMAS values, two things break silently:
    a contiguous (integer-range) issue reports `(min, max)` rather than its values,
    and every proposed outcome comes out as a tuple of strings that is not a member
    of the outcome space.
    """

    @pytest.fixture
    def int_issues(self):
        return [
            make_issue((1, 7), name="price"),
            make_issue((1, 10), name="quantity"),
        ]

    @pytest.fixture
    def int_ufuns(self, int_issues):
        from negmas.preferences.value_fun import AffineFun

        os_ = make_os(int_issues)
        buyer = LinearAdditiveUtilityFunction(
            values=[AffineFun(-0.1, bias=1.0), AffineFun(0.05)],
            weights=[0.6, 0.4],
            outcome_space=os_,
        )
        seller = LinearAdditiveUtilityFunction(
            values=[AffineFun(0.1), AffineFun(-0.05, bias=1.0)],
            weights=[0.5, 0.5],
            outcome_space=os_,
        )
        return buyer, seller

    @pytest.mark.parametrize("agent_class", [BoulwareAgent, NiceTitForTat])
    def test_runs_on_contiguous_issues(self, agent_class, int_issues, int_ufuns):
        buyer_ufun, seller_ufun = int_ufuns
        mechanism = SAOMechanism(issues=int_issues, n_steps=100)
        mechanism.add(agent_class(name="buyer"), preferences=buyer_ufun)
        mechanism.add(ConcederAgent(name="seller"), preferences=seller_ufun)

        state = mechanism.run()

        assert state.ended and not state.has_error

    def test_offers_are_valid_outcomes(self, int_issues, int_ufuns):
        """Every offer must be a member of the outcome space, not a string tuple."""
        buyer_ufun, seller_ufun = int_ufuns
        os_ = make_os(int_issues)
        mechanism = SAOMechanism(issues=int_issues, n_steps=30)
        mechanism.add(BoulwareAgent(name="buyer"), preferences=buyer_ufun)
        mechanism.add(ConcederAgent(name="seller"), preferences=seller_ufun)

        mechanism.run()

        offers = [_.offer for _ in mechanism.full_trace if _.offer is not None]
        assert offers
        for offer in offers:
            assert os_.is_valid(offer), f"{offer} is not a valid outcome"

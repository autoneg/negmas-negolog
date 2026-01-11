from typing import Optional
import nenv
from nenv import Action, Bid
from agents.NiceTitForTat.helpers.BidHistory import BidDetails, BidHistory


class ParsCatAgent(nenv.AbstractAgent):
    """
    ANAC 2016 individual utility category runner-up. [Aydogan2021]_

    .. [Aydogan2021] Reyhan Aydoğan, Katsuhide Fujita, Tim Baarslag, Catholijn M. Jonker, and Takayuki Ito. ANAC 2017: Repeated multilateral negotiation league. In Advances in Auto- mated Negotiations, pages 101–115, Singapore, 2021. Springer Singapore.

    .. note::
        This description was AI-generated based on the referenced paper and source code analysis.

    """

    t: float
    maxBid: nenv.Bid
    otherAgentsBidHistory: BidHistory
    tresh: float
    t1: float
    u2: float

    @property
    def name(self) -> str:
        return "ParsCat"

    def initiate(self, opponent_name: Optional[str]):
        self.t1 = 0
        self.u2 = 1
        self.tresh = 0
        self.otherAgentsBidHistory = BidHistory()
        self.maxBid = self.preference.max_util_bid

    def receive_offer(self, bid: Bid, t: float):
        self.t = t

        self.otherAgentsBidHistory.add(
            BidDetails(bid.copy_without_utility(), self.preference.get_utility(bid), t)
        )

    def act(self, t: float) -> Action:
        if len(self.otherAgentsBidHistory.history) == 0:
            return nenv.Offer(self.maxBid)

        action = nenv.Offer(self.getRandomBid())
        myBid = action.bid

        myOfferedUtil = myBid.utility
        self.t = t
        self.t1 = t

        if self.otherAgentsBidHistory.history[-1].bid == myBid:
            return self.accept_action

        otherAgentBid = self.otherAgentsBidHistory.history[-1].bid
        offeredUtilFromOpponent = self.preference.get_utility(otherAgentBid)

        if self.isAcceptable(offeredUtilFromOpponent, myOfferedUtil, t):
            return self.accept_action

        return action

    def isAcceptable(
        self, offeredUtilFromOtherAgent: float, myOfferedUtil: float, time: float
    ):
        if not self.can_accept():
            return False

        if offeredUtilFromOtherAgent == myOfferedUtil:
            return True

        t = time
        Util = 1.0

        if time <= 0.25:
            Util = 1 - t * 0.4
        elif 0.25 < time < 0.375:
            Util = 0.9 + (t - 0.25) * 0.4
        elif 0.375 < time <= 0.5:
            Util = 0.95 - (t - 0.375) * 0.4
        elif 0.5 < time <= 0.6:
            Util = 0.9 - (t - 0.5)
        elif 0.6 < time <= 0.7:
            Util = 0.8 + (t - 0.6) * 2
        elif 0.7 < time <= 0.8:
            Util = 1 - (t - 0.7) * 3
        elif 0.8 < time <= 0.9:
            Util = 0.7 + (t - 0.8) * 1
        elif 0.9 < time <= 0.95:
            Util = 0.8 - (t - 0.9) * 6
        elif 0.95 < time <= 1:
            Util = 0.5 + (t - 0.95) * 4
        else:
            Util = 0.8

        return offeredUtilFromOtherAgent >= Util

    def getRandomBid(self):
        xxx = 0.001
        check = 0.0

        counter = 0

        if self.t1 < 0.5:
            self.tresh = 1.0 - self.t1 / 4
            xxx = 0.01
        if 0.5 <= self.t1 < 0.8:
            self.tresh = 0.9 - self.t1 / 5
            xxx = 0.02
        if 0.8 <= self.t1 < 0.9:
            self.tresh = 0.7 + self.t1 / 5
            xxx = 0.02
        if 0.9 <= self.t1 < 0.95:
            self.tresh = 0.8 + self.t1 / 5
            xxx = 0.02
        if self.t1 >= 0.95:
            self.tresh = 1.0 - self.t / 4 - 0.01
            xxx = 0.02
        if self.t1 == 1:
            self.tresh = 0.5
            xxx = 0.05

        self.tresh -= check
        if self.tresh > 1:
            self.tresh = 1
            xxx = 0.01
        if self.tresh <= 0.5:
            self.tresh = 0.49
            xxx = 0.01

        bid = self.preference.get_random_bid(self.tresh - xxx, self.tresh + xxx)

        counter += 1

        while (
            self.preference.get_utility(bid) < self.tresh - xxx
            or self.preference.get_utility(bid) > self.tresh + xxx
        ) and counter < 1000:
            bid = self.preference.get_random_bid()

            self.tresh -= check

            if self.tresh > 1:
                self.tresh = 1
                xxx = 0.01
            if self.tresh <= 0.5:
                self.tresh = 0.49
                xxx = 0.01

            counter += 1

            check += 0.01

        if (
            self.preference.get_utility(bid)
            < self.preference.get_utility(
                self.otherAgentsBidHistory.getBestBidDetails().bid
            )
            and self.getNumberOfParties() == 2
        ):
            return self.otherAgentsBidHistory.getBestBidDetails().bid

        return bid

    def getNumberOfParties(self):
        return 2

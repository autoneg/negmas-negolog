from typing import Dict, List

import nenv


class BidSelector:
    """
        This class helps to select a bid based on a given utility
    """
    pref: nenv.Preference               # Preferences
    BidList: Dict[float, nenv.Bid]      # Utility-Bid mapping
    sorted_keys: List[float]            # BidList's keys, ascending (see below)

    def __init__(self, pref: nenv.Preference):
        """
            Constructor. It also generates the BidList dictionary.
        :param pref: Preferences of the agent
        """
        self.pref = pref
        self.BidList = {}

        InitialBid = {issue: issue.values[0] for issue in self.pref.issues}

        b = nenv.Bid(InitialBid)
        self.BidList[self.pref.get_utility(b)] = b

        for issue in self.pref.issues:
            TempBids = {}

            # We add a small negative value to use floorEntry and lowerEntry methods
            d = -0.00000001

            for TBid in self.BidList.values():
                for value in issue.values:
                    NewBidV = TBid.copy()
                    NewBidV[issue] = value

                    webid = NewBidV.copy()

                    TempBids[self.pref.get_utility(webid) + d] = NewBidV

                    d -= 0.00000001

            self.BidList = TempBids

        # BidList is complete and is never mutated afterwards, so its keys can be
        # ordered once here instead of on every lookup. This is what lets
        # HardHeaded.floorEntry/lowerEntry binary-search rather than re-sort the whole
        # utility space each time they are called; see KLH.floorEntry.
        self.sorted_keys = sorted(self.BidList.keys())

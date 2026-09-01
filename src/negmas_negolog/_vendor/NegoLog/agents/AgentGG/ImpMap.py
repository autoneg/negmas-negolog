from typing import List, Dict
from agents.AgentGG.ImpUnit import ImpUnit
import nenv


class ImpMap:
    """
        Importance Map is an Opponent Model which is a Frequency-Based approach. This opponent model can be used to
        estimate not only the opponents preferences but also self preferences (Uncertainty Challenge).

        It tries to predict importance of a value.
    """
    map: Dict[nenv.Issue, List[ImpUnit]]        # Importance dictionary
    pref: nenv.Preference                       # Self preferences
    _issues: List[nenv.Issue]                   # `pref.issues`, fetched once (see below)
    _index: Dict[nenv.Issue, Dict[str, ImpUnit]]  # value -> unit, so lookups are not scans

    def __init__(self, preference: nenv.Preference):
        """
            Constructor
        :param preference: Self preferences
        """
        self.pref = preference
        self.map = {}

        # Initiate importance units
        for issue in self.pref.issues:
            values = issue.values

            issueImpUnit = [ImpUnit(value) for value in values]

            self.map[issue] = issueImpUnit

        # `pref.issues` is a property that copies its list on every access, and the
        # lookups below run it once per issue per bid -- ten million times in a single
        # negotiation on a large domain. It cannot change for a fixed preference.
        self._issues = list(self.pref.issues)
        self._reindex()

    def _reindex(self) -> None:
        """Rebuild the value -> unit lookup used in place of scanning each value list.

        Finding a value's unit was a linear scan of the issue's value list, run once per
        issue per bid. That is fine for one bid and ruinous over a whole outcome space:
        with 188,160 outcomes, seven issues and a handful of values each, `getImportance`
        alone accounted for 18.5s of a 49s negotiation.

        `setdefault` rather than plain assignment so that a repeated value resolves to
        the same unit the scan would have returned -- the first one in the list's
        *current* order. That order changes whenever the units are re-sorted, which is
        why this is called again after every sort rather than built once.
        """
        self._index = {
            issue: {}
            for issue in self.map
        }
        for issue, units in self.map.items():
            index = self._index[issue]
            for unit in units:
                index.setdefault(unit.valueOfIssue, unit)

    def opponent_update(self, receivedOfferBid: nenv.Bid):
        """
            This method is called when a bid is received from the opponent to update estimated opponent preferences.
        :param receivedOfferBid: Received bid
        :return: Nothing
        """
        for issue in self._issues:
            # Update value weight when it is observed
            currentUnit = self._index[issue].get(receivedOfferBid[issue])

            if currentUnit is not None:
                currentUnit.meanWeightSum += 1

        for issue, impUnitList in self.map.items():     # Sort values
            self.map[issue] = sorted(impUnitList, reverse=True)

        self._reindex()     # the sort above may have changed which unit a value resolves to

    def self_update(self, bidOrdering: list):
        """
            This method is called to estimate self preferences
        :param bidOrdering: List of bids in Preferences
        :return: Nothing
        """

        # Current Weight starts from the zero and increases depending on the importance of a bid.
        # Higher importance higher Current Weight value
        current_weight = 0

        # In the Framework, bid ordering is sorted in descending order. However, Genius sorts in ascending order.
        for bid in reversed(bidOrdering):
            # Increase current weight
            current_weight += 1

            # Update the observed values
            for issue in self._issues:
                # Update corresponding values
                currentUnit = self._index[issue].get(bid[issue])

                if currentUnit is not None:
                    currentUnit.weightSum += current_weight
                    currentUnit.count += 1

        # Normalized values
        for impUnitList in self.map.values():
            for currentUnit in impUnitList:
                if currentUnit.count == 0:
                    currentUnit.meanWeightSum = 0.
                else:
                    currentUnit.meanWeightSum = currentUnit.weightSum / currentUnit.count

        # Sort the values in descending order
        for issue, impUnitList in self.map.items():
            self.map[issue] = sorted(impUnitList, reverse=True)

        self._reindex()     # the sort above may have changed which unit a value resolves to

        # Minimum value must be 0
        minMeanWeightSum = 1000000000
        for issue, impUnitList in self.map.items():
            tempMeanWeightSum = impUnitList[-1].meanWeightSum

            if tempMeanWeightSum < minMeanWeightSum:
                minMeanWeightSum = tempMeanWeightSum

        for impUnitList in self.map.values():
            for currentUnit in impUnitList:
                currentUnit.meanWeightSum -= minMeanWeightSum

    def getImportance(self, bid: nenv.Bid) -> float:
        """
            Calculate the estimated importance of a given bid.
        :param bid: Target bid
        :return: Estimated importance
        """
        bidImportance = 0.

        for issue in self._issues:
            unit = self._index[issue].get(bid[issue])

            # A value with no unit contributes nothing, exactly as the scan's
            # `valueImportance = 0.` default did when it found no match.
            if unit is not None:
                bidImportance += unit.meanWeightSum

        return bidImportance

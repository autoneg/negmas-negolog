import random
from typing import List, Dict, Set
import numba
import numpy
import nenv
from agents.AhBuNeAgent.impmap.IssueValueUnit import IssueValueUnit
from agents.AhBuNeAgent.linearorder.SimpleLinearOrdering import SimpleLinearOrdering


class SimilarityMap:
    """
        This class estimates the importance of values and issues for the uncertainty challenge.
    """
    pref: nenv.Preference                               # Preferences
    issueValueImpMap: Dict[str, List[IssueValueUnit]]   # Importance of values
    issueImpMap: Dict[str, float]                       # Importance of issue
    estimatedProfile: SimpleLinearOrdering              # Estimated self preferences
    maxImpBid: nenv.Bid                                 # The bid with the highest importance
    minImpBid: nenv.Bid                                 # The bid with the lowest importance
    availableValues: Dict[str, Set[str]]               # Available values
    forbiddenValues: Dict[str, Set[str]]               # Forbidden values
    rnd: random.Random                                  # Random object
    issueList: List[str]                                # List of issues
    sortedIssueImpMap: Dict[str, float]                 # Sorted issue importance
    valueIndex: Dict[str, Dict[str, IssueValueUnit]]    # value -> unit, so lookups are not scans
    totalKnownValues: int                               # Number of (issue, value) pairs the maps can hold

    def __init__(self, pref: nenv.Preference):
        """
            Constructor
        :param pref: Self preferences
        """
        self.pref = pref
        self.issueList = []
        self.rnd = random.Random()

        # Get all issues

        for issue in pref.issues:
            self.issueList.append(issue.name)

        # Initiate dictionaries

        self.renewMaps()

    def createConditionLists(self, numFirstBids: int, numLastBids: int):
        """
            This method determines the available and forbidden values from the given bid ranking
        :param numFirstBids: Number of first bids
        :param numLastBids: Number of last bids
        :return: Nothing
        """
        # Initiate lists
        self.renewLists()

        # Get estimated bids. `getBids` hands back a copy of the ranking, which on a
        # domain the size of Travel is a 188,160-element list copied once per round for
        # no reason: nothing below writes to it.
        sortedBids = self.estimatedProfile.bids
        firstStartIndex = (len(sortedBids) - 1) - numFirstBids

        # Start index must be >= 0
        if firstStartIndex < 0:
            firstStartIndex = 0

        # Pair each issue with its value index and its target set once, so that the bid
        # loop below costs one dictionary lookup per issue instead of a scan of that
        # issue's value list. Keyed by issue name, which is what an Issue hashes and
        # compares as, so a bid's Issue keys still find the right entry.
        available = {
            name: (self.valueIndex[name], self.availableValues[name])
            for name in self.issueValueImpMap
        }

        # A value is added at most once, so once every (issue, value) pair the map knows
        # about has been added, no later bid can change anything: the loop has reached
        # its fixed point and the remaining bids are pure no-ops.
        filled = 0

        # Find available values
        for bidIndex in range(firstStartIndex, len(sortedBids)):
            currentBid = sortedBids[bidIndex]

            for issue, value in currentBid.content.items():
                valueUnits, availableIssueValues = available[issue]

                # The scan only recorded a value that had a unit in that issue's list,
                # and only if it was not recorded already.
                if value in valueUnits and value not in availableIssueValues:
                    availableIssueValues.add(value)
                    filled += 1

            if filled == self.totalKnownValues:
                break

        # Number of last bids cannot exceed the number of total bids
        if numLastBids >= len(sortedBids):
            numLastBids = len(sortedBids) - 1

        forbidden = {
            name: (self.valueIndex[name], self.forbiddenValues[name])
            for name in self.issueValueImpMap
        }

        filled = 0

        # Find forbidden values
        for bidIndex in range(0, numLastBids):
            currentBid = sortedBids[bidIndex]

            for issue, value in currentBid.content.items():
                valueUnits, forbiddenIssueValues = forbidden[issue]

                if value in valueUnits and value not in forbiddenIssueValues:
                    forbiddenIssueValues.add(value)
                    filled += 1

            if filled == self.totalKnownValues:
                break

    def isCompatibleWithSimilarity(self, bid: nenv.Bid, minUtility: float) -> bool:
        """
            Check if the given bid is compatible with the Similarity Map
        :param bid: Target bid
        :param numFirstBids: First number of bids
        :param numLastBids: Last number of bids
        :param minUtility: Minimum utility value
        :return: Whether the given bid is compatible with the Similarity Map, or not
        """
        # self.createConditionLists(numFirstBids, numLastBids)
        issueChangeLoss = 1. / len(self.pref.issues)

        changeRest = int((1 - minUtility) / issueChangeLoss) + 1

        if changeRest > len(self.pref.issues):
            changeRest = len(self.pref.issues)

        changedIssueBest = 0
        changedIssueWorst = 0
        changedNotAvailable = 0

        # Sort issues based on importance
        sortedIssueMapSet = self.sortedIssueImpMap.items()
        sortedIssueArrList = [[key, value] for key, value in self.sortedIssueImpMap.items()]

        for i in range(len(sortedIssueArrList)):
            issue = sortedIssueArrList[i][0]

            # Check all available values are also forbidden
            allAvailablesForbidden = True
            availableIssueValueList = self.availableValues[issue]
            forbiddenIssueValueList = self.forbiddenValues[issue]

            for issueValue in availableIssueValueList:
                if issueValue not in forbiddenIssueValueList:
                    allAvailablesForbidden = False
                    break

            # If the value of that issue in the given bid is the value in the highest important bid
            if bid[issue] != self.maxImpBid[issue]:
                # The value of the issue is not forbidden, False
                if not allAvailablesForbidden and bid[issue] not in forbiddenIssueValueList:
                    return False

                # Count changed value
                if bid[issue] not in availableIssueValueList:
                    changedNotAvailable += 1
                elif i < (len(sortedIssueArrList) + 1) // 2:
                    changedIssueWorst += 1
                else:
                    changedIssueBest += 1

        # Change in Rest of Worst and Best number of values
        changeRestBest = changeRest // 2
        changeRestWorst = (changeRest // 2) + (changeRest % 2)

        # Update Worst and Best number of values
        changedIssueBest += changedNotAvailable
        changedIssueWorst += changedNotAvailable

        # Best
        exceedBestBidNum = changedIssueBest - changeRestBest

        if exceedBestBidNum > 0:
            equivalentWorstBidNum = exceedBestBidNum * 2
            changedIssueBest -= exceedBestBidNum
            changedIssueWorst += equivalentWorstBidNum

        # Worst
        exceedWorstBidNum = changedIssueWorst - changeRestWorst
        if exceedBestBidNum > 0:
            equivalentBestBidNum = (exceedWorstBidNum + 1) // 2
            changedIssueWorst -= exceedWorstBidNum
            changedIssueBest += equivalentBestBidNum

        # If decreases
        if changedIssueBest <= changeRestBest and changedIssueWorst <= changeRestWorst:
            return True

        return False

    def findBidCompatibleWithSimilarity(self, minUtility: float, oppMaxBid: nenv.Bid):
        """
            This method finds a bid compatible with the Similarity Map
        :param numFirstBids: First number of bids
        :param numLastBids: Last number of bids
        :param minUtility: Minimum utility value
        :param oppMaxBid:
        :return: Compatible bid
        """

        # Create lists
        # self.createConditionLists(numFirstBids, numLastBids)

        # Change rest
        issueChangeLoss = 1. / len(self.pref.issues)

        changeRest = int((1 - minUtility) / issueChangeLoss) + 1

        if changeRest > len(self.pref.issues):
            changeRest = len(self.pref.issues)

        # Rest of number of Best and Worst values
        changeRestBest = changeRest // 2
        changeRestWorst = (changeRest // 2) + (changeRest % 2)

        # Sorted issues
        # TODO Check it again!
        sortedIssueArrList = [[key, value] for key, value in self.sortedIssueImpMap.items()]

        # Create a bid content which has the highest important values
        createBid = {}
        for i in range(len(self.sortedIssueImpMap)):
            issue = sortedIssueArrList[i][0]
            createBid[issue] = self.maxImpBid[issue]

        selectOppValueCount = 0

        while not (changeRestWorst == 0 and changeRestBest == 0):
            # Minimum Rest
            notAvailableChance = min(changeRestWorst, changeRestBest)

            # Randomly select an issue in the first half of the sorted issues
            bestIssueStartIndex = (len(sortedIssueArrList) + 1) // 2
            randIssue = self.rnd.randint(0, len(sortedIssueArrList) - 1)

            # If will be changed.
            if (randIssue < bestIssueStartIndex and changeRestWorst != 0) or (randIssue >= bestIssueStartIndex and changeRestBest != 0):
                issue = sortedIssueArrList[randIssue][0]

                # Check if all available values are forbidden in that issue
                allAvailablesForbidden = True

                for issueValue in self.availableValues[issue]:
                    if issueValue not in self.forbiddenValues[issue]:
                        allAvailablesForbidden = False
                        break

                availableIssueValueList = self.availableValues[issue]
                forbiddenIssueValueList = self.forbiddenValues[issue]
                allIssueValues = self.issueValueImpMap[issue]
                randomIssueValue: str

                randIssueValueIndex = self.rnd.randint(0, len(allIssueValues) - 1)
                if selectOppValueCount < 500 and oppMaxBid is not None:  # Limit
                    randomIssueValue = oppMaxBid[issue]
                    selectOppValueCount += 1
                else:
                    randomIssueValue = allIssueValues[randIssueValueIndex].valueOfIssue

                # Value must not be forbidden
                if not allAvailablesForbidden:
                    while randomIssueValue in forbiddenIssueValueList:
                        randIssueValueIndex = self.rnd.randint(0, len(allIssueValues) - 1)
                        randomIssueValue = allIssueValues[randIssueValueIndex].valueOfIssue

                selectValue = False

                # Controls
                if randomIssueValue not in availableIssueValueList:
                    if notAvailableChance != 0:
                        changeRestWorst -= 1
                        changeRestBest -= 1
                        selectValue = True
                elif randIssue < bestIssueStartIndex:
                    if changeRestWorst != 0:
                        changeRestWorst -= 1
                        selectValue = True
                elif changeRestBest != 0:
                    changeRestBest -= 1
                    selectValue = True

                # Change the bid content
                if selectValue:
                    createBid[issue] = randomIssueValue

        # Create the bid content for Bid object
        createBid = {self.pref.issues[self.pref.issues.index(i)]: v for i, v in createBid.items()}

        return nenv.Bid(createBid)  # Convert into Bid object

    def extract_issue_value_imp(self, sortedBids: list, issueValueImpMap: dict):
        # Iterate over sorted bids to extract the Issue-Value importance dictionary
        # The unit a value belongs to is found by lookup rather than by scanning the
        # issue's value list; `valueIndex` resolves a repeated value to the same unit the
        # scan's first match would have picked.
        # Built from the argument rather than read off `self`, so it indexes whatever map
        # the caller handed in. `setdefault` keeps the first unit for a repeated value,
        # which is the one the scan would have stopped at.
        index = {}

        for name, units in issueValueImpMap.items():
            issueIndex = {}

            for unit in units:
                issueIndex.setdefault(unit.valueOfIssue, unit)

            index[name] = issueIndex

        for bidIndex in range(len(sortedBids)):
            currentBid = sortedBids[bidIndex]
            bidImportance = float(bidIndex) + 1.

            for issue, value in currentBid.content.items():
                currentUnit = index[issue].get(value)

                if currentUnit is not None:
                    currentUnit.importanceList.append(bidImportance)

    def update(self, estimatedProfile: SimpleLinearOrdering):
        """
            This method is called when bid ranking is provided.
        :param estimatedProfile: Self estimated preferences
        :return: Nothing
        """

        # Create maps
        self.renewMaps()

        # Initiate self estimated profile
        self.estimatedProfile = estimatedProfile
        sortedBids = estimatedProfile.getBids()

        # Initiate max. and min. important bids for the agent
        self.maxImpBid = estimatedProfile.getMaxBid()
        self.minImpBid = estimatedProfile.getMinBid()

        self.extract_issue_value_imp(sortedBids, self.issueValueImpMap)

        # Extract the importance dictionary of each issue
        for issue in self.issueImpMap.keys():
            issueValAvgList = []
            currentIssueList = self.issueValueImpMap[issue]

            for currentUnit in currentIssueList:
                if len(currentUnit.importanceList) == 0:
                    continue

                # Get average importance values
                issueValueAvg = 0.

                for IssueUnitTmp in currentUnit.importanceList:
                    issueValueAvg += IssueUnitTmp

                issueValueAvg /= len(currentUnit.importanceList)
                issueValAvgList.append(issueValueAvg)

            self.issueImpMap[issue] = self.stdev(issueValAvgList)

        # Sort by the importance
        self.sortedIssueImpMap = self.sortByValueBid(self.issueImpMap)

    def stdev(self, arr: list) -> float:
        """
            This method calculated standard deviation of a given list.
        :param arr: Target list
        :return: Standard deviation of the list
        """
        return float(numpy.std(arr))

    def renewMaps(self):
        """
            This method initiates the corresponding dictionaries
        :return: Nothing
        """
        self.issueValueImpMap = {}
        self.issueImpMap = {}

        for issue in self.pref.issues:
            self.issueImpMap[issue.name] = 0.
            values = issue.values
            issueIssueValueUnit = [IssueValueUnit(value) for value in values]
            self.issueValueImpMap[issue.name] = issueIssueValueUnit

        # Index the units by value. `setdefault` keeps the first unit for a repeated
        # value, which is the one the scans this replaces would have stopped at. The
        # unit lists are never re-ordered after they are built here, so this index stays
        # correct until the next `renewMaps`.
        self.valueIndex = {}

        for name, units in self.issueValueImpMap.items():
            index = {}

            for unit in units:
                index.setdefault(unit.valueOfIssue, unit)

            self.valueIndex[name] = index

        self.totalKnownValues = sum(len(index) for index in self.valueIndex.values())

    def renewLists(self):
        """
            This method initiates the corresponding lists
        :return: Nothing
        """
        self.availableValues = {issue.name: set() for issue in self.pref.issues}
        self.forbiddenValues = {issue.name: set() for issue in self.pref.issues}

    def sortByValueBid(self, hm: dict) -> dict:
        """
            This method sorts a given dictionary based on the values
        :param hm: Given dictionary
        :return: Sorted dictionary
        """
        list = [[key, value] for key, value in hm.items()]
        list.sort(key=lambda x: x[1])

        temp = {}

        for [key, value] in list:
            temp[key] = value

        return temp

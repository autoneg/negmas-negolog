import nenv.OpponentModel


class SaneUtilitySpace(nenv.OpponentModel.EstimatedPreference):
    def __init__(self, reference: nenv.Preference):
        super().__init__(reference)

    def init_zero(self):
        for issue in self.issue_weights.keys():
            self._issue_weights[issue] = 0.

            for value_name in self.value_weights[issue].keys():
                self._value_weights[issue][value_name] = 0.

    def init_copy(self, pref: nenv.Preference):
        for issue in self.issue_weights.keys():
            self._issue_weights[issue] = pref.issue_weights[issue]

            for value_name in self.value_weights[issue].keys():
                self._value_weights[issue][value_name] = pref.value_weights[issue][value_name]

    def normalize(self):
        # LOCAL PATCH (negmas-negolog): guard both divisions against a zero sum.
        # EstimatedPreference seeds this space with the *inverse* of the reference
        # weights (1 - w), so a whole vector becomes zero whenever every weight is
        # 1.0 -- a single-issue domain (issue weight 1.0), or any issue the agent is
        # indifferent about (every value fully acceptable). Both raised
        # ZeroDivisionError here. The degenerate case falls back to a uniform
        # distribution, which keeps this method's sum-to-1 semantics; the base
        # nenv.OpponentModel.EstimatedPreference.normalize guards the same two
        # divisions. No effect when the sums are non-zero.
        issueSum = sum(self.issue_weights.values())

        for issue in self.issue_weights.keys():
            if issueSum == 0:
                self._issue_weights[issue] = 1. / len(self.issue_weights)
            else:
                self._issue_weights[issue] /= issueSum

            valueSum = sum(self.value_weights[issue].values())

            for value in self.value_weights[issue].keys():
                if valueSum == 0:
                    self._value_weights[issue][value] = 1. / len(self.value_weights[issue])
                else:
                    self._value_weights[issue][value] /= valueSum

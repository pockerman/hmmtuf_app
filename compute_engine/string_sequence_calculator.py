import textdistance


class TextDistanceCalculator(object):

    NAMES = ["Prefix similarity", "Postfix similarity",
             "Length distance", "Identity similarity",
             "Matrix similarity", "Longest common subsequence similarity",
             "Longest common substring similarity",
             "Ratcliff-Obershelp similarity"]

    def __init__(self, dist_type):
        self._dist_type = type

    def calculate(self, txt1, txt2):
        pass
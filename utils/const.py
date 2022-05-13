from enum import Enum

class ComparisonValues(str, Enum):
    equal = "0"
    greater = "1"
    less = "2"

    def __str__(self):
        return self.value

class HyperplaneComparisonValues(str, Enum):
    accepted = "Accepted"
    rejected = "Rejected"

    def __str__(self):
        return self.value

SUBSCRIPT_NUMBERS = "₀₁₂₃₄₅₆₇₈₉"
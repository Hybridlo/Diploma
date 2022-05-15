from enum import Enum

class ComparisonValues(str, Enum):
    equal = "="
    greater = ">"
    less = "<"

    def __str__(self):
        return self.value

SUBSCRIPT_NUMBERS = "₀₁₂₃₄₅₆₇₈₉"
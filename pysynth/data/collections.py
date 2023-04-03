class Collection(list):
    """A list extended with a subtraction with repetition operation."""

    def __sub__(self, other):
        i = 0
        diff = list(self)
        other = list(other)
        while i < len(diff):
            item = diff[i]
            if item in other:
                diff.pop(i)
                other.remove(item)
            else:
                i += 1
        return diff

    def __str__(self):
        return "["+",".join([str(item) for item in self])+"]"


class UniqueCollection(set):
    """A set extended with an addition that performs union"""
    def __add__(self, other):
        return UniqueCollection(list(self)+list(other))

    def __sub__(self, other):
        return UniqueCollection(set(self)-set(other))

    def __str__(self):
        return "["+",".join([str(item) for item in self])+"]"

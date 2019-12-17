"""
Test lower-level caching basic functions.
These don't do multiplication searching.
"""
from mult_by_const import MultCache, Instruction
import os


def test_lower_level_caching():
    mcache = MultCache()
    mcache.check()
    # Note: dictionaries keys in Python 3.8+ are in given in insertion order.
    assert list(mcache.keys()) == [0, 1], "We should have at least 0 and 1"
    assert len(mcache) == 2, "Should have at least 0 and 1"

    mcache.insert(2, 1, 1, True, [Instruction("add", 1)])
    assert len(mcache) == 3, "Should have increased cache"
    mcache.check()

    # This should do nothing
    mcache.insert_or_update(1, 0, 0, True, [Instruction("nop", 0, 0)])
    assert len(mcache) == 3, "Should not have increased cache; entry already exists."
    mcache.check()

    mcache.insert_or_update(4, 1, 1, True, [Instruction("shift", 2)])
    assert len(mcache) == 4, "Should have increased cache."
    mcache.check()

    mcache.clear()
    assert len(mcache) == 2, "Should have cleared cache."
    mcache.check()


# If run as standalone
if __name__ == "__main__":
    test_lower_level_caching()

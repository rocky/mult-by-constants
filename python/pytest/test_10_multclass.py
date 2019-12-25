"""
Test multiplication-by-constant base class
These don't do multiplication searching.
"""
from mult_by_const import MultConstClass


def test_basic():
    mconst = MultConstClass()
    result: List[Instruction] = []
    for number, expect in (
            (5, (5, 1, 0)),
            (10, (5, 2, 1)),
            (20, (5, 2, 2))
            ):
        got = mconst.make_odd(number, 1, result)
        assert got == expect, f"make_odd({number})={got}; expect {expect}"


# If run as standalone
if __name__ == "__main__":
    test_basic()

"""
Test higher-level caching of multiplication searching.
"""
from mult_by_const import MultConst
import os


def test_mult_cache():
    debug = "DEBUG" in os.environ
    mconst = MultConst(debug=debug)

    for clear_cache in (False, True):
        for n in range(340, 344):
            cost, instrs = mconst.find_mult_sequence(n)
            mconst.mult_cache.check()
            if clear_cache:
                mconst.mult_cache.clear()


# If run as standalone
if __name__ == "__main__":
    test_mult_cache()

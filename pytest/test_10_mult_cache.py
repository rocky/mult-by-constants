"""
Test higher-level caching of multiplication searching.
"""
from mult_by_const import MultConst
import os


def test_mult_cache():
    debug = "DEBUG" in os.environ
    mconst = MultConst(debug=debug)

    for clear_cache in (False, True):
        for n in range(2, 52):
            cost, instrs = mconst.find_mult_sequence(n)
            mconst.mult_cache.check()
            if clear_cache:
                mconst.mult_cache.clear()
                pass
            pass
        if not clear_cache:
            assert mconst.mult_cache[51][1] == 4, f"for {51} expected cost 4; got {cost}"
        pass
    return


# If run as standalone
if __name__ == "__main__":
    test_mult_cache()
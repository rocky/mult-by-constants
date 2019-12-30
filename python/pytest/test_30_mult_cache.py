"""
Test higher-level caching of multiplication searching.
"""
from mult_by_const import MultConst
# from mult_by_const.io import dump


def test_mult_cache():
    mconst = MultConst(debug=True)

    for clear_cache in (False, True):
        for n in range(2, 52):
            cost, instrs = mconst.find_mult_sequence(n)
            # dump(mconst.mult_cache)
            mconst.mult_cache.check()
            if clear_cache:
                mconst.mult_cache.clear()
                pass
            pass
        if not clear_cache:
            assert mconst.mult_cache[51][1] == 4, f"for {51} expected cost 4; got {cost}"
            for n in range(-2, -52, -1):
                ncost, instrs = mconst.find_mult_sequence(n)
                cost = mconst.mult_cache[-n][1]
                assert 0 <= ncost - cost <= 1, f"{ncost} - {cost} not in [0, 1]"
                mconst.mult_cache.check()
                pass
        pass
    return


# If run as standalone
if __name__ == "__main__":
    test_mult_cache()

"""
Test the add-chain cpu model of described in Knuth.
"""
import os

from typing import Tuple
from mult_by_const import MultConst
from mult_by_const.cpu import (chained_adds, inf_cost)


def test_add_chains():
    debug = "DEBUG" in os.environ
    mconst = MultConst(cpu_model=chained_adds, debug=debug)

    cost_layers: Tuple(List[int]) = (
        [1],   # cost 0
        [2],   # cost 1
        [3, 4],  # cost 2
        [5, 6, 8], # cost 3
        [7, 10, 12, 9, 16], # cost 4
        [14, 11, 20, 15, 24, 13, 17, 18, 32], # cost 5
        [19, 28, 21, 22,
         # 23, # 23 reuses 3 on the path to 1 which we don't pick up.
         40, 27,
         # 30, # 30 reuses 12 + 3 on the path to 1 which we don't pick up.
         25, 48, 26, 34, 36, 33, 64], # cost 6
    )

    for clear_cache in (True, False):
        for expected_cost in range(len(cost_layers)):
            for num in cost_layers[expected_cost]:
                cost, instrs = mconst.find_mult_sequence(num)
                assert (
                    cost == expected_cost
                ), f"for {num} expecting {expected_cost}, got {cost}."
                mconst.mult_cache.check()
                if clear_cache:
                    mconst.mult_cache.clear()
                    pass
                pass
            pass
        pass
    from mult_by_const.io import dump
    dump(mconst.mult_cache)
    return


# If run as standalone
if __name__ == "__main__":
    test_add_chains()

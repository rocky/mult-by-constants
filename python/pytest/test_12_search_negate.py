from typing import List
from mult_by_const import (
    MultConst,
    print_instructions,
    inf_cost,
    Instruction,
    check_instruction_sequence_cost,
    check_instruction_sequence_value,
    binary_method,
)

from mult_by_const.search_methods import search_negate

import os


def check(n: int, cost: float, instrs: List[Instruction], debug) -> None:
    if debug:
        print_instructions(instrs, n, cost)
    check_instruction_sequence_cost(cost, instrs)
    check_instruction_sequence_value(n, instrs)


def test_negate():
    debug = "DEBUG" in os.environ

    instrs: List[Instruction] = []
    candidate_instrs: List[Instruction] = []

    mconst = MultConst(debug=debug)
    mconst.search_methods = search_negate

    n = 10
    bin_cost, bin_instrs = binary_method.binary_sequence(mconst, n)
    negate_cost = mconst.op_costs["negate"]

    # upper is too low to allow us to get a solution
    scost, s_instrs = search_negate(
        mconst,
        -n,
        upper=bin_cost + negate_cost,
        lower=bin_cost,
        instrs=bin_instrs,
        candidate_instrs=candidate_instrs,
    )

    assert s_instrs == candidate_instrs

    # upper is okay (and exact) to allow us to get a solution
    s_cost, s_instrs = search_negate(
        mconst,
        -n,
        upper=bin_cost + negate_cost + 1,
        lower=bin_cost,
        instrs=bin_instrs,
        candidate_instrs=candidate_instrs,
    )
    assert s_cost == bin_cost + negate_cost
    check(-n, s_cost, s_instrs, debug)

    # Try something not in the cache.
    # Negate will use the binary method
    n = -23
    s_cost, s_instrs = search_negate(
        mconst,
        n,
        upper=inf_cost,
        lower=0,
        instrs=instrs,
        candidate_instrs=candidate_instrs,
    )

    check(n, s_cost, instrs=s_instrs, debug=debug)


# If run as standalone
if __name__ == "__main__":
    test_negate()

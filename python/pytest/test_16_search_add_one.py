from typing import List
from mult_by_const import (
    Instruction,
    MultConst,
    binary_method,
    check_instruction_sequence_cost,
    check_instruction_sequence_value,
    inf_cost,
    print_instructions,
)

from mult_by_const.search_methods import search_add_one

# FIXME: DRY
def check(n: int, cost: float, instrs: List[Instruction]) -> None:
    print_instructions(instrs, n, cost)
    check_instruction_sequence_cost(cost, instrs)
    check_instruction_sequence_value(n, instrs)


def test_search_add_one():

    instrs: List[Instruction] = []
    candidate_instrs: List[Instruction] = []

    mconst = MultConst(debug=True)
    # mconst = MultConst(debug=debug)
    mconst.search_methods = (search_add_one,)

    n = 12
    bin_cost, bin_instrs = binary_method.binary_sequence(mconst, n)
    add_cost = mconst.op_costs["add"]

    # upper is too low to allow us to get a solution
    s_cost, s_instrs = search_add_one(
        mconst,
        n,
        upper=bin_cost + add_cost,
        lower=bin_cost,
        instrs=bin_instrs,
        candidate_instrs=candidate_instrs,
    )

    assert s_instrs == candidate_instrs
    # No check since we did a cutoff.

    # We should start out with n+1, instead when
    # we subtract one, so we should get a cutoff here
    # quickly too
    s_cost, s_instrs = search_add_one(
        mconst,
        n,
        upper=bin_cost + add_cost + 1,
        lower=bin_cost,
        instrs=bin_instrs,
        candidate_instrs=candidate_instrs,
    )
    assert s_instrs == candidate_instrs
    # No check since we did a cutoff.

    # upper is okay to allow us to get a solution using
    # cached entry 3 added via binary_method.
    instrs = []
    s_cost, s_instrs = search_add_one(
        mconst,
        n + 1,
        upper=20,
        lower=0,
        instrs=instrs,
        candidate_instrs=candidate_instrs,
    )
    check(n + 1, s_cost, s_instrs)
    from mult_by_const.io import dump

    dump(mconst.mult_cache)

    # Try something that makes add count down for a bit.
    instrs = []
    candidate_instrs = []
    n = 11
    s_cost, s_instrs = search_add_one(
        mconst,
        n,
        upper=inf_cost,
        lower=0,
        instrs=instrs,
        candidate_instrs=candidate_instrs,
    )

    check(n, s_cost, instrs=s_instrs)
    from mult_by_const.io import dump
    dump(mconst.mult_cache)

    # Try something that makes add count down for a bit and fail.
    mconst.mult_cache.clear()
    instrs = []
    candidate_instrs = []
    n = 20
    s_cost, s_instrs = search_add_one(
        mconst, n, upper=6, lower=0, instrs=instrs, candidate_instrs=candidate_instrs,
    )

    # dump(mconst.mult_cache)
    # assert not s_instrs, f"should not find a value for {n} after clearing cache"
    # assert (
    #     mconst.mult_cache[n + 1][0] > 0
    # ), f"{n} failed but lower should have been updated"

    # # Negative numbers!
    # instrs = []
    # candidate_instrs = []
    # n = -4
    # s_cost, s_instrs = search_add_one(
    #     mconst, n, upper=8, lower=0, instrs=instrs, candidate_instrs=candidate_instrs,
    # )

    # check(n, s_cost, instrs=s_instrs)
    # from mult_by_const.io import dump
    # dump(mconst.mult_cache)


# If run as standalone
if __name__ == "__main__":
    test_search_add_one()

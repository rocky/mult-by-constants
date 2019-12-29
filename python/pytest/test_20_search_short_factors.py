from typing import List
from mult_by_const import (
    Instruction,
    MultConst,
    check_instruction_sequence_cost,
    check_instruction_sequence_value,
    print_instructions,
    binary_method
    )
from mult_by_const.search_methods import search_short_factors

# FIXME: DRY
def check(n: int, cost: float, instrs: List[Instruction]) -> None:
    print_instructions(instrs, n, cost)
    check_instruction_sequence_cost(cost, instrs)
    check_instruction_sequence_value(n, instrs)


def test_factor():

    instrs: List[Instruction] = []
    candidate_instrs: List[Instruction] = []

    mconst = MultConst(debug=True)
    # mconst = MultConst(debug=debug)
    mconst.search_methods = (search_short_factors,)

    n = 27

    s_cost, s_instrs = search_short_factors(
        mconst,
        n,
        upper=20,
        lower=0,
        instrs=instrs,
        candidate_instrs=candidate_instrs,
    )

    check(n, s_cost, s_instrs)
    # cost, instrs = mconst.try_shift_op_factor(n, 5, "add", 2, bin_cost, 0, [], bin_instrs)
    # assert bin_cost == cost, "5 is not a factor of 27, so we keep old bin_cost"

    # for n, factor, shift_amount in ((27, 3, 1), (85, 5, 2)):
    #     bin_cost, bin_instrs = binary_method.binary_sequence(mconst, n)
    #     if debug:
    #         print_instructions(bin_instrs, n, bin_cost)
    #     result = []
    #     cost, result = mconst.try_shift_op_factor(
    #         n, factor, "add", shift_amount, bin_cost, 0, [], bin_instrs
    #     )
    #     assert cost < bin_cost, f"should use the fact that {factor} is a factor of {n}"
    #     if debug:
    #         print_instructions(result, n, cost)


# If run as standalone
if __name__ == "__main__":
    test_factor()

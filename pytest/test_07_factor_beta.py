from mult_by_const import MultConst, print_instructions, binary_method
import os


def test_factor():
    debug = "DEBUG" in os.environ
    mconst = MultConst(debug=debug)
    n = 27
    bin_cost, bin_instrs = binary_method.binary_sequence(mconst, n)
    if debug:
        print_instructions(bin_instrs, n, bin_cost)
    result = []

    cost, instrs = mconst.try_shift_op_factor(n, 5, "add", 2, bin_cost, 0, [], bin_instrs)
    assert bin_cost == cost, "5 is not a factor of 27, so we keep old bin_cost"

    for n, factor, shift_amount in ((27, 3, 1), (85, 5, 2)):
        bin_cost, bin_instrs = binary_method.binary_sequence(mconst, n)
        if debug:
            print_instructions(bin_instrs, n, bin_cost)
        result = []
        cost, result = mconst.try_shift_op_factor(
            n, factor, "add", shift_amount, bin_cost, 0, [], bin_instrs
        )
        assert cost < bin_cost, f"should use the fact that {factor} is a factor of {n}"
        if debug:
            print_instructions(result, n, cost)


# If run as standalone
if __name__ == "__main__":
    test_factor()

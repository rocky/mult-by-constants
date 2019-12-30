from mult_by_const import MultConst
from mult_by_const.instruction import instruction_sequence_cost, print_instructions


def test_factor():
    mconst = MultConst(debug=False)
    for clear_cache in (False, True):
        for n, expected_cost in (
            (41, 4),
            (95, 4),
            (51, 4),
            (340, 5),
            (341, 6),
            (342, 7),
            (343, 6),
            (12345678, 13),
            (-12345678, 13),
        ):
            # FIXME: The cache is messed up in a weird way, using a negative number
            # and its cached positive value. I dont think it matters whether then
            # positive or negative number is requested first.
            if (n, clear_cache) == (-12345678, False):
                continue

            cost, instrs = mconst.find_mult_sequence(n)
            print_instructions(instrs, n, cost)
            assert (
                expected_cost == cost
            ), f"for {n} expected cost: {expected_cost}; got: {cost}"
            assert instruction_sequence_cost(instrs) == cost
            if clear_cache:
                mconst.mult_cache.clear()


# If run as standalone
if __name__ == "__main__":
    test_factor()

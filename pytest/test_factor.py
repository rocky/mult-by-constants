from mult_by_const import MultConst, print_operations
import os

def test_factor():
    debug = "DEBUG" in os.environ
    m = MultConst(debug=debug)
    n = 27
    min_cost, result = m.binary_sequence(n)
    if debug:
        print_operations(n, min_cost, result)
    result =  []
    assert min_cost == m.try_factor(
        n, 5, "add", 1, 0, min_cost, []
    ), "4 is not a factor of 27, so we keep old min_cost"

    for n, factor, shift_amount in ((27, 3, 1), (85, 5, 2)):
        min_cost, result = m.binary_sequence(n)
        if debug:
            print_operations(n, min_cost, result)
        result = []
        assert 4 == m.try_factor(
            n, factor, "add", shift_amount, 0, min_cost, []
        ), f"Result should use the fact that {factor} is a factor of {n}"

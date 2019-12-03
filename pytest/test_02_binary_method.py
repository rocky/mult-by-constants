from mult_by_const import MultConst, print_instructions
import os


def test_binary_method():
    debug = "DEBUG" in os.environ
    m = MultConst(debug=debug)
    for (n, expect) in (
        (0, 1),
        (1, 0),
        (2, 1),
        (3, 2),
        (4, 1),
        (5, 2),
        (6, 3),
        (7, 2),
        (8, 1),
        (53, 6),
    ):
        cost, result = m.binary_sequence(n)
        if debug:
            print_instructions(result, n, cost)
        assert expect == cost, f"cost({n}) = {cost}; expected it to be {expect}."


# If run as standalone
if __name__ == "__main__":
    test_binary_method()

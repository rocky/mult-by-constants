from mult_by_const import MultConstClass, print_instructions, binary_method
import os


def test_binary_method():
    debug = "DEBUG" in os.environ
    mconst = MultConstClass(debug=debug)
    for (n, expect_cost) in (
        (0, 1),
        (1, 0),
        (-1, 1),
        (2, 1),
        (3, 2),
        (4, 1),
        (5, 2),
        (6, 3),
        (7, 2),
        (-7, 2),
        (-3, 2),
        (8, 1),
        (53, 6),
        (340, 7),
    ):
        cost, result = binary_method.binary_sequence(mconst, n)
        if debug:
            print_instructions(result, n, cost)
        assert expect_cost == cost, f"cost({n}) = {cost}; expected it to be {expect_cost}."


# If run as standalone
if __name__ == "__main__":
    test_binary_method()

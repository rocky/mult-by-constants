from mult_by_const import MultConst
from mult_by_const.instruction import instruction_sequence_cost, print_instructions
import os


def test_factor():
    debug = "DEBUG" in os.environ
    m = MultConst(debug=debug)
    for n, expected_cost in ((340, 5), (341, 6), (342, 7), (343, 6)):
        min_cost, instrs = m.binary_sequence(n)
        cost, instrs = m.find_mult_sequence(n)
        print_instructions(instrs, n, cost)
        assert expected_cost == cost
        assert instruction_sequence_cost(instrs) == cost


# If run as standalone
if __name__ == "__main__":
    test_factor()

# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Multiplication sequence searching."""

from typing import List, Tuple

from mult_by_const.cpu import DEFAULT_CPU_PROFILE

from mult_by_const.instruction import Instruction

from mult_by_const.util import (
    consecutive_zeros,
    default_shift_cost,
)

from mult_by_const.cache import MultCache


class MultConstClass:
    def __init__(
        self,
        cpu_model=DEFAULT_CPU_PROFILE,
        debug=False,
        shift_cost_fn=default_shift_cost,
        search_methods=None,
    ):

        # Op_costs gives costs of using each kind of instruction.
        # The below just saves us from having to index into cpu_model
        # everywhere
        self.cpu_model = cpu_model
        self.op_costs = cpu_model.costs

        # FIXME: get rid of as a parameter and put in cpu_model
        self.shift_cost = shift_cost_fn

        # Cache prior searches
        # The key is the positive number looked up.
        # The value is a tuple of: lower bound, upper bound,
        # "finished" boolean, and an upper-bound instruction sequence.
        #
        # If the "finished" boolean is True, then the searching
        # previously completed, and "upper" has the final
        # cost. Otherwise, upper is undefined; a cutoff occurred previously
        # and searching wasn't complete. However, on subsquent
        # searches, we can query the lower bound and do another cutoff
        # if the current-search lower bound is not less than the
        # previously-recorded lower bound.

        # FIXME: give an examples here. Also attach names "alpha" and
        # and "beta" with the different types of cutoffs.
        self.mult_cache = MultCache(cpu_model)

        if debug:
            # We use indent show nesting in debug output
            self.indent = 0
        self.debug = debug
        self.search_methods = search_methods

        return

    def dedent(self) -> None:
        if self.debug:
            self.indent -= 2

    def debug_msg(self, s: str, relative_indent=0) -> None:
        print(f"{' '*self.indent}{s}")
        if relative_indent:
            self.indent += relative_indent

    def make_odd(
        self, n: int, cost: float, result: List[Instruction]
    ) -> Tuple[int, float]:
        """Handle low-order 0's with a single shift.
           Note: those machines that can only do a single shift of one place
           or those machines whose time varies with the shift amount, that is covered
           by the self.shift_cost function
        """
        shift_amount, n = consecutive_zeros(n)
        if shift_amount:
            shift_cost = self.shift_cost(shift_amount)
            cost += shift_cost
            result.append(Instruction("shift", shift_amount, shift_cost))
            pass
        return (n, cost)


if __name__ == "__main__":
    mconst = MultConstClass()
    result: List[Instruction] = []
    print(mconst.make_odd(5, 1, result))
    result = []
    print(mconst.make_odd(10, 1, result))
    print(mconst.make_odd(20, 1, result))

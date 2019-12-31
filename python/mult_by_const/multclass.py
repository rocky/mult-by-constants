# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Multiplication sequence searching."""

from typing import List, Tuple

from mult_by_const.cpu import DEFAULT_CPU_PROFILE

from mult_by_const.instruction import Instruction

from mult_by_const.util import consecutive_zeros, default_shift_cost

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
        self.debug = debug
        self.eps = self.op_costs["eps"]
        self.search_methods = search_methods

        # We use indent show nesting in debug output
        self.indent = 0
        return

    def dedent(self) -> None:
        if self.debug:
            self.indent -= 2

    def debug_msg(self, s: str, relative_indent=0) -> None:
        if self.debug:
            print(f"{' '*self.indent}{s}")
            if relative_indent:
                self.indent += relative_indent

    def make_odd(
        self, n: int, cost: float, result: List[Instruction]
    ) -> Tuple[int, float, int]:
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
        return (n, cost, shift_amount)

    def add_instruction(
        self, bin_instrs: List[Instruction], op_name: str, op_flag: int
    ) -> float:
        cost = self.op_costs[op_name]
        bin_instrs.append(Instruction(op_name, op_flag, cost))
        return cost

    def need_negation(self, n: int) -> Tuple[int, bool]:
        """
        See if we need to negate n and check that the CPU model can handle negation.
        If the CPU can't handle a negation, raise an error.
        Return whether the absolute value of n and whether negation is needed.
        """
        if n < 0:
            if not self.cpu_model.can_negate():
                raise TypeError(
                    f"cpu model {self.cpu_model.name} doesn't support multiplication by negative numbers"
                )
            need_negation = True
            n = -n
        else:
            need_negation = False
        return n, need_negation


if __name__ == "__main__":
    mconst = MultConstClass()
    result: List[Instruction] = []
    print(mconst.make_odd(5, 1, result))
    result = []
    print(mconst.make_odd(10, 1, result))
    print(mconst.make_odd(20, 1, result))

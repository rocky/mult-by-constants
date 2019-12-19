"""
Multiplication using the binary method representation of a number.
"""
from typing import List, Tuple

from mult_by_const.cpu import inf_cost
from mult_by_const.instruction import OP_R1, REVERSE_SUBTRACT_1, Instruction
from mult_by_const.util import bin2str, consecutive_ones
from mult_by_const.multclass import MultConstClass


def binary_sequence(self: MultConstClass, n: int) -> Tuple[float, List[Instruction]]:
    """Returns the cost and operation sequence using the binary
    representation of the number, assuming a (mostly empty)
    multiplication cache. (0 and 1 are always in the cache)

    If the cache has been populated, it is possible this will pick
    up a more optimal value from the cache and further reduce the
    sequence cost.

    In this (noncached) approach, each one bit other than the
    highest-order one bit is a "shift" by the number of
    consecutive zeros followed by an addition.

    If the number is even and not zero, then there is a final "shift".

    If subtraction is available, then each run of 1's in the
    binary representation is replaced by a shift of that amount
    followed by a subtraction.

    Since we generally prefer addition over subtraction:

         x = (x << 1) + x

    is preferable to:

         x = (x << 2) - x

    Examples:
    ---------

    We'll assume cost one for "add", "subtract", and "shift" by
    any amount.

    number  cost  remarks
    ------  ----  ------
    0:      0     do nothing; load constant zero
    1:      0     do nothing, load operand
    10:     1     shift one
    11:     2     shift one; add
    101:    2     shift two; add
    110     3     shift one; add; shift one
    111:    2     shift three; subtract one      - if subtract is available
    111:    4     shift one; add; shift one; add - if subtract is not available

    """

    cache_lower, cache_upper, finished, cache_instr = self.mult_cache[n]
    if finished:
        return (cache_upper, cache_instr)

    return binary_sequence_inner(self, n)


def binary_sequence_inner(self: MultConstClass, n: int) -> Tuple[float, List[Instruction]]:  # noqa: C901

    def add_instruction(bin_instrs: List[Instruction], op_name: str, op_flag: int) -> float:
        cost = self.op_costs[op_name]
        bin_instrs.append(Instruction(op_name, op_flag, cost))
        return cost

    def append_instrs(cache_instrs: List[Instruction], bin_instrs, cache_upper: float) -> float:
        cache_instrs.reverse()  # Because we compute in reverse order here
        bin_instrs += cache_instrs
        return cache_upper

    if n == 0:
        return (self.op_costs["zero"], [Instruction("zero", 0, self.op_costs["zero"])])
    orig_n = n

    n, need_negation = self.need_negation(n)

    assert n > 0

    bin_instrs: List[Instruction] = []
    cost: float = 0  # total cost of sequence

    while n > 1:

        if need_negation:
            cache_lower, cache_upper, finished, cache_instrs = self.mult_cache[-n]
            if cache_upper < inf_cost:
                cost += append_instrs(cache_instrs, bin_instrs, cache_upper)
                need_negation = False
                break

        cache_lower, cache_upper, finished, cache_instrs = self.mult_cache[n]
        if cache_upper < inf_cost:

            # If we were given a positive number, then we are done.
            # However if we were given a negative number, then from the
            # test above we now the negative version is not in the cache.
            # So we still have to continue in order to potentially find
            # a shorter sequence using a subtract.
            if not (need_negation and self.cpu_model.subtract_can_negate()):
                cost += append_instrs(cache_instrs, bin_instrs, cache_upper)
                break

        n, cost = self.make_odd(n, cost, bin_instrs)

        if n == 1:
            break

        # Handle low-order 1's via "adds", and also "subtracts" if subtracts are available.
        #
        one_run_count, m = consecutive_ones(n)
        try_reverse_subtract = need_negation and self.cpu_model.subtract_can_negate()
        if self.cpu_model.can_subtract() and (one_run_count > 2 or try_reverse_subtract):
            if try_reverse_subtract:
                cost += add_instruction(bin_instrs, "subtract", REVERSE_SUBTRACT_1)
                need_negation = False
            else:
                cost += add_instruction(bin_instrs, "subtract", OP_R1)

            n += 1
            pass
        else:
            cost += add_instruction(bin_instrs, "add", OP_R1)
            n -= 1
            pass
        pass

    bin_instrs.reverse()

    if need_negation:
        cost += add_instruction(bin_instrs, "negate", OP_R1)

    if self.debug:
        self.debug_msg(
            f"binary method for {orig_n} = {bin2str(orig_n)} has cost {cost}"
        )

    self.mult_cache.insert_or_update(orig_n, 0, cost, False, bin_instrs)

    return (cost, bin_instrs)


if __name__ == "__main__":
    from mult_by_const.instruction import print_instructions
    from mult_by_const.multclass import MultConstClass

    mconst = MultConstClass(debug=True)

    for n in [1, 0, -1, -7, -3]:
        cost, instrs = binary_sequence(mconst, n)
        print_instructions(instrs, n, cost)

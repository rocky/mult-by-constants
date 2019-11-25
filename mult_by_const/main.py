#!/usr/bin/env python
from typing import List, Set, Dict, Tuple, Optional

multSequence: List[int] = [1]

def consecutive_zeros(n: int)->(int, int):
    shift_amount = 0
    while n % 2 == 0:
        shift_amount += 1
        n >>= 1
    return (shift_amount, n)

def consecutive_ones(n: int)->(int, int):
    one_run_count = 0
    while n % 2 == 1:
        one_run_count += 1
        n >>= 1
    return (one_run_count, n)

class Operation:
    def __init__(self, op, cost, value, amount=None):
        self.op = op
        self.cost = cost
        self.value = value
        self.amount = amount

    def __repr__(self):
        if self.amount is not None:
            return (
                f"op: {self.op}({self.amount}),\tvalue: {self.value}, cost: {self.cost}"
            )
        else:
            return f"op: {self.op},\tvalue: {self.value}, cost: {self.cost}"
        pass


def print_operations(n: int, cost: int, ops: List[Operation]) -> None:
    print(f"Instruction sequence for {n}, total cost: {cost}:")
    for op in ops:
        print(op)
        pass
    print("-" * 45)
    return


class MultConst:
    OP_COSTS_DEFAULT = {
        "shift": 1,
        "add": 1,
        "subtract": 1,
        # "shift_add" = 1  # old RISC machines have this
    }

    def __init__(self, op_costs=OP_COSTS_DEFAULT, debug=True):
        self.op_costs = op_costs
        self.mult_cache = {}
        self.debug = debug

    def shift_cost(self, num: int) -> int:
        return 1

    def binary_sequence(self, n: int) -> List[Operation]:
        """Returns the cost and operation sequence using the binary
        representation of the number.

        In this approach, each one bit other than the highest-order
        one bit is a "shift" by the number of consecutive zeros
        followed by an addition.

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

        We'll assume cost one for add, subtract, and shift by any amount

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

        # FIXME allow negative numbers too.
        assert n >= 0, "We handle only positive numbers"

        if self.debug:
            print(bin(n)[2:])

        if n == 0:
            return (0, [Operation("constant 0", 0, 0)])
        elif n == 1:
            return (0, [Operation("noop", 0, 1)])

        result = []  # Sequence of operations
        cost = 0     # total cost of sequence
        while n > 1:

            # Handle low-order 0's with a single shift.
            # Note: those machines that can only do a single shift of one place
            # or those machines whose time varies with the shift amount, that is covered
            # by the self.shift_cost function
            m = n
            shift_amount, n  = consecutive_zeros(n)
            if shift_amount:
                shift_cost = self.shift_cost(shift_amount)
                cost += shift_cost
                result.append(Operation("shift", shift_cost, m, shift_amount))
                continue

            # Handle low-order 1's via adds and subtracts if subtracts are available.
            #
            one_run_count, m = consecutive_ones(n)
            if one_run_count:
                if "subtract" in self.op_costs and one_run_count > 2:
                    subtract_cost = self.op_costs["subtract"]
                    result.append(Operation("subtract", subtract_cost, n))
                    subtract_cost = self.shift_cost(one_run_count)
                    cost += subtract_cost
                    n += 1
                    pass
                else:
                    add_cost = self.op_costs["add"]
                    result.append(Operation("add", add_cost, n))
                    cost += add_cost
                    n -= 1
                    if n == 1:
                        break
                    pass
                pass
            pass

        result.reverse()
        return (cost, result)

    pass


if __name__ == "__main__":
    m = MultConst()
    for n in list(range(9)) + [53, 93]:
        cost, result = m.binary_sequence(n)
        print_operations(n, cost, result)

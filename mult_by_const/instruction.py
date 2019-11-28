"""Code around instructions and instruction sequences"""
from typing import List
from mult_by_const.util import bin2str, print_sep

FACTOR_FLAG = -1

OP2SHORT = {"add": "+", "subtract": "-", "shift": "<<"}


class Instruction:
    """Object containing information about a particular operation or instruction as it pertains
    to the instruction sequence"""

    def __init__(self, op: str, cost: float, amount: int):
        self.op = op  # The name of the operation; e.g. "shift", "add", "subtract"

        # "cost" is redundant and can be computed from the "op" and "amount";
        # we add it for convenience.
        self.cost = cost

        # If "op" is a "shift", then it is amount to shift.
        # if "op" is an "add or subtract", then it is either 1 if we
        # add/subtract one, and FACTOR_FLAG if we add/subtract a factor value.
        self.amount = amount

    def __repr__(self):
        op_str = OP2SHORT.get(self.op, self.op)
        if self.op == "shift":
            return f"{op_str} {self.amount}"
        elif self.op in ("add", "subtract"):
            operand = "(n)" if self.amount == FACTOR_FLAG else "1"
            return f"{op_str}{operand}"
        else:
            return f"{op_str} {self.amount}"

    def __str__(self):
        op_str = self.op
        if self.op in ("add", "subtract"):
            op_str += "(n)" if self.amount == FACTOR_FLAG else "(1)"
        else:
            op_str = f"{self.op}({self.amount})"
        op_str += ","
        return f"op: {op_str:12}\tcost: {self.cost:2}"


def print_instructions(
    instrs: List[Instruction], n=None, expected_cost=None, prefix=""
) -> None:
    print_sep("-")
    cost = instruction_sequence_cost(instrs)
    intro = f"{prefix}Instruction sequence"
    if n is not None:
        intro += f" for {n:2} = {bin2str(n)}"
    print(f"{intro}, cost: {cost:2}:")
    if n == 0:
        i = 0
        assert len(instrs) == 1
    else:
        i = 1
    j = 1
    for instr in instrs:
        if instr.op == "shift":
            j = i
            i <<= instr.amount
        elif instr.op == "add":
            i += 1 if instr.amount == 1 else j
        elif instr.op == "subtract":
            i -= 1 if instr.amount == 1 else j
        elif instr.op == "constant 0":
            pass
        elif instr.op == "noop":
            pass
        else:
            print(f"unknown op {instr.op}")
        print(f"{instr},\tvalue: {i:3}")
        pass

    print_sep()
    assert n is None or n == i, f"Multiplier should be {n}, not computed value {i}"
    assert (
        expected_cost is None or expected_cost == cost
    ), f"Cost should be {expected_cost}, not computed value {cost}"
    return


def instruction_sequence_cost(instrs: List[Instruction]) -> float:
    cost: float = 0
    for inst in instrs:
        cost += inst.cost
        pass
    return cost


def instruction_sequence_value(instrs: List[Instruction]) -> int:
    i, j = 1, 1
    for instr in instrs:
        if instr.op == "shift":
            j = i
            i <<= instr.amount
        elif instr.op == "add":
            if instr.amount == 1:
                i += 1
            else:
                i += j
        elif instr.op == "subtract":
            if instr.amount == 1:
                i -= 1
            else:
                i -= j
        elif instr.op == "constant 0":
            return 0
        elif instr.op == "noop":
            pass
        else:
            print(f"unknown op {instr.op}")
        pass

    return i


if __name__ == "__main__":
    instrs = [
        Instruction("shift", 1, 4),
        Instruction("add", 1, 1),
        Instruction("shift", 1, 2),
        Instruction("subtract", 1, FACTOR_FLAG),
    ]
    print(instrs)
    for inst in instrs:
        print(str(inst))
    print_instructions(instrs)

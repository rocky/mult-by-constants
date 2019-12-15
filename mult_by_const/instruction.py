# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Code around instructions and instruction sequences"""
from typing import List
from mult_by_const.util import bin2str, print_sep

FACTOR_FLAG = -1


OP2SHORT = {"add": "+", "makezero": "0", "negate": "(-n)", "shift": "<<", "subtract": "-"}
SHORT2OP = {v:k for k, v in OP2SHORT.items()}


class Instruction:
    """Object containing information about a particular operation or instruction as it pertains
    to the instruction sequence"""

    def __init__(self, op: str, amount: int, cost: float = 1):
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
        elif self.op in ("makezero", "negate"):
            return op_str
        elif self.op in ("add", "subtract"):
            operand = "n" if self.amount == FACTOR_FLAG else "1"
            return f"{op_str}{operand}"
        else:
            return f"{op_str} {self.amount}"

    def __str__(self):
        op_str = self.op
        if self.op in ("add", "subtract"):
            op_str += "(n)" if self.amount == FACTOR_FLAG else "(1)"
        elif self.op == "makezero":
            op_str = "0"
        elif self.op == "negate":
            op_str = "negate(n)"
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
        value = 0
        assert len(instrs) == 1
    else:
        value = 1

    if instrs:
        print(f"{value:9}: r0 = <initial value>")

    previous_value = 1
    for instr in instrs:
        if instr.op == "shift":
            previous_value = value
            value <<= instr.amount
        elif instr.op == "add":
            value += 1 if instr.amount == 1 else previous_value
        elif instr.op == "subtract":
            value -= 1 if instr.amount == 1 else previous_value
        elif instr.op == "makezero":
            value = 0
        elif instr.op == "negate":
            value = -value
        else:
            print(f"unknown op {instr.op}")
        print(f"{value:9}: {instr}")
        pass

    print_sep()
    assert n is None or n == value, f"Multiplier should be {n}, not computed value {value}"
    assert (
        expected_cost is None or expected_cost == cost
    ), f"Cost should be {expected_cost}, not computed value {cost}"
    return


def check_instruction_sequence_value(n: int, instrs: List[Instruction]) -> None:
    actual_value = instruction_sequence_value(instrs)
    assert (
        n == actual_value
    ), f"{instrs} value for {n} is {actual_value}; expecting {n}"
    return


def check_instruction_sequence_cost(cost: float, instrs: List[Instruction]) -> None:
    actual_cost = instruction_sequence_cost(instrs)
    assert cost == actual_cost, f"{instrs} cost is {actual_cost}; expecting {cost}"
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
        elif instr.op == "makezero":
            return 0
        elif instr.op == "negate":
            i = -i
        else:
            print(f"unknown op {instr.op}")
        pass

    return i

def str2instruction(s: str) -> Instruction:
    op_str = s[0:1]
    if op_str in ("+", "-"):
        amount = 1 if s[1:2] == "1" else FACTOR_FLAG
        op = SHORT2OP[op_str]
    elif s in ("(-n)", "0"):
        amount = 0
        op = SHORT2OP[s]
    else:
        op_str = s[0:2]
        if op_str == "<<":
            amount = int(s[2:], 10)
            op = SHORT2OP[op_str]
        else:
            raise RuntimeError(f"Unconvertable string {s}")
    return Instruction(op, amount)

def str2instructions(s: str) -> List[Instruction]:
    assert s[0:1] == "[" and s[-1:] == "]"
    instr_strs = s[1:-1].split(", ")
    return [str2instruction(inst_str) for inst_str in instr_strs]

if __name__ == "__main__":
    instrs = [
        Instruction("shift", 4),
        Instruction("add", 1),
        Instruction("shift", 2),
        Instruction("subtract", FACTOR_FLAG),
        Instruction("negate", 0),
    ]
    print(instrs)
    for inst in instrs:
        print(str(inst))
    print_instructions(instrs)
    print(
        f"Instruction value: {instruction_sequence_value(instrs)}, cost: {instruction_sequence_cost(instrs)}"
    )

    for inst in instrs:
        roundtrip_inst = str2instruction(repr(inst))
        print(f"inst: {repr(inst)}, str: {repr(roundtrip_inst)}")
        assert repr(inst) == repr(roundtrip_inst)
        print(str2instructions("[<< 4, +1, << 2, -(n)]"))

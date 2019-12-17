# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Code around instructions and instruction sequences"""
from typing import List
from mult_by_const.util import bin2str, print_sep

FACTOR_FLAG = -2  # r1 = r1 op r0 where r0 was the register to mul
REVERSE_SUBTRACT_1 = -1  # r1 = r0 - r1
REVERSE_SUBTRACT_FACTOR = -3 # r1 = r2 - r1


OP2SHORT = {
    "add": "+",
    "zero": "0",
    "negate": "-n",
    "nop": "nop",
    "shift": "<<",
    "subtract": "-",
}
SHORT2OP = {v: k for k, v in OP2SHORT.items()}


class Instruction:
    """Object containing information about a particular operation or instruction as it pertains
    to the instruction sequence"""

    def __init__(self, op: str, amount: int, cost: float = 1):
        self.op = op  # The name of the operation; e.g. "shift", "add", "subtract"

        # "cost" is redundant and can be computed from the "op" and "amount";
        # we add it for convenience.
        self.cost = cost

        # If "op" is a "shift", then it is amount to shift.

        # if "op" is an "add or subtract", then it is either:
        #    1 if we add/subtract one,
        #    FACTOR_FLAG if we add/subtract a factor value,
        #    REVERSE_SUBTRACT_1 if we reverse the operands and subtract,
        #    REVERSE_SUBTRACT_FACTOR if we reverse the operands and add the last factor,
        #
        self.amount = amount

    def __repr__(self):
        """Format instruction in compact form. No cost is shown"""
        op_str = OP2SHORT.get(self.op, self.op)
        if op_str == "<<":
            return f"n{op_str}{self.amount}"
        elif op_str in ("0", "nop", "-n"):
            return op_str
        elif op_str == "+":
            operand1 = "n"
            if self.amount == FACTOR_FLAG:
                operand2 = "m"
            elif self.amount == 1:
                operand2 = "1"
                pass
            else:
                operand2 = f"???{self.amount}"
            return f"{operand1}{op_str}{operand2}"
        elif op_str == "-":
            if self.amount == FACTOR_FLAG:
                operand1 = "n"
                operand2 = "m"
            elif self.amount == REVERSE_SUBTRACT_1:
                operand1 = "1"
                operand2 = "n"
            elif self.amount == 1:
                operand1 = "n"
                operand2 = "1"
            else:
                operand1 = "n"
                operand2 = f"???{self.amount}"
            return f"{operand1}{op_str}{operand2}"
        else:
            return f"{op_str} {self.amount}"

    def fmt(self, target="r1", op1="r1", op2="r1", r1="r0"):
        """format instruction as a full target and 2 operand assignment statement"""
        instr_str = f"{target} = "
        if self.op in ("add", "subtract"):
            instr_str += f"{op1} {OP2SHORT[self.op]} "
            instr_str += op2 if self.amount == FACTOR_FLAG else r1
        elif self.op == "zero":
            instr_str += "0"
        elif self.op == "negate":
            instr_str += f"-{op1}"
        elif self.op == "shift":
            instr_str += f"{op1} << {self.amount}"
        else:
            instr_str = f"{op1} {self.op} {op2}"
        instr_str += ";"
        return f"{instr_str:22}cost: {self.cost:2}"

    def __str__(self):
        """format instruction showing cost"""
        op_str = self.op
        if self.op == "add":
            if self.amount == FACTOR_FLAG:
                op_str += " n, m"
            elif self.amount == 1:
                op_str += " n, 1"
            else:
                op_str += f" ???{self.amount}"
                pass
        elif self.op == "subtract":
            if self.amount == FACTOR_FLAG:
                op_str += " n, m"
            elif self.amount == REVERSE_SUBTRACT_1:
                op_str += " 1, n"
            elif self.amount == 1:
                op_str += " n, 1"
            else:
                op_str += f"???{self.amount}"
        elif self.op in ("zero", "noop"):
            pass
        elif self.op == "negate":
            op_str += " n"
            pass
        elif self.op == "shift":
            op_str += f" n, {self.amount}"
        else:
            op_str = f"{self.op} {self.amount} ???"
        op_str += ";"
        return f"op: {op_str:22}cost: {self.cost:2}"

    def __eq__(self, other: object):
        for field in ("op", "cost", "amount"):
            if not hasattr(other, field):
                return False
            if getattr(self, field) != getattr(other, field):
                return False
            pass
        return True


def print_instructions(
    instrs: List[Instruction], n=None, expected_cost=None, prefix=""
) -> None:
    """Print the instruction-sequnce `instrs` in a nice, understandable way.
    """
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
        print(f"{value:9}: r0 = <initial value>; cost:  0")

    previous_value = 1
    last_target = "r0"
    target = "r1"
    for i, instr in enumerate(instrs):
        if instr.op == "shift":
            previous_value = value
            value <<= instr.amount
            if i < len(instrs) and instrs[i+1].amount != 1:
                target = "r2"
        elif instr.op == "add":
            value += 1 if instr.amount == 1 else previous_value
        elif instr.op == "subtract":
            value -= 1 if instr.amount == 1 else previous_value
        elif instr.op == "zero":
            value = 0
        elif instr.op == "negate":
            value = -value
        else:
            print(f"unknown op {instr.op}")
        print(f"{value:9}: {instr.fmt(target=target, op1=last_target, r1='r0')}")
        last_target = target
        target = "r1"
        pass

    print_sep()
    assert (
        n is None or n == value
    ), f"Multiplier should be {n}, not computed value {value}"
    assert (
        expected_cost is None or expected_cost == cost
    ), f"Cost should be {expected_cost}, not computed value {cost}"
    return


def check_instruction_sequence_value(n: int, instrs: List[Instruction]) -> None:
    """
    Check that the multiplication performed by the list of instructions `instrs`, is
    equal to passed-in expected multiplier `n`.
    """
    actual_value = instruction_sequence_value(instrs)
    assert n == actual_value, f"{instrs} value for {n} is {actual_value}; expecting {n}"
    return


def check_instruction_sequence_cost(cost: float, instrs: List[Instruction]) -> None:
    """Check that the instruction cost in `instrs`, is equal to passed-in expected cost `cost`.
    """
    actual_cost = instruction_sequence_cost(instrs)
    assert cost == actual_cost, f"{instrs} cost is {actual_cost}; expecting {cost}"
    return


def instruction_sequence_cost(instrs: List[Instruction]) -> float:
    """Check that the instruction sequence cost of the list of instructions `instrs`, is
    equal to passed-in expected cost `cost`.
    """
    cost: float = 0
    for inst in instrs:
        cost += inst.cost
        pass
    return cost


def instruction_sequence_value(instrs: List[Instruction]) -> int:
    """Return the cost associated with instruction sequence `instrs`.
    """
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
        elif instr.op == "zero":
            return 0
        elif instr.op == "negate":
            i = -i
        elif instr.op == "nop":
            pass
        else:
            print(f"unknown op {instr.op}")
        pass

    return i


# The next to functions assist in loading and dumping data.
def str2instruction(s: str) -> Instruction:
    if len(s) < 2:
        raise RuntimeError(f'Unconvertable string "{s}" is too short')
    if s[1] in ("+", "-"):
        if s[2] == "m":
            amount = FACTOR_FLAG
        elif s[2] == "1":
            amount = 1
        elif s[2] == "n":
            if s[1] == "-":
                amount = REVERSE_SUBTRACT_1
            else:
                raise RuntimeError(f"Unconvertable amount in subtract {s}")
        else:
            raise RuntimeError(f"Unconvertable amount in add/subtract {s}")
        pass
        op = SHORT2OP[s[1]]
    elif s in ("-n", "0", "nop"):
        amount = 0
        op = SHORT2OP[s]
    elif s[1] == "<":
        if s[1:3] != "<<":
            raise RuntimeError(f"Expecting shift operator got {s}")
        amount = int(s[3:], 10)
        op = SHORT2OP["<<"]
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
    instrs2 = str2instructions("[n<<4, n+1, n<<2, n-m, -n]")
    print(instrs2)
    assert instrs == instrs2
    for inst in instrs:
        print(str(inst))
    print_instructions(instrs)
    print(
        f"Instruction value: {instruction_sequence_value(instrs)}, cost: {instruction_sequence_cost(instrs)}"
    )

    for inst in instrs:
        roundtrip_inst = str2instruction(repr(inst))
        print(f"repr() vs roundtrip(): '{repr(inst)}' == '{repr(roundtrip_inst)}'")
        assert repr(inst) == repr(roundtrip_inst)
        pass

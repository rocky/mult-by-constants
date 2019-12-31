# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Code around instructions and instruction sequences"""
from typing import List, Optional
from mult_by_const.cpu import inf_cost
from mult_by_const.util import bin2str, print_sep

# Below r[1] is the register we started out with
OP_R1 = 1  # r[n] = r[n] op r[1]
FACTOR_FLAG = -2  # r[n] = r[n] op r[n-1]
REVERSE_SUBTRACT_1 = -1  # r[n] = r[1] - r[n]
REVERSE_SUBTRACT_FACTOR = -3 # r[n] = r[1] - r[n]


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
            elif self.amount == REVERSE_SUBTRACT_1:
                return f"1-{operand1}"
            elif self.amount == REVERSE_SUBTRACT_FACTOR:
                return f"m-{operand1}"
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
            elif self.amount == REVERSE_SUBTRACT_FACTOR:
                operand1 = "m"
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

    def fmt(self, target="r[n]", op1="r[n]", op2="r[n-1]", r1="r[1]"):
        """format instruction as an assignment statement with up to two arguments"""
        instr_str = f"{target} = "
        if self.op == "add":
            if self.amount == OP_R1:
                instr_str += f"{op1} + {r1}"
            elif self.amount == REVERSE_SUBTRACT_1:
                instr_str += f"{r1} - {op1}"
            elif self.amount == FACTOR_FLAG:
                instr_str += f"{op1} + {op2}"
            else:
                instr_str += f" ???{self.amount}"
        elif self.op == "subtract":
            if self.amount == OP_R1:
                instr_str += f"{op1} - {r1}"
            elif self.amount == FACTOR_FLAG:
                instr_str += f"{op1} - {op2}"
            elif self.amount == REVERSE_SUBTRACT_1:
                instr_str += f"{r1} - {op1}"
            elif self.amount == REVERSE_SUBTRACT_FACTOR:
                instr_str += f"{op2} - {op1}"
            else:
                instr_str += f" ???{self.amount}"
        elif self.op == "negate":
            instr_str += f"-{op1}"
        elif self.op == "nop":
            instr_str += f"{target}"
        elif self.op == "shift":
            instr_str += f"{op1} << {self.amount}"
        elif self.op == "zero":
            instr_str += "0"
        else:
            instr_str = f"{op1} {self.op} {op2}"
        instr_str += ";"
        return f"{instr_str:24}cost: {self.cost:2}"

    def __str__(self):
        """format instruction showing cost"""
        op_str = self.op
        if self.op == "add":
            if self.amount == FACTOR_FLAG:
                op_str += " n, m"
            elif self.amount == REVERSE_SUBTRACT_1:
                op_str += " 1, n"
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
        return f"op: {op_str:24}cost: {self.cost:2}"

    def __eq__(self, other: object):
        for field in ("op", "cost", "amount"):
            if not hasattr(other, field):
                return False
            if getattr(self, field) != getattr(other, field):
                return False
            pass
        return True


def print_instructions(
    instrs: List[Instruction], n=None, stored_cost=None, prefix=""
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
        print(f"{value:9}: r[1] = <initial value>; cost:  0")

    previous_value = 1
    last_target = "r[1]"
    target = "r[n]"
    for i, instr in enumerate(instrs):
        if instr.op == "shift":
            previous_value = value
            value <<= instr.amount
            if i + 1 < len(instrs) and instrs[i + 1].amount != OP_R1:
                target = "r[n]"
                pass
        elif instr.op == "add":
            if instr.amount == OP_R1:
                value += 1
            elif instr.amount == REVERSE_SUBTRACT_1:
                value = -(value + 1)
            elif instr.amount == FACTOR_FLAG:
                value += previous_value
            else:
                print(f"unknown add flag: {instr.amount}")
        elif instr.op == "subtract":
            if instr.amount == OP_R1:
                value -= 1
            elif instr.amount == REVERSE_SUBTRACT_1:
                value = 1 - value
            elif instr.amount == FACTOR_FLAG:
                value -= previous_value
            elif instr.amount == REVERSE_SUBTRACT_FACTOR:
                value = previous_value - value
            else:
                print(f"unknown subtract flag: {instr.amount}")
        elif instr.op == "zero":
            value = 0
        elif instr.op == "negate":
            value = -value
        elif instr.op == "nop":
            pass
        else:
            print(f"unknown op {instr.op}")
        print(f"{value:9}: {instr.fmt(target=target, op1=last_target, r1='r[1]')}")
        last_target = target
        target = "r[n]"
        pass

    print_sep()
    if instrs:
        assert (
            n is None or n == value
        ), f"Multiplier should be {n}, not computed value {value}."
        assert (
            stored_cost is None or stored_cost == cost
        ), f"Stored cost for {n} is {stored_cost}, but computed value is {cost}."
    else:
        assert n == 1, f"When no instructions, multiplier should be 1; got {n}."
    return


def check_instruction_sequence_value(n: int, instrs: Optional[List[Instruction]]) -> None:
    """
    Check that the multiplication performed by the list of instructions `instrs`, is
    equal to passed-in expected multiplier `n`.
    """
    if instrs is None:
        # Can't check so do nothing
        return
    actual_value = instruction_sequence_value(instrs)
    assert n == actual_value, f"value for {n} is {actual_value}; expecting {n}"
    return


def check_instruction_sequence_cost(cost: float, instrs: Optional[List[Instruction]], n=None) -> None:
    """Check that the instruction cost in `instrs`, is equal to passed-in expected cost `cost`.
    """
    actual_cost = inf_cost if cost == inf_cost else instruction_sequence_cost(instrs)
    prefix = f"{instrs} cost"
    prefix += f" for {n}" if n is not None else ""
    assert cost == actual_cost, f"{prefix} is {actual_cost}; expecting {cost}"
    return


def instruction_sequence_cost(instrs: Optional[List[Instruction]]) -> float:
    """Check that the instruction sequence cost of the list of instructions `instrs`, is
    equal to passed-in expected cost `cost`.
    """
    if instrs is None:
        return inf_cost
    cost: float = 0
    for inst in instrs:
        cost += inst.cost
        pass
    return cost

def instruction_sequence_value(instrs: Optional[List[Instruction]]) -> int:
    """Return the cost associated with instruction sequence `instrs`.
    """
    if instrs is None:
        return inf_cost
    n, m = 1, 1
    for instr in instrs:
        if instr.op == "shift":
            m = n
            n <<= instr.amount
        elif instr.op == "add":
            if instr.amount == OP_R1:
                n += 1
            elif instr.amount == FACTOR_FLAG:
                n += m
            elif instr.amount == REVERSE_SUBTRACT_1:
                n = -(n - 1)
            else:
                print(f"Invalid flag on add in {instr}")
                pass
            pass
        elif instr.op == "subtract":
            if instr.amount == OP_R1:
                n -= 1
            elif instr.amount == REVERSE_SUBTRACT_1:
                n = 1 - n
            elif instr.amount == FACTOR_FLAG:
                n -= m
            elif instr.amount == REVERSE_SUBTRACT_FACTOR:
                n = m - n
            else:
                print(f"Invalid flag on subtract in {instr}")
        elif instr.op == "zero":
            return 0
        elif instr.op == "negate":
            n = -n
        elif instr.op == "nop":
            pass
        else:
            print(f"unknown op {instr.op}")
        pass

    return n

def find_negatable(instrs: List[Instruction]) -> int:
    for (i, inst) in enumerate(instrs):
        if inst.op in ("negate", "subtract"):
            return i
        pass
    return -1


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
    print(find_negatable(instrs))
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

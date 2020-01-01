# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Various CPU profiles which includes instruction-cost models.
"""
from typing import Any, Callable, Dict, FrozenSet, Optional
from sys import maxsize as inf_cost

# Do the instructions allow up to 3 operands or 2?
# Two-operand instructions are of the form:
#  reg op= operand; for example r1 += 2 or r1 -= r2
# Three-instructons are of the form:
#  reg = operand1 op operand2; for example r1 = r2 + r3

INSTRUCTION_TYPES: FrozenSet[str] = frozenset(("two-address", "three-address"))

# Instruction costs. Note that:
# "shift" of one place can be simulated via a doubling add: r1 << 1 == r1 + r1
# "negate" can be simulated via "subtract" r1 - (r1 << 1)
# "zero" can be simulated via "subtract" and a number of other operations:
#     r1 - r1
# "nop" is kind of a placeholder for the initial register being an initial value, and that is
# why it is (and must be) 0.
#
RISC_equal_time_cost_profile: Dict[str, float] = {
    "add": 1,
    "copy": 1,
    "eps": 0.1,
    "negate": 1,
    "nop": 0,
    "shift": 1,
    "subtract": 1,
    "zero": 1,
    # "shift_add" = 1  # old RISC machines have this
}

# "add" and "copy" only
add_only_cost_profile: Dict[str, float] = {
    "add": 1,
    "copy": 1,
    "eps": 0.1,
    "nop": 0,
    "zero": inf_cost,  # Can't do in this model
}

# "add", "subtraction", "copy" only.
add_subtract_cost_profile: Dict[str, float] = {
    "add": 1,
    "copy": 1,
    "eps": 0.1,
    "nop": 0,
    "subtract": 1,
    "zero": 1,  # via subtract
}

OP_COST_PROFILES: Dict[str, Dict[str, float]] = {
    "RISC Equal Time": RISC_equal_time_cost_profile,
    "add only": add_only_cost_profile,
    "add_subtract": add_subtract_cost_profile,
}

# What is the maxumum number of temporary registers or temporary products are we
# allowed to keep around? The minimum is 2.
# Three registers allows for negation by reversing a subtraction's operands, e.g:
# r1 = r0 - r1 is the negative of r1 = r1 - r0
# If the instruction type is "two address", an additional copy is needed above to negate.
MAX_REGISTERS_DEFAULT: int = 3


class CPUProfile:
    # FIXME: allow for a shift function that varies with the shift amount
    def __init__(
        self,
        name: str,
        instruction_type: str,
        max_registers: int,
        costs: Dict[str, float],
        shift_cost_fn: Optional[Callable] = None,
    ):
        self.name = name
        self.instruction_type = instruction_type
        self.max_registers = max_registers
        self.costs = costs
        for field in ("add", "eps", "zero", "copy", "nop"):
            assert field in costs, f'A cost model needs to include  operation "{field}"'
        self.eps = self.costs["eps"]
        if shift_cost_fn is None:
            self.shift_cost_fn = lambda amount: shift_cost_equal_time
        else:
            self.shift_cost_fn = shift_cost_fn
            pass
        return

    def subtract_can_negate(self) -> bool:
        return "subtract" in self.costs and self.max_registers > 2

    def can_negate(self) -> bool:
        return "negate" in self.costs or self.subtract_can_negate()

    def can_subtract(self) -> bool:
        return "subtract" in self.costs

    def has_true_shift(self) -> bool:
        """Has a real "shift". If False we have to simulate this via a doubling "add".
        """
        return "shift" in self.costs

    def can_zero(self) -> bool:
        return self.can_negate() or self.costs["zero"] != inf_cost

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "instruction_type": self.instruction_type,
            "max_registers": self.max_registers,
            "instruction_costs": self.costs,
        }


def shift_cost_equal_time(shift_cost, amount: int) -> float:
    """
    In this shift-cost model, there is no cost penalty for shifting larger amounts.
    """
    return shift_cost


def shift_cost_double_only(shift_cost, amount: int) -> float:
    """
    In this shift-cost model, we can only shift by 1; essentially this is a doubling,
    which can be done via an "add" instruction. We'll pretend there is a single
    "shift" instruction, but when we go to print out the instructions, we'll
    unroll this into the multiple "double" instructions.
    """
    return amount


POWER_3addr_3reg = CPUProfile(
    name="POWER 3-address, 3-register",
    instruction_type="three-address",
    max_registers=3,
    costs=RISC_equal_time_cost_profile,
    shift_cost_fn=lambda amount: shift_cost_equal_time(
        RISC_equal_time_cost_profile["shift"], amount
    ),
)

chained_adds = CPUProfile(
    name="chained adds",
    instruction_type="two-address",
    max_registers=3,
    costs=add_only_cost_profile,
    shift_cost_fn=lambda amount: shift_cost_double_only(
        add_only_cost_profile["add"], amount
    ),
)

DEFAULT_CPU_PROFILE = POWER_3addr_3reg
SHORT2MODEL: Dict[str, Any] = {"RISC": POWER_3addr_3reg, "adds": chained_adds}

if __name__ == "__main__":
    print(POWER_3addr_3reg.can_negate())
    print(POWER_3addr_3reg.subtract_can_negate())
    print(POWER_3addr_3reg.shift_cost_fn(1))
    print(POWER_3addr_3reg.shift_cost_fn(2))
    print(chained_adds.can_negate())
    print(chained_adds.subtract_can_negate())
    print(chained_adds.to_dict())
    print(chained_adds.shift_cost_fn(1))
    print(chained_adds.shift_cost_fn(2))

# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Various instruction cost models.
"""
from typing import Dict, KeysView, FrozenSet

# Instruction costs. Note that:
# "shift" of one place can be simulated via a doubling add: r1 << 1 == r1 + r1
# "negate" can be simulated via "subtract" r1 - (r1 << 1)
# "makezero" can be simulated via "subtract" and a number of other operations:
#     r1 - r1
# "noop" is kind of a placeholder for the initial register being an initial value, and that is
# why it is (and must be) 0.
#
OP_COSTS_DEFAULT: Dict[str, int] = {
    "add": 1,
    "makezero": 1,
    "copy": 1,
    "negate": 1,
    "noop": 0,
    "shift": 1,
    "subtract": 1,
    # "shift_add" = 1  # old RISC machines have this
}

COST_PROFILE_NAME_DEFAULT = "RISC equal time"

# What instructions are available. For example:
# - Do we have an shift instruction that shifts by an arbitrary amount?
# - Is subtraction available?
INSTRUCTION_OPS_DEFAULT: KeysView[str] = OP_COSTS_DEFAULT.keys()

# Do the instructions allow up to 3 operands or 2?
# Two-operand instructions are of the form:
#  reg op= operand; for example r1 += 2 or r1 -= r2
# Three-instructons are of the form:
#  reg = operand1 op operand2; for example r1 = r2 + r3

INSTRUCTION_TYPES: FrozenSet[str] = frozenset(("two-address", "three-address"))

# What is the maxumum number of temporary registers or temporary products are we
# allowed to keep around? The minimum is 2.
# Three registers allows for negation by reversing a subtraction's operands, e.g:
# r1 = r0 - r1 is the negative of r1 = r1 - r0
# If the instruction type is "two address", an additional copy is needed above to negate.
MAX_REGISTERS_DEFAULT: int = 3

DEFAULT_MODEL = {
    "instruction_type": "three-address",
    "max_registers": MAX_REGISTERS_DEFAULT,
    "costs": OP_COSTS_DEFAULT,
    "cost_profile": COST_PROFILE_NAME_DEFAULT,
    "model_name": "POWER 3-address, 3-register",
}

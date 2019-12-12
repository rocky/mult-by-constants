# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Various instruction cost models.
"""

OP_COSTS_DEFAULT = {
    "shift": 1,
    "add": 1,
    "subtract": 1,
    "noop": 0,
    "const": 1,
    "zero": 1,
    # "shift_add" = 1  # old RISC machines have this
}

# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Various instruction cost models.
"""

OP_COSTS_DEFAULT = {
    "add": 1,
    "makezero": 1,
    "negate": 1,
    "noop": 0,
    "shift": 1,
    "subtract": 1,
    # "shift_add" = 1  # old RISC machines have this
}

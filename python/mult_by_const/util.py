# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Miscellaneous small utility routines"""

import sys
from typing import List, Tuple, Dict


def signum(n):
    return 1 if n > 0 else -1


def consecutive_zeros(n: int) -> Tuple[int, int]:
    shift_amount = 0
    while n % 2 == 0:
        shift_amount += 1
        n >>= 1
    return (shift_amount, n)


def consecutive_ones(n: int) -> Tuple[int, int]:
    one_run_count = 0
    while n % 2 == 1:
        one_run_count += 1
        n >>= 1
    return (one_run_count, n)


def default_shift_cost(num: int) -> int:
    # The default is to use a simple model where shifting by any amount is
    # done in a fixed amount of time which is the same as an add/subtract
    # operation.
    return 1


def bin2str(n: int) -> str:
    """Like built-in bin(), but we remove the leading 0b"""
    return f"-{bin(-n)[2:]}" if n < 0 else bin(n)[2:]


# Length of separator lines.
SEP_LEN = 60


def print_sep(sep: str = "=", out=sys.stdout) -> None:
    out.write(sep * SEP_LEN)
    out.write("\n")
    return

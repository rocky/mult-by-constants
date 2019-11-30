# Mode: -*- python -*-
# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>

import click
import os
import sys
from mult_by_const.mult import MultConst
from mult_by_const.instruction import print_instructions
from mult_by_const.version import VERSION

program = os.path.splitext(os.path.basename(__file__))[0]


@click.command()
@click.option(
    "--showcache/--no-showcache", "-S", default=False, help="Show multiplication cache."
)
@click.option(
    "--debug/--no-debug",
    "-d",
    default=False,
    help="Add trace output in multiplication-sequence searching.",
)
@click.option(
    "--binary-method/--no-binary-method",
    "-b",
    default=False,
    help="Use binary method instead of searching.",
)
@click.version_option(version=VERSION)
@click.argument("numbers", nargs=-1, type=int, required=True)
def main(showcache, binary_method, debug, numbers):
    """Searches for short sequences of shift, add, subtract instruction to compute multiplication
    by a constant.
    """
    mult = MultConst(debug=debug)
    for number in numbers:
        if binary_method:
            cost, instrs = mult.binary_sequence(number)
        else:
            cost, instrs = mult.find_mult_sequence(number)
        print_instructions(instrs, number, cost)
        pass
    if showcache:
        mult.mult_cache.dump()

    return


if __name__ == "__main__":
    main(sys.argv[1:])

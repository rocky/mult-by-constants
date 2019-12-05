# Mode: -*- python -*-
# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""
Command-line interface to multiplication sequence searching, caching
load, and dump.
"""

import click
import os
import sys
from mult_by_const.mult import MultConst
from mult_by_const.instruction import print_instructions
from mult_by_const.io import dump, dump_yaml, dump_json
from mult_by_const.version import VERSION

program = os.path.splitext(os.path.basename(__file__))[0]


@click.command()
@click.option("--to", type=int, required=False, help="Generate table up to this value.")
@click.option(
    "--showcache/--no-showcache",
    "-S",
    default=False,
    help="Show multiplication cache. This is forced on when either --fmt or --to is given.",
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
@click.option(
    "--fmt",
    type=click.Choice(["text", "json", "yaml"], case_sensitive=False),
    default="text",
    help="Format, JSON, YAML, or text, to use in dumping multiplication cache.",
)
@click.option(
    "--compact/--no-compact", default=False, help="Show cache in compact format."
)
@click.option("--output", "-o", type=click.File("w"), help="File path to dump cache.")
@click.version_option(version=VERSION)
@click.argument("numbers", nargs=-1, type=int)
def main(to, showcache, debug, binary_method, fmt, compact, output, numbers):
    """Searches for short sequences of shift, add, subtract instruction to compute multiplication
    by a constant.
    """
    mult = MultConst(debug=debug)
    if to:
        for number in range(2, to + 1):
            if binary_method:
                cost, instrs = mult.binary_sequence(number)
            else:
                cost, instrs = mult.find_mult_sequence(number)
                pass
            pass
        pass
    else:
        for number in numbers:
            if binary_method:
                cost, instrs = mult.binary_sequence(number)
            else:
                cost, instrs = mult.find_mult_sequence(number)

            print_instructions(instrs, number, cost)
            pass
        pass
    if output or showcache or to:
        if output is None:
            output = sys.stdout
        if fmt == "text":
            dump(mult.mult_cache, out=output)
        elif fmt == "yaml":
            dump_yaml(mult.mult_cache, out=output, compact=compact)
        else:
            assert fmt == "json"
            indent = None if compact else 2
            dump_json(mult.mult_cache, out=output, indent=indent)

    return


if __name__ == "__main__":
    main(sys.argv[1:])

"""
Test instruction-sequence class and its conversion to string routines
"""
from mult_by_const import Instruction, FACTOR_FLAG, str2instruction, str2instructions
import os


def test_instruction():
    debug = "DEBUG" in os.environ

    # Build instructions
    instrs = [
        Instruction("shift", 4),
        Instruction("add", 1),
        Instruction("shift", 2),
        Instruction("subtract", FACTOR_FLAG),
        Instruction("negate", 0),
    ]

    # Round-trip test instructions via conversions
    expect_str = """\
op: shift(4),   	cost:  1
op: add(1),     	cost:  1
op: shift(2),   	cost:  1
op: subtract(n),	cost:  1
op: negate(n),  	cost:  1
    """
    expect = expect_str.split(
        "\n"
    )
    for i, inst in enumerate(instrs):
        assert expect[i] == str(inst), f"{expect[i]}\n{str(inst)}"

        roundtrip_inst = str2instruction(repr(inst))
        assert repr(inst) == repr(
            roundtrip_inst
        ), f"inst: {repr(inst)} vs. {repr(roundtrip_inst)}"
        pass

    instrs_str = str(instrs)
    instrs2 = str2instructions(instrs_str)
    assert str(instrs2) == instrs_str
    instrs2_str = "\n".join(str(inst) for inst in instrs2)
    print(expect_str.strip())
    print('-' * 10)
    print(instrs2_str)
    assert expect_str.strip() == instrs2_str
    assert str2instruction("0").cost == 1


# If run as standalone
if __name__ == "__main__":
    test_instruction()

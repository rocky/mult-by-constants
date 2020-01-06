"""
Test instruction module
"""
from mult_by_const.instruction import (
    Instruction, OP_R1, FACTOR_FLAG,
    find_negatable,
    instruction_sequence_cost,
    instruction_sequence_value,
    print_instructions,
    str2instruction,
    str2instructions,
)

def test_instruction():
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

    instrs3 = [
        Instruction("shift-add", amount=4, flag=OP_R1),
        Instruction("shift-subtract", amount=2, flag=FACTOR_FLAG),
    ]
    print(instrs3)
    instrs4 = str2instructions("[n<<4+1, n<<2-m]")
    print(instrs4)
    assert instrs3 == instrs4
    for inst in instrs4:
        print(str(inst))
    print_instructions(instrs4)


# If run as standalone
if __name__ == "__main__":
    test_instruction()

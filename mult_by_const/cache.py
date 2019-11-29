"""Mutiplication sequence cache"""
from sys import maxsize
from typing import List, Tuple, Dict, Any

from mult_by_const.instruction import (
    check_instruction_sequence_cost,
    check_instruction_sequence_value,
    Instruction,
    instruction_sequence_cost,
)

from mult_by_const.util import print_sep


class MultCache:
    def __init__(self):
        self.clear()

    def check(self) -> None:
        # We do sorted so that in the future we can compare
        # consecutive pairs.
        for num in sorted(self.cache.keys()):
            lower, upper, finished, instrs = self.cache[num]
            if finished:
                assert lower == upper
                check_instruction_sequence_cost(upper, instrs)
                check_instruction_sequence_value(num, instrs)
            else:
                assert lower <= instruction_sequence_cost(instrs) <= upper
        return

    def clear(self) -> None:
        self.cache: Dict[int, Tuple[float, float, bool, List[Instruction]]] = {}
        # The following help with search statistics
        self.cache_hits_exact = 0
        self.cache_hits_partial = 0
        self.cache_misses = 0

    def dump(self) -> None:
        """Dump the instruction cache accumulated.
        """
        # FIXME: compute field widths dynamically
        for num in sorted(self.cache.keys()):
            lower, upper, finished, instrs = self.cache[num]
            upper_any: Any = upper
            if upper == maxsize:
                upper_any = "inf"
            if finished:
                cache_str = f"cost: {upper_any:7}"
                assert upper == lower
            else:
                cache_str = f"cost: ({lower},{upper_any:4}]"
                assert upper >= lower
            print(f"{num:4}: {cache_str};\t{str(instrs)}")
        print("\n")
        print(f"Cache hits (finished):\t\t{self.cache_hits_exact:4}")
        print(f"Cache hits (unfinished):\t{self.cache_hits_partial:4}")
        print(f"Cache misses:\t\t\t{self.cache_hits_partial:4}")
        print_sep()
        return

    def insert(
        self,
        n: int,
        cache_lower: float,
        cache_upper: float,
        finished: bool,
        instrs: List[Instruction],
    ) -> None:
        self.cache[n] = (cache_lower, cache_upper, False, instrs)

    def lookup(self, n: int) -> Tuple[float, float, bool, List[Instruction]]:
        """Check if we have cached search results for "n", and return that.
        If not in cached, we will return (0, 0, {}). Note that a prior
        result has been fully only searched if if the lower bound is equal to the
        upper bound.
        """
        cache_lower, cache_upper, finished, cache_instr = self.cache.get(
            n, (0, maxsize, False, [])
        )
        if finished:
            self.cache_hits_exact += 1
        elif cache_upper == maxsize:
            self.cache_misses += 1
        else:
            self.cache_hits_partial += 1
        return cache_lower, cache_upper, finished, cache_instr

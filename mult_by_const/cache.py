"""A multiplication-sequence cache module"""
from copy import deepcopy
import json
import sys
from sys import maxsize as inf_cost
from ruamel.yaml import YAML
from typing import List, Tuple, Dict, Any

from mult_by_const.instruction import (
    check_instruction_sequence_cost,
    check_instruction_sequence_value,
    Instruction,
    instruction_sequence_cost,
)

from mult_by_const.util import print_sep


class MultCache:
    """A multiplication-sequence cache object"""

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
            elif instrs:
                assert lower <= instruction_sequence_cost(instrs) <= upper
        return

    def clear(self) -> None:
        """Reset the multiplication cache, and cache statistics to an initial state.
        The inital state, has constants 0 and 1 preloaded.
        """
        self.cache: Dict[int, Tuple[float, float, bool, List[Instruction]]] = {
            0: (1, 1, True, [Instruction("constant", 1, 0)]),
            1: (0, 0, True, [Instruction("noop", 0, 0)]),
        }
        # The following help with search statistics
        self.hits_exact = 0
        self.hits_partial = 0
        self.misses = 0

    def reformat_cache(self) -> Dict[int, Any]:
        """Reorganize the instruction cache in a more machine-readable format"
        """
        table: Dict[int, Any] = {}
        for num in sorted(self.cache.keys()):
            lower, upper, finished, instrs = self.cache[num]
            if instrs:
                table[num] = {
                    "cost": upper,
                    "finished": "search-complete" if finished else "upper-bound",
                    "sequence": str(instrs)
                    }
                pass
            pass
        return table

    def dump_yaml(self, compact=False) -> None:
        table = self.reformat_cache()
        yaml = YAML()
        if compact:
            yaml.compact(seq_seq=False, seq_map=False)
        else:
            yaml.explicit_start = True
        yaml.dump(table, sys.stdout)

    def dump_json(self, indent=2) -> None:
        table = self.reformat_cache()
        print(json.dumps(table, sort_keys=True, indent=indent))

    def dump(self) -> None:
        """Dump the instruction cache accumulated.
        """
        # FIXME: compute field widths dynamically
        for num in sorted(self.cache.keys()):
            lower, upper, finished, instrs = self.cache[num]

            upper_any: Any = upper
            if upper == inf_cost:
                upper_any = "inf"
            if finished:
                cache_str = f"cost: {upper_any:7}"
                assert upper == lower
            else:
                cache_str = f"cost: ({lower},{upper_any:4}]"
                assert upper >= lower
            print(f"{num:4}: {cache_str};\t{str(instrs)}")
        print("\n")
        print(f"Cache hits (finished):\t\t{self.hits_exact:4}")
        print(f"Cache hits (unfinished):\t{self.hits_partial:4}")
        print(f"Cache misses:\t\t\t{self.misses:4}")
        print_sep()
        return

    def insert(
        self,
        n: int,
        lower: float,
        upper: float,
        finished: bool,
        instrs: List[Instruction],
    ) -> None:
        self.cache[n] = (lower, upper, finished, instrs)

    def insert_or_update(
        self,
        n: int,
        lower: float,
        upper: float,
        finished: bool,
        instrs: List[Instruction],
    ) -> None:
        """Insert value if it is not in cache or if the upper value is less than what is currently cached.
        """
        if n in self.cache:
            cache_upper = self.cache[n][1]
            do_insert = cache_upper > upper
        else:
            do_insert = True

        if do_insert:
            self.insert(n, lower, upper, finished, instrs)

    def lookup(self, n: int) -> Tuple[float, float, bool, List[Instruction]]:
        """Check if we have cached search results for "n", and return that.
        If not in cached, we will return (0, 0, {}). Note that a prior
        result has been fully only searched if if the lower bound is equal to the
        upper bound.
        """
        cache_lower, cache_upper, finished, cache_instrs = self.cache.get(
            n, (0, inf_cost, False, [])
        )
        if finished:
            self.hits_exact += 1
        elif n not in self.cache:
            self.misses += 1
        else:
            # FIXME: should we split out the case where there is *no*
            # information, but key has been seen as opposed to the
            # case where there not *complete* information?
            self.hits_partial += 1
        self.cache[n] = (cache_lower, cache_upper, finished, cache_instrs)
        return cache_lower, cache_upper, finished, deepcopy(cache_instrs)

    def update(
        self,
        n: int,
        lower: Any = None,  # FIXME: the below are really Union types
        upper: Any = None,
        finished: Any = None,
        instrs: Any = None,
    ) -> None:
        """Insert non-null field value(s) but we check first to see if:
           * key "n" has a cache entry.
           * non-empty field values are "better" than cached entries.

        See also "insert" or "insert_or_update"
        """
        cache_lower, cache_upper, cache_finished, cache_instrs = self.cache.get(
            n, (0, inf_cost, False, [])
        )
        worse = True

        # FIXME: Give warnings for any of the below?
        if lower is not None and lower > cache_lower:
            cache_lower = lower
        if upper is not None and upper < cache_upper:
            cache_upper = upper
            worse = False
        if finished is not None and not cache_finished:
            cache_finished = finished
        if instrs is not None and not worse:
            cache_instrs = instrs
        self.cache[n] = (cache_lower, cache_upper, cache_finished, cache_instrs)


if __name__ == "__main__":
    c = MultCache()
    assert sorted(c.cache.keys()) == [0, 1]
    c.insert(0, 1, 1, True, [Instruction("constant", 1, 0)])
    c.insert_or_update(1, 0, 0, True, [Instruction("noop", 0, 0)])
    c.dump()
    c.check()
    c.dump_yaml()

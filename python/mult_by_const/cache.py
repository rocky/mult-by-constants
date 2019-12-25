# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""A multiplication-sequence cache module"""
from typing import List, Tuple, Dict, Any

from mult_by_const.cpu import inf_cost, DEFAULT_CPU_PROFILE

from mult_by_const.instruction import (
    check_instruction_sequence_cost,
    check_instruction_sequence_value,
    Instruction,
    instruction_sequence_cost,
    OP_R1,
    FACTOR_FLAG,
    REVERSE_SUBTRACT_1,
    REVERSE_SUBTRACT_FACTOR,
)

from mult_by_const.version import VERSION


class MultCache:
    """A multiplication-sequence cache object"""

    def __init__(self, cpu_profile=DEFAULT_CPU_PROFILE, *args, **kwargs):
        self.version = VERSION
        self.cpu_profile = cpu_profile
        self.clear()

    def keys(self):
        return self.cache.keys()

    def values(self):
        return self.cache.values()

    def items(self):
        return self.cache.items()

    def __len__(self):
        return len(self.cache)

    def has_key(self, k):
        return k in self.cache

    def update(self, *args, **kwargs):
        return self.cache.update(*args, **kwargs)

    def __contains__(self, item):
        return item in self.cache

    def __iter__(self):
        return iter(self.cache)

    # There is also get(), clear(), detdefault(), pop() popitem(), copy()
    # pop, __cmp__, __contains__,

    def check(self) -> None:
        # We do sorted so that in the future we can compare
        # consecutive pairs.
        for num in sorted(self.cache.keys()):
            lower, upper, finished, instrs = self.cache[num]
            if finished:
                check_instruction_sequence_cost(upper, instrs)
                check_instruction_sequence_value(num, instrs)
                pass

            if instrs:
                assert lower <= instruction_sequence_cost(instrs) <= upper
        return

    def clear(self) -> None:
        """Reset the multiplication cache, and cache statistics to an initial state.
        The inital state, has constants 0 and 1 preloaded.
        """
        # Dictionaries keys in Python 3.8+ are in given in insertion order,
        # so we should insert 0 before 1.
        self.cache: Dict[int, Tuple[float, float, bool, List[Instruction]]] = {
            0: (1, 1, True, [Instruction("zero", 0, self.cpu_profile.costs["zero"])]),
            1: (0, 0, True, [Instruction("nop", 0, self.cpu_profile.costs["nop"])]),
        }

        if "negate" in self.cpu_profile.costs:
            negate_cost = self.cpu_profile.costs["negate"]
            self.cache[-1] = (
                negate_cost,
                negate_cost,
                True,
                [Instruction("negate", 0, negate_cost)],
            )
            pass

        # The following help with search statistics
        self.hits_exact = 0
        self.hits_partial = 0
        self.misses = 0

    def insert(
        self,
        n: int,
        lower: float,
        upper: float,
        finished: bool,
        instrs: List[Instruction],
    ) -> None:
        self.cache[n] = (lower, upper, finished, instrs[:])

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
            do_insert = cache_upper > upper or (
                cache_upper == upper and not self.cache[n][3]
            )
        else:
            do_insert = True

        if do_insert:
            self.insert(n, lower, upper, finished, instrs)

    def __getitem__(
        self, n: int, record=True
    ) -> Tuple[float, float, bool, List[Instruction]]:
        """Check if we have cached search results for "n", and return that.
        If not in cached, we will return (0, 0, {}). Note that a prior
        result has been fully only searched if if the lower bound is equal to the
        upper bound.
        """
        cache_lower, cache_upper, finished, cache_instrs = self.cache.get(
            n, (0, inf_cost, False, [])
        )
        if record:
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
        return cache_lower, cache_upper, finished, cache_instrs[:]

    def update_field(
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

        There is a special case for "finished". If "upper" is better than
        the cached entry, and "finished" is is None (unknown) as opposed
        to "False" or "True", then it is set "True".

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
            assert instrs is not None
            cache_upper = upper
            if upper < cache_lower:
                cache_lower = upper
            worse = False
        if finished is not None and not cache_finished:
            cache_finished = finished
        if instrs is not None and not worse:
            cache_instrs = instrs[:]
        if finished is None and not worse:
            cache_finished = True
            cache_lower = cache_upper
        self.cache[n] = (cache_lower, cache_upper, cache_finished, cache_instrs)

    def update_sequence_partials(self, instrs: List[Instruction]) -> None:  # noqa: C901
        """Make sure partial products for `instrs` are in cache.
        """
        n, m = 1, 1
        cost: float = 0
        for i, instr in enumerate(instrs):
            if instr.op == "shift":
                m = n
                n <<= instr.amount
            elif instr.op == "add":
                if instr.amount == OP_R1:
                    n += 1
                elif instr.amount == FACTOR_FLAG:
                    n += m
                else:
                    print(f"Invalid flag on add in {instr}")
                    pass
            elif instr.op == "subtract":
                if instr.amount == OP_R1:
                    n -= 1
                elif instr.amount == REVERSE_SUBTRACT_1:
                    n = 1 - n
                elif instr.amount == FACTOR_FLAG:
                    n -= m
                elif instr.amount == REVERSE_SUBTRACT_FACTOR:
                    n = m - n
                else:
                    raise RuntimeError(f"Invalid flag on subtract in {instr}")
            elif instr.op == "zero":
                return
            elif instr.op == "negate":
                n = -n
            elif instr.op == "nop":
                pass
            else:
                print(f"unknown op {instr.op}")
            cost += instr.cost
            self.insert_or_update(n, 0, cost, False, instrs[0 : i + 1])  # noqa
            pass


if __name__ == "__main__":
    multcache = MultCache()
    multcache.check()
    # Note: dictionaries keys in Python 3.8+ are in given in insertion order.
    assert list(multcache.keys()) == [0, 1, -1], "We should have at least -1, 0 and 1"
    multcache.check()
    multcache.insert(0, 1, 1, True, [Instruction("zero", 0, 1)])
    multcache.check()
    multcache.insert_or_update(1, 0, 0, True, [Instruction("nop", 0, 0)])
    multcache.check()

    instrs = [
        Instruction("shift", 4),
        Instruction("add", 1),
        Instruction("shift", 2),
        Instruction("subtract", FACTOR_FLAG),
        Instruction("negate", 0),
    ]
    multcache.update_sequence_partials(instrs)
    multcache.check()
    from mult_by_const.io import dump

    dump(multcache)
    multcache.clear()
    instrs = [
        Instruction("shift", 3),
        Instruction("subtract", 1),
        Instruction("shift", 2),
        Instruction("add", 1),
    ]
    multcache.update_sequence_partials(instrs)
    multcache.check()
    dump(multcache)

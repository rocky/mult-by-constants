"""A multiplication-sequence cache I/O routines"""

from typing import Dict, Any
from ruamel.yaml import YAML

import json
import sys

from mult_by_const.cache import MultCache, inf_cost
from mult_by_const.instruction import str2instructions
from mult_by_const.util import print_sep

def reformat_cache(cache: MultCache) -> Dict[int, Any]:
    """Reorganize the instruction cache in a more machine-readable format"
    """
    table: Dict[int, Any] = {}
    for num in sorted(cache.keys()):
        lower, upper, finished, instrs = cache.cache[num]
        if instrs:
            table[num] = {
                "cost": upper,
                "finished": "search-complete" if finished else "upper-bound",
                "sequence": str(instrs),
            }
            pass
        pass
    return table

def load_table(table: Dict[int, Any], check_consistency=True, cache=MultCache()) -> MultCache:
    """Reorganize read-in dictionary into the format used internally.
    """
    line = 0
    for n, value in table.items():
        line += 1
        for key in ("finished", "cost", "sequence"):
            if not hasattr(value, key):
                print(f"Error: item {line} has no key {key}; entry:\n{value}")
                continue
            upper = value.cost
            if value.finished == "search-complete":
                lower = upper
                finished = True
            else:
                # writing outside loses partial info
                lower = 0
                finished = False
        instrs = str2instructions(value.sequence)
        cache.insert(n, lower, upper, finished, instrs)
        pass
    if check_consistency:
        cache.check()
    return cache

def dump_yaml(cache: MultCache, compact=False) -> None:
    table = reformat_cache(cache)
    yaml = YAML()
    if compact:
        yaml.compact(seq_seq=False, seq_map=False)
    else:
        yaml.explicit_start = True
    yaml.dump(table, sys.stdout)

def dump_json(cache: MultCache, indent=2) -> None:
    table = reformat_cache(cache)
    print(json.dumps(table, sort_keys=True, indent=indent))

def dump(cache) -> None:
    """Dump the instruction cache accumulated.
    """
    # FIXME: compute field widths dynamically
    for num in sorted(cache.cache.keys()):
        lower, upper, finished, instrs = cache.cache[num]

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
    print(f"Cache hits (finished):\t\t{cache.hits_exact:4}")
    print(f"Cache hits (unfinished):\t{cache.hits_partial:4}")
    print(f"Cache misses:\t\t\t{cache.misses:4}")
    print_sep()
    return

def load_json(fd, reset_cache=True, cache=MultCache()) -> None:
    if reset_cache:
        cache.clear()
    return cache.load_table(json.load(fd))

def load_yaml(fd, reset_cache=False, cache=MultCache()) -> MultCache:
    if reset_cache:
        cache.clear()
    return cache.load_table(YAML().load(fd.read()))

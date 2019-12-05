# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""A multiplication-sequence cache I/O routines"""

from typing import Dict, Any
from ruamel.yaml import YAML

import json
import sys

from mult_by_const.cache import MultCache, inf_cost
from mult_by_const.instruction import str2instructions
from mult_by_const.util import print_sep

def dump_yaml(cache: MultCache, out=sys.stdout, compact=False) -> None:
    table = reformat_cache(cache)
    yaml = YAML()
    if compact:
        yaml.compact(seq_seq=False, seq_map=False)
    else:
        yaml.explicit_start = True  # type: ignore
    yaml.dump(table, out)

def dump_json(cache: MultCache, out=sys.stdout, indent=2) -> None:
    table = reformat_cache(cache)
    out.write(json.dumps(table, sort_keys=True, indent=indent))
    out.write("\n")

def dump(cache, out=sys.stdout) -> None:
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
        else:
            cache_str = f"cost: ({lower},{upper_any:4}]"
            assert upper >= lower
        out.write(f"{num:4}: {cache_str};\t{str(instrs)}\n")
    out.write("\n")
    out.write(f"Cache hits (finished):\t\t{cache.hits_exact:4}\n")
    out.write(f"Cache hits (unfinished):\t{cache.hits_partial:4}\n")
    out.write(f"Cache misses:\t\t\t{cache.misses:4}\n")
    print_sep(out=out)
    out.write("\n")
    return

def load_json(fd, mcache=MultCache()) -> None:
    mcache = load_table(json.load(fd), cache=mcache)
    mcache.check()
    return mcache

def load_table(table, check_consistency=True, cache=MultCache()) -> MultCache:
    """Reorganize read-in dictionary into the format used internally.
    """

    # FIXME: decide what to do about merging/comparing version and costs
    line = 0
    products = table["products"]
    for n, value in products.items():
        d = dict(value)
        line += 1
        for key in ("finished", "cost", "sequence"):
            if key not in d:
                print(f"Error: item {line} has no key {key}; entry:\n{d}")
                continue
            pass
        upper = d["cost"]
        finished = d["finished"] == "search-complete"
        instrs = str2instructions(d["sequence"])
        cache.insert(n, 0, upper, finished, instrs)
        pass
    if check_consistency:
        cache.check()
    return cache

def load_yaml(fd, cache=MultCache()) -> MultCache:
    mcache = load_table(YAML().load(fd.read()))
    mcache.check()
    return mcache

def reformat_cache(cache: MultCache) -> Dict[str, Dict[int, Any]]:
    """Reorganize the instruction cache in a more machine-readable format"
    """
    table: Dict[str, Dict[int, Any]] = {
        "version": cache.version,
        "costs": cache.costs,
        "products": {}
    }
    products = table["products"]
    for num in sorted(cache.keys()):
        lower, upper, finished, instrs = cache.cache[num]
        if instrs:
            products[num] = {
                "cost": upper,
                "finished": "search-complete" if finished else "upper-bound",
                "sequence": str(instrs),
            }
            pass
        pass
    return table


if __name__ == "__main__":
    import os.path as osp
    yaml_table = osp.join(osp.dirname(__file__), "..", "pytest", "data", "10-stdcost.yaml")
    mcache = load_yaml(open(yaml_table, "r"))

    dump(mcache)
    print_sep()
    dump_yaml(mcache)
    print_sep()
    dump_json(mcache)

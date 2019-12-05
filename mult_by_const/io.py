# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""A multiplication-sequence cache I/O routines"""

from typing import Dict, Any
from ruamel.yaml import YAML

import csv
import json
import sys

from mult_by_const.cache import MultCache, inf_cost
from mult_by_const.instruction import str2instructions
from mult_by_const.util import print_sep

CSV_DIALECT = "excel-tab"
CSV_FIELDNAMES = ("n", "cost", "search-status", "sequence")


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
    return


def dump_csv(cache: MultCache, out=sys.stdout) -> None:
    table = []
    for num in sorted(cache.keys()):
        lower, cost, finished, instrs = cache.cache[num]
        if instrs:
            table.append(
                {
                    "n": num,
                    "cost": cost,
                    "search-status": "completed" if finished else "upper-bound",
                    "sequence": str(instrs),
                }
            )
            pass
        pass

    writer = csv.DictWriter(out, dialect=CSV_DIALECT, fieldnames=CSV_FIELDNAMES)
    writer.writeheader()
    writer.writerows(table)


def dump_json(cache: MultCache, out=sys.stdout, indent=2) -> None:
    table = reformat_cache(cache)
    out.write(json.dumps(table, sort_keys=True, indent=indent))
    out.write("\n")


def dump_yaml(cache: MultCache, out=sys.stdout, compact=False) -> None:
    table = reformat_cache(cache)
    yaml = YAML()
    if compact:
        yaml.compact(seq_seq=False, seq_map=False)
    else:
        yaml.explicit_start = True  # type: ignore
    yaml.dump(table, out)


def load_csv(fd, mcache=MultCache()) -> MultCache:
    csv_reader = csv.DictReader(fd, dialect=CSV_DIALECT)
    for row in csv_reader:
        n = int(row["n"], 10)
        cost = int(row["cost"], 10)
        finished = row["search-status"] == "completed"
        instrs = str2instructions(row["sequence"])
        mcache.insert_or_update(n, 0, cost, finished, instrs)
        pass

    mcache.check()
    return mcache


def load_json(fd, mcache=MultCache()) -> MultCache:
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
        for key in ("search-status", "cost", "sequence"):
            if key not in d:
                print(f"Error: item {line} has no key {key}; entry:\n{d}")
                continue
            pass
        upper = d["cost"]
        finished = d["search-status"] == "completed"
        instrs = str2instructions(d["sequence"])
        cache.insert_or_update(n, 0, upper, finished, instrs)
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
        "products": {},
    }
    products = table["products"]
    for num in sorted(cache.keys()):
        lower, upper, finished, instrs = cache.cache[num]
        if instrs:
            products[num] = {
                "cost": upper,
                "search-status": "completed" if finished else "upper-bound",
                "sequence": str(instrs),
            }
            pass
        pass
    return table


if __name__ == "__main__":
    import os.path as osp

    # table_path = osp.join(
    #     osp.dirname(__file__), "..", "tables", "100-stdcost.yml"
    # )
    # mcache = load_yaml(open(table_path, "r"))

    # dump(mcache)
    # dump_yaml(mcache)
    # print_sep()
    # dump_json(mcache)
    # print_sep()
    # dump_csv(mcache)

    table_path = osp.join(osp.dirname(__file__), "..", "tables", "100-stdcost.csv")
    mcache = load_csv(open(table_path, "r"))
    dump(mcache)

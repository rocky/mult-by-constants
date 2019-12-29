# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Multiplication sequence searching."""

from typing import List, Tuple

from mult_by_const.multclass import MultConstClass
from mult_by_const.cpu import inf_cost, DEFAULT_CPU_PROFILE
from mult_by_const.binary_method import binary_sequence
from mult_by_const.search_methods import (
    search_add_one,
    search_add_or_subtract_one,
    # search_binary_method_with_cache,
    search_cache,
    search_negate_subtract_one,
    search_short_factors,
    search_subtract_one,
)

from mult_by_const.instruction import FACTOR_FLAG, Instruction, instruction_sequence_cost

from mult_by_const.util import default_shift_cost


class MultConst(MultConstClass):
    def __init__(
        self,
        cpu_model=DEFAULT_CPU_PROFILE,
        debug=False,
        shift_cost_fn=default_shift_cost,
        search_methods=None,
    ):
        super().__init__(cpu_model, debug, shift_cost_fn, search_methods)

    # FIXME: move info search_methods
    def try_shift_op_factor(
        self,
        n: int,  # Number we are seeking
        factor: int,  # factor to try to divide "n" by
        op: str,  # operation after "shift"; either "add" or "subtract"
        shift_amount: int,  # shift amount used in shift operation
        upper: float,  # maximum allowed cost for an instruction sequence.
        lower: float,  # cost of instructions seen so far
        instrs: List[Instruction],  # We build on this.
        candidate_instrs: List[
            Instruction
        ],  # If not empty, the best instruction sequence seen so for with cost "limit".
    ) -> Tuple[float, List[Instruction]]:
        if (n % factor) == 0:
            shift_cost = self.shift_cost(shift_amount)
            shift_op_cost = self.op_costs[op] + shift_cost

            # FIXME: figure out why lower != instruction_sequence_cost(instrs)
            lower = instruction_sequence_cost(instrs) + shift_op_cost

            if lower < upper:
                m = n // factor
                self.debug_msg(f"Trying factor {factor}...")
                try_cost, try_instrs = self.alpha_beta_search(
                    m, lower=lower, limit=(upper - (lower - shift_op_cost))
                )
                if try_cost < upper - lower:
                    try_instrs.append(Instruction("shift", shift_amount, shift_cost))
                    try_instrs.append(Instruction(op, FACTOR_FLAG, self.op_costs[op]))
                    try_cost += shift_op_cost
                    self.debug_msg(
                        f"*update {n} using factor {factor}; cost {try_cost} < previous limit {upper}"
                    )
                    self.mult_cache.update_field(
                        n, upper=try_cost, instrs=try_instrs
                    )
                    # Upper is the cost for the entire sequence; the remaining cost is in "lower".
                    # However, in candidate_cost we factored in the "shift_op_cost" so we need to remove that.
                    upper = try_cost
                    candidate_instrs = try_instrs
                pass
            pass
        return upper, candidate_instrs

    # FIXME: move info search_methods
    def try_plus_offset(
        self,
        n: int,  # Number we are seeking
        increment: int,  # +1 or -1 for now
        limit: float,  # maximum allowed cost for an instruction sequence.
        lower: float,  # cost of instructions seen so far
        instrs: List[
            Instruction
        ],  # If not empty, an instruction sequence with cost "limit".
        # We build on this.
        candidate_instrs: List[
            Instruction
        ],  # The best current candidate sequencer. It or a different sequence is returned.
        op_flag,
    ) -> Tuple[float, List[Instruction]]:

        op_str = "add" if increment < 0 else "subtract"
        op_cost = self.op_costs[op_str]
        try_lower = lower + op_cost
        if try_lower < limit:
            n1 = n + increment

            cache_lower, neighbor_cost, finished, neighbor_instrs = self.mult_cache[n1]
            if not finished:
                if self.debug:
                    which = "lower" if n1 < n else "upper"
                    self.debug_msg(f"Trying {which} neighbor {n1} of {n}...")
                    pass

                neighbor_cost, neighbor_instrs = self.alpha_beta_search(
                    n1, try_lower, limit=limit
                )

            try_cost = neighbor_cost + op_cost

            if try_cost < limit:
                self.debug_msg(
                    f"*neighbor {n} update cost {try_cost}, previously {limit}."
                )
                limit = try_cost
                neighbor_instrs.append(Instruction(op_str, op_flag, op_cost))
                lower = self.mult_cache[n][0]
                self.mult_cache.insert_or_update(
                    n, lower, try_cost, False, neighbor_instrs
                )
                candidate_instrs = neighbor_instrs
                pass

        return limit, candidate_instrs

    def find_mult_sequence(
        self, n: int, search_methods=None
    ) -> Tuple[float, List[Instruction]]:
        """Top-level searching routine. Computes binary method upper bound
        and then does setup to the alpha-beta search
        """

        cache_lower, limit, finished, cache_instrs = self.mult_cache[n]
        if finished:
            return limit, cache_instrs

        if search_methods is None:
            # Note timings show search_cache() *without* binary search is faster on one-shot
            # searches than search_binary_method_with_cache().
            if n > 0:
                self.search_methods = (
                    search_cache,
                    search_short_factors,
                    search_add_one,
                    search_subtract_one,
                )
            else:
                self.search_methods = (
                    search_cache,
                    search_short_factors,
                    search_add_or_subtract_one,
                    search_negate_subtract_one,
                )
                pass
            pass

        if limit == inf_cost:
            # The binary sequence gives a workable upper bound on the cost
            cache_lower, cache_instrs = binary_sequence(self, n)
            self.mult_cache.insert_or_update(n, 0, limit, False, cache_instrs)

        cost, instrs = self.alpha_beta_search(n, 0, limit=limit)
        self.mult_cache.update_field(n, upper=cost, finished=True, instrs=instrs)
        if instrs:
            return cost, instrs
        else:
            return limit, cache_instrs

    def alpha_beta_search(
        self, n: int, lower: float, limit: float
    ) -> Tuple[float, List[Instruction]]:
        """Alpha-beta search

        n: is the (sub-)multiplier we are seeking at this point in the
           search.  Note that it is *not* the initial multiplier
           sought.

        lower: is the cost used up until this point
               for the top-level searched multiplier. This number has
               to be added onto the cost for *n* when compared against
               the *limit* in order for multiplication via
               *n* to be considered a better sequence.

        limit: is the cost of the best sequence of instructions we've
               seen so far, and that is recorded in "results".  We get
               this value initially using the binary method, but it
               can be lowered as we find better sequences.

        We return the lowest cost we can find using "n" in the sequence. Note that we
        don't return the cost of computing "n", but rather of the total sequence. If
        you subtract the "lower" value *on entry* than that is the cost of computing "n".
        """

        self.debug_msg(
            f"alpha-beta search for {n} in at most {limit-lower} = max alotted cost: {limit}, incurred cost {lower}",
            2,
        )

        # FIXME: should be done in caller?
        cache_lower, cache_upper, finished, cache_instrs = self.mult_cache[n]
        if finished:
            self.debug_msg(
                f"alpha-beta using cache entry for {n} cost: {cache_upper}", -2
            )
            return cache_upper, [] if n == 1 else cache_instrs

        orig_n = n
        n, need_negation = self.need_negation(n)

        assert n > 0

        instrs: List[Instruction] = []
        m, shift_cost, shift_amount = self.make_odd(n, 0, instrs)

        lower += shift_cost
        if lower > limit:
            self.debug_msg(
                f"**alpha cutoff after shift for {n} incurred {lower} > {limit} alotted",
                -2,
            )
            return inf_cost, []

        # Make "m" negative if "n" was and search for that directly
        if need_negation:
            m = -m

        candidate_instrs: List[Instruction] = []

        # If we have caching enabled, m != 1 since caching will catch earlier.
        # However for saftey and extreme cases where we don't have caching,
        # we will test here.
        if m in (-1, 0, 1):
            _, limit, _, candidate_instrs = self.mult_cache[m]
            limit += shift_cost
            lower = limit
        else:

            # FIXME: might be "limit - shift" cost, but possibly a bug in
            # add/subtract one will prevent a needed cost update when this
            # happens. Investigate and fix.
            search_limit = limit

            for fn in self.search_methods:
                candidate_upper, candidate_instrs = fn(
                    self, m, search_limit, lower, instrs, candidate_instrs
                )
                if candidate_upper + shift_cost < search_limit:
                    search_limit = candidate_upper
                    self.debug_msg(
                        f"*alpha-beta lowering limit of {m} cost to {search_limit} via search {fn.__name__}"
                    )
                    pass
                pass
            if search_limit < limit:
                limit = search_limit + shift_cost
            pass
        if candidate_instrs:
            if shift_amount:
                candidate_instrs.append(Instruction("shift", shift_amount, shift_cost))
            self.mult_cache.insert_or_update(n, limit, limit, True, candidate_instrs)
        else:
            candidate_instrs = cache_instrs

        if not candidate_instrs:
            self.debug_msg(
                f"**cutoffs before anything found for {orig_n}; check/update instructions used to {limit - lower}"
            )
            self.mult_cache.update_field(n, lower=limit - lower)

        self.dedent()

        return limit, candidate_instrs

    pass


if __name__ == "__main__":
    from mult_by_const.instruction import print_instructions

    mconst = MultConst(debug=True)
    # cost, instrs = mconst.try_shift_op_factor(n, 5, "add", 2, min_cost, 0, [], bin_instrs)
    # assert min_cost == cost, "5 is not a factor of 27, so we keep old min_cost"
    # cost, instrs = mconst.try_shift_op_factor(n, 3, "add", 1, min_cost, 0, [], bin_instrs)
    # assert 4 == cost, f"Instrs should use the fact that 3 is a factor of {n}"
    # print_instructions(instrs, n, cost)

    # for n in [170, 1706] + list(range(340, 345)):
    #     min_cost, instrs = binary_sequence(mconst, n)
    #     cost, instrs = mconst.find_mult_sequence(n)
    #     print_instructions(instrs, n, cost)
    #     dump(mconst.mult_cache)
    #     mconst.mult_cache.check()
    #     # mconst.mult_cache.clear()

    # n = 343
    n = 12345678

    mconst = MultConst(debug=True)
    cost, instrs = mconst.find_mult_sequence(n)
    # print(instrs)
    print_instructions(instrs, n, cost)
    # from mult_by_const.io import dump

    # dump(mconst.mult_cache)

    # n = 17
    # cost, instrs = mconst.find_mult_sequence(n)
    # print_instructions(instrs, n, cost)
    # dump(mconst.mult_cache)

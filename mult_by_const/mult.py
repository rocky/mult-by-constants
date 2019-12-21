# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Multiplication sequence searching."""

from typing import List, Tuple
from copy import deepcopy

from mult_by_const.multclass import MultConstClass
from mult_by_const.cpu import inf_cost, DEFAULT_CPU_PROFILE
from mult_by_const.binary_method import binary_sequence
from mult_by_const.search_methods import (
    search_add_one,
    search_add_or_subtract_one,
    # search_binary_method,
    search_cache,
    search_negate_subtract_one,
    search_short_factors,
    search_subtract_one,
)

from mult_by_const.instruction import (
    FACTOR_FLAG,
    Instruction,
    instruction_sequence_cost,
    instruction_sequence_value,
)

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
        upper: float,  # cost of a valid instruction sequence
        lower: float,  # cost of instructions seen so far
        instrs: List[Instruction],  # An instruction sequence with cost "upper".
        # We build on this.
        candidate_instrs: List[
            Instruction
        ],  # The best current candidate sequencer. It or a different sequence is returned.
    ) -> Tuple[float, List[Instruction]]:
        if (n % factor) == 0:
            shift_cost = self.shift_cost(shift_amount)
            lower += self.op_costs[op] + shift_cost
            if lower < upper:
                m = n // factor
                if self.debug:
                    self.debug_msg(f"Trying factor {factor}...")
                try_cost, try_instrs = self.alpha_beta_search(m, lower=0, upper=upper - lower)
                if lower + try_cost < upper:
                    if self.debug:
                        self.debug_msg(
                            f"Update {n} using factor {factor}; cost {lower + try_cost} < previous best {upper}"
                        )
                    candidate_instrs = try_instrs + [
                        Instruction("shift", shift_amount, shift_cost)
                    ]
                    candidate_instrs.append(
                        Instruction(op, FACTOR_FLAG, self.op_costs[op])
                    )
                    candidate_instrs = candidate_instrs + instrs
                    upper = lower + try_cost + shift_cost
                pass
            pass
        return upper, candidate_instrs

    # FIXME: move info search_methods
    def try_plus_offset(
        self,
        n: int,  # Number we are seeking
        increment: int,  # +1 or -1 for now
        upper: float,  # cost of a valid instruction sequence
        lower: float,  # cost of instructions seen so far
        instrs: List[Instruction],  # An instruction sequence with cost "upper".
        # We build on this.
        candidate_instrs: List[
            Instruction
        ],  # The best current candidate sequencer. It or a different sequence is returned.
        op_flag,
    ) -> Tuple[float, List[Instruction]]:
        op_str = "add" if increment < 0 and n > 0 else "subtract"
        op_cost = self.op_costs[op_str]
        try_lower = lower + op_cost
        if try_lower < upper:
            n_inc = n + increment
            if self.debug:
                self.debug_msg(f"Trying neighbor {n_inc} of {n}...")
                pass

            neighbor_cost, neighbor_instrs = self.alpha_beta_search(
                n_inc, 0, upper - try_lower
            )

            try_cost = neighbor_cost + try_lower
            if try_cost < upper:
                if self.debug:
                    self.debug_msg(f"Neighbor {n_inc} update {try_cost} < {upper}.")

                n_instrs = deepcopy(neighbor_instrs)
                n_instrs.append(Instruction(op_str, op_flag, op_cost))
                n_cost = instruction_sequence_cost(n_instrs)
                self.mult_cache.insert_or_update(n, n_cost, n_cost, True, n_instrs)

                # Compute the caller's "n" (not the "n" passed here),
                # by adding on "instrs"
                candidate_instrs = n_instrs + instrs
                upper = instruction_sequence_cost(candidate_instrs)
                caller_n = instruction_sequence_value(candidate_instrs)
                self.mult_cache.insert(caller_n, 0, upper, False, candidate_instrs)
                pass

        return upper, candidate_instrs

    def find_mult_sequence(self, n: int, search_methods=None) -> Tuple[float, List[Instruction]]:
        """Top-level searching routine. Computes binary method upper bound
        and then does setup to the alpha-beta search
        """

        cache_lower, cache_upper, finished, cache_instr = self.mult_cache[n]
        if finished:
            return cache_upper, cache_instr

        if search_methods is None:
            if n > 0:
                self.search_methods = (
                    search_cache,
                    search_short_factors,
                    search_subtract_one,
                    search_add_one,
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

        if cache_upper == inf_cost:
            # The binary sequence gives a workable upper bound on the cost
            cache_upper, bin_instrs = binary_sequence(self, n)
            self.mult_cache.insert_or_update(n, 0, cache_upper, False, bin_instrs)

        cost, instrs = self.alpha_beta_search(n, 0, cache_upper)
        self.mult_cache.update_field(n, finished=True)
        return cost, instrs

    def check_for_cutoff(
        self, n: int, lower: float, upper: float, candidate_instrs: List[Instruction]
    ) -> float:

        candidate_cost = instruction_sequence_cost(candidate_instrs)
        if candidate_cost > upper:
            if self.debug:
                self.debug_msg(
                    f"**beta cutoff for {n} in cost {candidate_cost} >= {upper}"
                )
            # Our best for n won't appear in the final sequence. Still, can we
            # update the cache n?
            self.mult_cache.update_field(
                n, upper, candidate_cost, None, candidate_instrs
            )
            pass
        elif candidate_instrs:
            self.mult_cache.insert_or_update(n, candidate_cost, candidate_cost, True,
                                             candidate_instrs)
            upper = candidate_cost
        else:
            # If there are no candidate instructions, then we were unsuccessful
            # at finding any sequence. However update lower to note
            # how many instructions we needed to use to get nowhere.
            if self.debug:
                self.debug_msg(
                    f"cutoffs before anything found for {n}; check/update instructions used {lower}"
                )
            self.mult_cache.update_field(n, lower=lower)
        return upper

    def alpha_beta_search(
        self, n: int, lower: float, upper: float
    ) -> Tuple[float, List[Instruction]]:
        """Alpha-beta search

        n: is the (sub-)multiplier we are seeking at this point in the
           search.  Note that it is *not* the initial multiplier
           sought.

        lower: is the cost used up until this point
               for the top-level searched multiplier. This number has
               to be added onto the cost for *n* when compared against
               the *upper* in order for multiplication via
               *n* to be considered a better sequence.

        upper: is the cost of the best sequence of instructions we've
               seen so far, and that is recorded in "results".  We get
               this value initially using the binary method, but it
               can be lowered as we find better sequences.

        We return the lowest cost we can find using "n" in the sequence. Note that we
        don't return the cost of computing "n", but rather of the total sequence. If
        you subtract the "lower" value *on entry* than that is the cost of computing "n".
        """

        if self.debug:
            self.debug_msg(
                f"alpha-beta search for {n}; incurred cost: {lower}, max alotted cost: {upper}",
                2,
            )

        if lower > upper:
            if self.debug:
                self.debug_msg(
                    f"**alpha cutoff for {n} incurred {lower} > {upper} alotted", -2
                )
            return inf_cost, []

        # assert lower <= upper

        orig_n = n
        n, need_negation = self.need_negation(n)

        assert n > 0

        cache_lower, cache_upper, finished, candidate_instrs = self.mult_cache[n]

        if cache_upper < upper:
            # Better candidate is in sequence
            upper = cache_upper
        # elif cache_lower < lower:
        #     # No sequence found, but we may have used more instructions in the
        #     # process; so update lower to reflect that fact that we'll neede
        #     # to use at least this many instructions in the future
        #     lower = cache_lower

        instrs: List[Instruction] = []
        m, shift_cost, _ = self.make_odd(n, 0, instrs)

        # Make "m" negative if "n" was and search for that directly
        if need_negation:
            m = -m

        for fn in self.search_methods:
            upper, candidate_instrs = fn(
                self, m, upper, lower, instrs, candidate_instrs
            )

        upper = self.check_for_cutoff(
            orig_n, lower=lower, upper=upper, candidate_instrs=candidate_instrs
        )

        if self.debug:
            self.dedent()

        return upper, candidate_instrs

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

    n = 343

    mconst = MultConst(debug=True)
    cost, instrs = mconst.find_mult_sequence(n)
    print(instrs)
    print_instructions(instrs, n, cost)
    from mult_by_const.io import dump
    dump(mconst.mult_cache)

    # n = 17
    # cost, instrs = mconst.find_mult_sequence(n)
    # print_instructions(instrs, n, cost)
    # dump(mconst.mult_cache)

# Copyright (c) 2019 by Rocky Bernstein <rb@dustyfeet.com>
"""Multiplication sequence searching."""

from typing import List, Tuple
from copy import deepcopy

from mult_by_const.costs import OP_COSTS_DEFAULT

from mult_by_const.instruction import (
    FACTOR_FLAG,
    Instruction,
    instruction_sequence_cost,
    instruction_sequence_value,
)

from mult_by_const.util import (
    bin2str,
    consecutive_zeros,
    consecutive_ones,
    default_shift_cost,
)

from mult_by_const.cache import MultCache, inf_cost


class MultConst:
    def __init__(
            self, op_costs=OP_COSTS_DEFAULT, debug=False, shift_cost_fn=default_shift_cost, search_methods=None
    ):

        # Op_costs gives costs of using each kind of instruction.
        self.op_costs = op_costs
        self.shift_cost = shift_cost_fn

        # Cache prior searches
        # The key is the positive number looked up.
        # The value is a tuple of: lower bound, upper bound,
        # "finished" boolean, and an upper-bound instruction sequence.
        #
        # If the "finished" boolean is True, then the searching
        # previously completed, and "upper" has the final
        # cost. Otherwise, upper is undefined; a cutoff occurred previously
        # and searching wasn't complete. However, on subsquent
        # searches, we can query the lower bound and do another cutoff
        # if the current-search lower bound is not less than the
        # previously-recorded lower bound.

        # FIXME: give an examples here. Also attach names "alpha" and
        # and "beta" with the different types of cutoffs.
        self.mult_cache = MultCache(op_costs)

        if debug:
            # We use indent show nesting in debug output
            self.indent = 0
        self.debug = debug

        if search_methods is None:
            self.search_methods = (
                self.search_short_factors,
                self.search_subtract_one,
                self.search_add_one
            )
            pass
        else:
            self.search_methods = search_methods
        return

    def dedent(self) -> None:
        if self.debug:
            self.indent -= 2

    def debug_msg(self, s: str, relative_indent=0) -> None:
        print(f"{' '*self.indent}{s}")
        if relative_indent:
            self.indent += relative_indent

    def make_odd(
        self, n: int, cost: float, result: List[Instruction]
    ) -> Tuple[int, float]:
        """Handle low-order 0's with a single shift.
           Note: those machines that can only do a single shift of one place
           or those machines whose time varies with the shift amount, that is covered
           by the self.shift_cost function
        """
        shift_amount, n = consecutive_zeros(n)
        if shift_amount:
            shift_cost = self.shift_cost(shift_amount)
            cost += shift_cost
            result.append(Instruction("shift", shift_amount, shift_cost))
            pass
        return (n, cost)

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
                try_cost, try_instrs = self.alpha_beta_search(m, upper - lower)
                if lower + try_cost < upper:
                    if self.debug:
                        self.debug_msg(f"factor {factor} update")
                    candidate_instrs = try_instrs + [
                        Instruction("shift", shift_amount, shift_cost)
                    ]
                    candidate_instrs.append(
                        Instruction(op, FACTOR_FLAG, self.op_costs[op])
                    )
                    candidate_instrs = candidate_instrs + instrs
                    upper = lower + try_cost
                pass
            pass
        return upper, candidate_instrs

    def try_factors(
        self,
        n: int,  # Number we are seeking
        upper: float,  # cost of a valid instruction sequence
        lower: float,  # cost of instructions seen so far
        instrs: List[Instruction],  # An instruction sequence with cost "upper".
        # We build on this.
        candidate_instrs: List[
            Instruction
        ],  # The best current candidate sequencer. It or a different sequence is returned.
    ) -> Tuple[float, List[Instruction]]:

        # The first factors, 3 = 2+1, and 5 = 4+1, are done special
        # and out of the "while" loop below, because we don't want to
        # consider subtraction factors 2-1 = 1, or 4-1 = 3.
        #
        # The latter, 3, is covered by 2+1 of the "for" loop below

        for factor, shift_amount in ((3, 1), (5, 2)):
            if factor > n:
                break
            upper, candidate_instrs = self.try_shift_op_factor(
                n, factor, "add", shift_amount, upper, lower, instrs, candidate_instrs
            )
            pass

        i, j = 3, 8
        while j - 1 <= n:
            upper, candidate_instrs = self.try_shift_op_factor(
                n, j - 1, "subtract", i, upper, lower, instrs, candidate_instrs
            )
            upper, candidate_instrs = self.try_shift_op_factor(
                n, j + 1, "add", i, upper, lower, instrs, candidate_instrs
            )

            # Any other factors to try?

            i += 1
            j <<= 1
            pass
        return upper, candidate_instrs

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
    ) -> Tuple[float, List[Instruction]]:
        op_str = "add" if increment < 0 else "subtract"
        op_cost = self.op_costs[op_str]
        try_lower = lower + op_cost
        if try_lower < upper:
            n_inc = n + increment
            if self.debug:
                self.debug_msg(f"Trying neighbor {n_inc} of {n}...")
                pass

            neighbor_cost, neighbor_instrs = self.alpha_beta_search(
                n_inc, upper - try_lower
            )

            try_cost = neighbor_cost + try_lower
            if try_cost < upper:
                if self.debug:
                    self.debug_msg(f"Neighbor {n_inc} update {try_cost} < {upper}.")

                n_instrs = deepcopy(neighbor_instrs)
                n_instrs.append(Instruction(op_str, 1, op_cost))
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

    def binary_sequence(self, n: int) -> Tuple[float, List[Instruction]]:
        """Returns the cost and operation sequence using the binary
        representation of the number, assuming a (mostly empty)
        multiplication cache. (0 and 1 are always in the cache)

        If the cache has been populated, it is possible this will pick
        up a more optimal value from the cache and further reduce the
        sequence cost.

        In this (noncached) approach, each one bit other than the
        highest-order one bit is a "shift" by the number of
        consecutive zeros followed by an addition.

        If the number is even and not zero, then there is a final "shift".

        If subtraction is available, then each run of 1's in the
        binary representation is replaced by a shift of that amount
        followed by a subtraction.

        Since we generally prefer addition over subtraction:

             x = (x << 1) + x

        is preferable to:

             x = (x << 2) - x

        Examples:
        ---------

        We'll assume cost one for "add", "subtract", and "shift" by
        any amount.

        number  cost  remarks
        ------  ----  ------
        0:      0     do nothing; load constant zero
        1:      0     do nothing, load operand
        10:     1     shift one
        11:     2     shift one; add
        101:    2     shift two; add
        110     3     shift one; add; shift one
        111:    2     shift three; subtract one      - if subtract is available
        111:    4     shift one; add; shift one; add - if subtract is not available

        """

        if n == 0:
            return self.op_costs["zero"]

        # FIXME allow negative numbers too.
        assert n > 0, "We handle only positive numbers for now"

        cache_lower, cache_upper, finished, cache_instr = self.mult_cache[n]
        if finished:
            return (cache_upper, cache_instr)

        return self.binary_sequence_inner(n)

    def binary_sequence_inner(self, n: int) -> Tuple[float, List[Instruction]]:

        assert n > 0

        orig_n = n

        bin_instrs: List[Instruction] = []
        cost: float = 0  # total cost of sequence

        while n > 1:

            cache_lower, cache_upper, finished, cache_instrs = self.mult_cache[n]
            if cache_upper < inf_cost:
                cost += cache_upper
                cache_instrs.reverse()  # Because we compute in reverse order here
                bin_instrs += cache_instrs
                break

            n, cost = self.make_odd(n, cost, bin_instrs)

            if n == 1:
                break

            # Handle low-order 1's via "adds", and also "subtracts" if subtracts are available.
            #
            one_run_count, m = consecutive_ones(n)
            if one_run_count:
                if "subtract" in self.op_costs and one_run_count > 2:
                    subtract_cost = self.op_costs["subtract"]
                    bin_instrs.append(Instruction("subtract", 1, subtract_cost))
                    subtract_cost = self.shift_cost(one_run_count)
                    cost += subtract_cost
                    n += 1
                    pass
                else:
                    add_cost = self.op_costs["add"]
                    bin_instrs.append(Instruction("add", 1, add_cost))
                    cost += add_cost
                    n -= 1
                    pass
                pass
            pass

        bin_instrs.reverse()
        if self.debug:
            self.debug_msg(
                f"binary method for {orig_n} = {bin2str(orig_n)} has cost {cost}"
            )

        self.mult_cache.insert_or_update(orig_n, 0, cost, False, bin_instrs)

        return (cost, bin_instrs)

    def find_mult_sequence(self, n: int) -> Tuple[float, List[Instruction]]:
        """Top-level searching routine. Computes binary method upper bound
        and then does setup to the alpha-beta search
        """

        cache_lower, cache_upper, finished, cache_instr = self.mult_cache[n]
        if finished:
            return cache_upper, cache_instr

        if cache_upper == inf_cost:
            # The binary sequence gives a workable upper bound on the cost
            cache_upper, bin_instrs = self.binary_sequence(n)
            self.mult_cache.insert_or_update(n, 0, cache_upper, False, bin_instrs)

        cost, instrs = self.alpha_beta_search(n, cache_upper)
        self.mult_cache.update_field(n, finished=True)
        return cost, instrs

    def search_short_factors(
        self,
        n: int,  # Number we are seeking
        upper: float,  # cost of a valid instruction sequence
        lower: float,  # cost of instructions seen so far
        instrs: List[Instruction],  # An instruction sequence with cost "upper".
        # We build on this.
        candidate_instrs: List[
            Instruction
        ],  # The best current candidate sequencer. It or a different sequence is returned.
    ) -> Tuple[float, List[Instruction]]:
        return self.try_factors(n, upper, lower, instrs, candidate_instrs)

    def search_subtract_one(
        self,
        n: int,  # Number we are seeking
        upper: float,  # cost of a valid instruction sequence
        lower: float,  # cost of instructions seen so far
        instrs: List[Instruction],  # An instruction sequence with cost "upper".
        # We build on this.
        candidate_instrs: List[
            Instruction
        ],  # The best current candidate sequencer. It or a different sequence is returned.
    ) -> Tuple[float, List[Instruction]]:
        return self.try_plus_offset(n, -1, upper, lower, instrs, candidate_instrs)

    def search_add_one(
        self,
        n: int,  # Number we are seeking
        upper: float,  # cost of a valid instruction sequence
        lower: float,  # cost of instructions seen so far
        instrs: List[Instruction],  # An instruction sequence with cost "upper".
        # We build on this.
        candidate_instrs: List[
            Instruction
        ],  # The best current candidate sequencer. It or a different sequence is returned.
    ) -> Tuple[float, List[Instruction]]:
        return self.try_plus_offset(n, +1, upper, lower, instrs, candidate_instrs)

    def check_for_cutoff(self, n: int, upper: float, candidate_instrs: List[Instruction]) -> None:

        candidate_cost = instruction_sequence_cost(candidate_instrs)
        if candidate_cost >= upper:
            # We have another cutoff
            if self.mult_cache[n][-1] != candidate_instrs:
                if self.debug:
                    self.debug_msg(
                        f"**alpha cutoff for {n} in cost {candidate_cost} >= {upper}"
                    )
                    pass
                self.mult_cache.insert_or_update(
                    n, upper, candidate_cost, upper == candidate_cost, candidate_instrs
                )
                upper = candidate_cost
                pass
            pass
        else:
            self.mult_cache.insert_or_update(n, upper, upper, True, candidate_instrs)
            pass
        return

    def alpha_beta_search(
        self, n: int, upper: float
    ) -> Tuple[float, List[Instruction]]:
        """Alpha-beta search

        n: is the (sub-)multiplier we are seeking at this point in the
           search.  Note that it is *not* the initial multiplier
           sought.

        upper: is the cost of the best sequence of instructions we've
               seen so far, and that is recorded in "results".  We get
               this value initially using the binary method, but it
               can be lowered as we find better sequences.

        We return the lowest cost we can find using "n" in the sequence. Note that we
        don't return the cost of computing "n", but rather of the total sequence. If
        you subtract the "lower" value *on entry* than that is the cost of computing "n".
        """

        if self.debug:
            self.debug_msg(f"alpha-beta search for {n} with max cost: {upper}", 2)

        # Variable "lower" tracks the cost of potential instruction
        # sequences used in searching.  It starts off 0 on a new
        # search. As we break apart the number searched, lower
        # accumulates the glue cost to combine the subparts back
        # together. When "lower" ever exceeds "upper" for a sequence,
        # the sequence is abandoned because there's some other
        # sequence that is better.
        #
        # In contrast to "cache_upper", which tracks the cost of
        # "cache_instrs", we often don't have an instruction sequence
        # that has a cost equal to lower, unless "lower" == "upper",
        # in which case our searching is complete.

        lower: float = 0

        assert upper > 0  # or lower < upper

        cache_lower, cache_upper, finished, cache_instrs = self.mult_cache[n]
        if finished:
            self.dedent()
            return cache_upper, cache_instrs

        instrs: List[Instruction] = []
        m, shift_cost = self.make_odd(n, 0, instrs)

        # If we were given an even number, then add the shift cost
        # and compute upper bound on the resulting odd number
        if m != n:
            lower += shift_cost
            if lower >= upper:
                # Saw a better result prevously. Do a cutoff after
                # caching a partial or full result.
                self.mult_cache.update_field(n, lower=upper)
                if self.debug:
                    self.debug_msg(
                        f"**beta cutoff for {n} in cost {lower} > {upper}", -2
                    )
                return inf_cost, []

            cache_lower, cache_upper, finished, cache_instrs = self.mult_cache[m]
            cache_instrs = cache_instrs + instrs

            if finished:
                # We've gone through this routine before, or with "m",
                # i.e. "n" without the shift operation. So we have the
                # best searching solution we can find using this code.

                try_upper = lower + cache_upper
                if try_upper < upper:
                    # Update cache bounds for n, which includes the "shift"
                    upper = try_upper
                    self.mult_cache.insert_or_update(
                        n, lower, upper, False, cache_instrs
                    )

                # Return what we got. The caller level may discard this
                # either immediately or eventually.
                self.dedent()
                return upper, cache_instrs
            pass

        # If no (incomplete) cached value found, use
        # the binary sequence which gives a workable upper bound on the cost.
        if cache_upper == inf_cost:
            bin_cost, bin_instrs = self.binary_sequence_inner(m)

            # Cache the binary sequence portion result
            self.mult_cache.insert(m, 0, bin_cost, False, bin_instrs)

            # Now tack on the instructions that got us to this point,
            # and pretend this is the cached value. We may
            # use this if we can't find a better sequence below
            cache_instrs = bin_instrs + instrs
            cache_upper = lower + bin_cost

        if cache_upper < upper:
            upper = cache_upper
            pass

        candidate_instrs = cache_instrs

        for fn in self.search_methods:
            upper, candidate_instrs = fn(
                m, upper, lower, instrs, candidate_instrs
            )

        self.check_for_cutoff(n, upper, candidate_instrs)

        self.dedent()
        return upper, candidate_instrs

    pass


if __name__ == "__main__":
    from mult_by_const.instruction import print_instructions
    # from mult_by_const.io import dump

    # m = MultConst(debug=True)
    # cost, instrs = m.binary_sequence(340)
    # cost, instrs = m.try_shift_op_factor(n, 5, "add", 2, min_cost, 0, [], bin_instrs)
    # assert min_cost == cost, "5 is not a factor of 27, so we keep old min_cost"
    # cost, instrs = m.try_shift_op_factor(n, 3, "add", 1, min_cost, 0, [], bin_instrs)
    # assert 4 == cost, f"Instrs should use the fact that 3 is a factor of {n}"
    # print_instructions(instrs, n, cost)

    # for n in [170, 1706] + list(range(340, 345)):
    #     min_cost, instrs = m.binary_sequence(n)
    #     cost, instrs = m.find_mult_sequence(n)
    #     print_instructions(instrs, n, cost)
    #     dump(m.mult_cache)
    #     m.mult_cache.check()
    #     # m.mult_cache.clear()

    n = 78

    mconst = MultConst(debug=True)
    cost, instrs = mconst.find_mult_sequence(n)
    print_instructions(instrs, n, cost)

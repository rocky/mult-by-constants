#!/usr/bin/env python
from typing import List, Tuple
from sys import maxsize
from copy import deepcopy

from mult_by_const.instruction import (
    FACTOR_FLAG,
    Instruction,
    print_instructions,
    instruction_sequence_cost,
    instruction_sequence_value,
)

from mult_by_const.util import (
    bin2str,
    consecutive_zeros,
    consecutive_ones,
    default_shift_cost,
)

from mult_by_const.cache import MultCache


class MultConst:
    OP_COSTS_DEFAULT = {
        "shift": 1,
        "add": 1,
        "subtract": 1,
        "noop": 0,
        "const": 1,
        # "shift_add" = 1  # old RISC machines have this
    }

    def __init__(
        self, op_costs=OP_COSTS_DEFAULT, debug=True, shift_cost_fn=default_shift_cost
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
        self.mult_cache = MultCache()

        self.debug = debug

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
            result.append(Instruction("shift", shift_cost, shift_amount))
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
                    print(f"Trying factor {factor}...")
                try_cost, try_instrs = self.alpha_beta_search(m, upper - lower)
                if lower + try_cost < upper:
                    if self.debug:
                        print(f"factor {factor} update")
                    candidate_instrs = try_instrs + [
                        Instruction("shift", shift_cost, shift_amount)
                    ]
                    candidate_instrs.append(
                        Instruction(op, self.op_costs[op], FACTOR_FLAG)
                    )
                    candidate_instrs = candidate_instrs + instrs
                    upper = lower + try_cost
                pass
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
                print(f"Trying neighbor {n_inc}...")
                pass

            # FIXME: check cache first!
            neighbor_cost, neighbor_instrs = self.alpha_beta_search(
                n_inc, upper - try_lower
            )
            try_cost = neighbor_cost + try_lower
            if try_cost < upper:
                if self.debug:
                    print(f"Neighbor {n_inc} update {try_cost} < {upper}.")

                n_instrs = deepcopy(neighbor_instrs)
                n_instrs.append(Instruction(op_str, op_cost, 1))
                n_cost = instruction_sequence_cost(n_instrs)
                self.mult_cache.insert(n, n_cost, n_cost, True, n_instrs)

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
        representation of the number.

        In this approach, each one bit other than the highest-order
        one bit is a "shift" by the number of consecutive zeros
        followed by an addition.

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

        We'll assume cost one for add, subtract, and shift by any amount

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

        # FIXME allow negative numbers too.
        assert n >= 0, "We handle only positive numbers"
        cache_lower, cache_upper, finished, cache_instr = self.mult_cache.lookup(n)
        if finished:
            return (cache_upper, cache_instr)

        return self.binary_sequence_inner(n)

    def binary_sequence_inner(self, n: int) -> Tuple[float, List[Instruction]]:
        assert n > 0
        orig_n = n

        bin_instrs: List[Instruction] = []
        cost: float = 0  # total cost of sequence
        while n > 1:

            n, cost = self.make_odd(n, cost, bin_instrs)

            if n == 1:
                break

            # Handle low-order 1's via "adds", and also "subtracts" if subtracts are available.
            #
            one_run_count, m = consecutive_ones(n)
            if one_run_count:
                if "subtract" in self.op_costs and one_run_count > 2:
                    subtract_cost = self.op_costs["subtract"]
                    bin_instrs.append(Instruction("subtract", subtract_cost, 1))
                    subtract_cost = self.shift_cost(one_run_count)
                    cost += subtract_cost
                    n += 1
                    pass
                else:
                    add_cost = self.op_costs["add"]
                    bin_instrs.append(Instruction("add", add_cost, 1))
                    cost += add_cost
                    n -= 1
                    pass
                pass
            pass

        bin_instrs.reverse()
        if self.debug:
            print(f"binary method for {orig_n} = {bin2str(orig_n)} has cost {cost}")

        self.mult_cache.insert(orig_n, 0, cost, False, bin_instrs)

        return (cost, bin_instrs)

    def find_mult_sequence(self, n: int) -> Tuple[float, List[Instruction]]:
        """Top-level searching routine. Computes binary method upper bound
        and then does setup to the alpha-beta search
        """

        cache_lower, cache_upper, finished, cache_instr = self.mult_cache.lookup(n)
        if finished:
            return cache_upper, cache_instr

        if cache_upper == maxsize:
            # The binary sequence gives a workable upper bound on the cost
            cache_upper, bin_instrs = self.binary_sequence(n)
            self.mult_cache.insert(n, 0, cache_upper, False, bin_instrs)

        cost, instrs = self.alpha_beta_search(n, cache_upper)
        return cost, instrs

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
            print(f"\nalpha-beta search for {n} in max cost: {upper}")

        # Lowers the cost of the instruction
        # sequence we've seen so far.  This sequence is
        # not the full sequence until we reach the end of
        # this routine.
        # If lower ever exceeds "upper", then this sequence is
        # abandoned because there's some other sequence that is
        # better.
        lower: float = 0

        assert upper > 0  # or lower < upper

        cache_lower, cache_upper, finished, cache_instrs = self.mult_cache.lookup(n)
        if finished:
            return upper, cache_instrs

        instrs: List[Instruction] = []
        m, shift_cost = self.make_odd(n, 0, instrs)

        # If we were given an even number, then add the shift cost
        # and compute upper bound on the resulting odd number
        if m != n:
            lower += shift_cost
            if lower >= upper:
                # Saw a better result prevously. Do a cutoff after
                # caching a partial or full result.
                if m == 1:
                    # n is a power of two; shift is probably the best
                    # you can do here, except for may when n == 2,
                    # and then maybe and "add" might be faster under
                    # some cost models.
                    self.mult_cache.insert(n, upper, upper, True, instrs)
                else:
                    cost = (
                        cache_upper if cache_upper == maxsize else lower + cache_upper
                    )
                    self.mult_cache.insert(n, lower, cost, False, instrs)
                if self.debug:
                    print(f"**beta cutoff for {n} in cost {lower} > {upper}")
                return maxsize, []

            cache_lower, cache_upper, finished, cache_instrs = self.mult_cache.lookup(m)
            cache_instrs = cache_instrs + instrs

            if finished:
                # We've gone through this routine before, or with "m",
                # i.e. "n" without the shift operation. So we have the
                # best searching solution we can find using this code.

                try_upper = lower + cache_upper
                if try_upper < upper:
                    # Update cache bounds for n, which includes the "shift"
                    print(f"XXX 2 {try_upper} < {upper}")
                    upper = try_upper
                    self.mult_cache(n, lower, upper, False, cache_instrs)
                else:
                    print(f"XXX {try_upper} >= {upper}")

                # Return what we got. The caller level may discard this
                # either immediately or eventually.
                return upper, cache_instrs
            pass

        # If no (incomplete) cached value found, use
        # the binary sequence which gives a workable upper bound on the cost.
        if cache_upper == maxsize:
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
        # The first factors, 3 = 2+1, and 5 = 4+1, are done special
        # and out of the "while" loop below, because we don't want to
        # consider subtraction factors 2-1 = 1, or 4-1 = 3.
        #
        # The latter, 3, is covered by 2+1 of the "for" loop below

        for factor, shift_amount in ((3, 1), (5, 2)):
            if factor > n:
                break
            upper, candidate_instrs = self.try_shift_op_factor(
                m, factor, "add", shift_amount, upper, lower, instrs, candidate_instrs
            )
            pass

        i, j = 3, 8
        while j - 1 <= n:
            upper, candidate_instrs = self.try_shift_op_factor(
                m, j - 1, "subtract", i, upper, lower, instrs, candidate_instrs
            )
            upper, candidate_instrs = self.try_shift_op_factor(
                m, j + 1, "add", i, upper, lower, instrs, candidate_instrs
            )

            # Any other factors to try?

            i += 1
            j <<= 1
            pass

        # Try subtracting one
        upper, candidate_instrs = self.try_plus_offset(
            m, -1, upper, lower, instrs, candidate_instrs
        )

        # FIXME: Do the same for "add" as above

        candidate_cost = instruction_sequence_cost(candidate_instrs)
        if candidate_cost >= upper:
            # We have another cutoff
            if self.mult_cache.lookup(n)[-1] != candidate_instrs:
                if self.debug:
                    print(f"**alpha cutoff for {n} in cost {candidate_cost} >= {upper}")
                    pass
                self.mult_cache.insert(
                    n, upper, candidate_cost, upper == candidate_cost, candidate_instrs
                )
                upper = candidate_cost
                pass
            pass
        else:
            self.mult_cache.insert(n, upper, upper, True, candidate_instrs)
            pass
        return upper, candidate_instrs

    pass


if __name__ == "__main__":
    m = MultConst()
    # for n in list(range(9)) + [53, 93]:
    #     cost, instrs = m.binary_sequence(n)
    #     print_instructions(instrs, n, cost)

    # n = 27
    # min_cost, bin_instrs = m.binary_sequence(n)
    # cost, instrs = m.try_shift_op_factor(n, 5, "add", 2, min_cost, 0, [], bin_instrs)
    # assert min_cost == cost, "5 is not a factor of 27, so we keep old min_cost"

    # cost, instrs = m.try_shift_op_factor(n, 3, "add", 1, min_cost, 0, [], bin_instrs)
    # assert 4 == cost, f"Instrs should use the fact that 3 is a factor of {n}"
    # print_instructions(instrs, n, cost)

    # for n in range(340, 344):
    for n in [1706]:
        min_cost, instrs = m.binary_sequence(n)
        cost, instrs = m.find_mult_sequence(n)
        print_instructions(instrs, n, cost)
        m.mult_cache.dump()
        m.mult_cache.check()
        # m.mult_cache.clear()

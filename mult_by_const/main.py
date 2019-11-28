#!/usr/bin/env python
from typing import List, Tuple, Dict, Any
from sys import maxsize

from mult_by_const.instruction import (
    FACTOR_FLAG,
    Instruction,
    print_instructions,
    instruction_sequence_cost,
)

from mult_by_const.util import (
    bin2str,
    consecutive_zeros,
    consecutive_ones,
    default_shift_cost,
    print_sep,
)


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
        self.clear_mult_cache()

        self.debug = debug

    def cache_lookup(self, n: int) -> Tuple[float, float, bool, List[Instruction]]:
        """Check if we have cached search results for "n", and return that.
        If not in cached, we will return (0, 0, {}). Note that a prior
        result has been fully only searched if if the lower bound is equal to the
        upper bound.
        """
        cache_lower, cache_upper, finished, cache_instr = self.mult_cache.get(
            n, (0, maxsize, False, [])
        )
        if finished:
            self.cache_hits_exact += 1
        elif cache_upper == maxsize:
            self.cache_misses += 1
        else:
            self.cache_hits_partial += 1
        return cache_lower, cache_upper, finished, cache_instr

    def clear_mult_cache(self) -> None:
        self.mult_cache: Dict[int, Tuple[float, float, bool, List[Instruction]]] = {}
        # The following help with search statistics
        self.cache_hits_exact = 0
        self.cache_hits_partial = 0
        self.cache_misses = 0

    def dump_mult_cache(self) -> None:
        """Dump the instruction cache accumulated.
        """
        for num in sorted(self.mult_cache.keys()):
            lower, upper, finished, instrs = self.mult_cache[num]
            upper_any: Any = upper
            if upper == maxsize:
                upper_any = "inf"
            if finished:
                cache_str = f"cost: {upper_any:9}"
                assert upper == lower
            else:
                cache_str = f"cost: {(lower + 1):2} ..{upper_any:4}"
                assert upper > lower
            print(f"{num:3}: {cache_str};\t{str(instrs)}")
        print("\n")
        print(f"Cache hits (finished):\t\t{self.cache_hits_exact:4}")
        print(f"Cache hits (unfinished):\t{self.cache_hits_partial:4}")
        print(f"Cache misses:\t\t\t{self.cache_hits_partial:4}")
        print_sep()
        return

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
        instrs: List[Instruction],  # An instruction sequence with cost "upper"
        candidate_instrs: List[
            Instruction
        ],  # The best current candidate sequencer. It is updated.
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
        if n == 0:
            return (1, [Instruction("constant 0", 1, 0)])
        elif n == 1:
            return (0, [Instruction("noop", 0, 0)])

        return self.binary_sequence_inner(n)

    def binary_sequence_inner(self, n: int) -> Tuple[float, List[Instruction]]:
        assert n > 0
        orig_n = n

        result: List[Instruction] = []
        cost: float = 0  # total cost of sequence
        while n > 1:

            n, cost = self.make_odd(n, cost, result)

            if n == 1:
                break

            # Handle low-order 1's via "adds", and also "subtracts" if subtracts are available.
            #
            one_run_count, m = consecutive_ones(n)
            if one_run_count:
                if "subtract" in self.op_costs and one_run_count > 2:
                    subtract_cost = self.op_costs["subtract"]
                    result.append(Instruction("subtract", subtract_cost, 1))
                    subtract_cost = self.shift_cost(one_run_count)
                    cost += subtract_cost
                    n += 1
                    pass
                else:
                    add_cost = self.op_costs["add"]
                    result.append(Instruction("add", add_cost, 1))
                    cost += add_cost
                    n -= 1
                    pass
                pass
            pass

        result.reverse()
        if self.debug:
            print(f"binary method for {orig_n} = {bin2str(orig_n)} has cost {cost}")
        return (cost, result)

    def find_mult_sequence(self, n: int) -> Tuple[float, List[Instruction]]:
        """Top-level searching routine. Computes binary method upper bound
        and then does setup to the alpha-beta search
        """

        cache_lower, cache_upper, finished, cache_instr = self.cache_lookup(n)
        if finished:
            return cache_upper, cache_instr

        if cache_upper == maxsize:
            # The binary sequence gives a workable upper bound on the cost
            cache_upper, bin_instrs = self.binary_sequence(n)
            self.mult_cache[n] = (0, cache_upper, False, bin_instrs)

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

        cache_lower, cache_upper, finished, cache_instrs = self.cache_lookup(n)
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
                    self.mult_cache[n] = (upper, upper, True, instrs)
                else:
                    self.mult_cache[n] = (lower, maxsize, False, instrs)
                if self.debug:
                    print(f"**beta cutoff for {n} in cost {lower} > {upper}")
                return maxsize, []

            cache_lower, cache_upper, finished, cache_instrs = self.cache_lookup(m)
            if finished:
                upper = lower + cache_upper
                self.mult_cache[m] = (upper, upper, True, cache_instrs)
                return upper, cache_instrs + instrs
            pass

        # If no (incomplete) cached value found, use
        # the binary sequence which gives a workable upper bound on the cost.
        if cache_upper == maxsize:
            bin_cost, bin_instrs = self.binary_sequence_inner(m)

            # Cache the binary sequence portion result
            self.mult_cache[m] = (0, bin_cost, False, bin_instrs)

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
        glue_cost = self.op_costs["subtract"] + shift_cost
        try_lower = lower + glue_cost
        if try_lower < upper:
            try_cost, try_instrs = self.alpha_beta_search(m - 1, upper - try_lower)
            if try_cost + try_lower < upper:
                candidate_instrs = instrs + try_instrs
                candidate_instrs.append(Instruction("add", self.op_costs["add"], 1))
                upper = try_cost + try_lower

        # FIXME: Do the same for "add" as above

        candidate_cost = instruction_sequence_cost(candidate_instrs)
        if candidate_cost >= upper:
            # We have another cutoff
            if self.debug:
                print(f"**alpha cutoff for {n} in cost {candidate_cost} >= {upper}")
            self.mult_cache[n] = (
                upper,
                candidate_cost,
                upper == candidate_cost,
                candidate_instrs,
            )
            upper = candidate_cost
        else:
            self.mult_cache[n] = (upper, upper, True, candidate_instrs)
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

    for n in range(340, 344):
        min_cost, instrs = m.binary_sequence(n)
        cost, instrs = m.find_mult_sequence(n)
        print_instructions(instrs, n, cost)
        m.dump_mult_cache()
        # m.clear_mult_cache()

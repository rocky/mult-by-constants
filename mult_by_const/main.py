#!/usr/bin/env python
from typing import List, Tuple, Dict
from math import sqrt
from copy import deepcopy


def consecutive_zeros(n: int) -> Tuple[int, int]:
    shift_amount = 0
    while n % 2 == 0:
        shift_amount += 1
        n >>= 1
    return (shift_amount, n)


def consecutive_ones(n: int) -> Tuple[int, int]:
    one_run_count = 0
    while n % 2 == 1:
        one_run_count += 1
        n >>= 1
    return (one_run_count, n)


FACTOR_FLAG = -1


def default_shift_cost(num: int) -> int:
    # The default is to use a simple model where shifting by any amount is
    # done in a fixed amount of time which is the same as an add/subtract
    # operation.
    return 1


class Instruction:
    """Object contining information about a particular operation or instruction as it pertains
    to the instruction sequence"""

    def __init__(self, op: str, cost: int, amount: int):
        self.op = op  # The name of the operation; e.g. "shift", "add", "subtract"

        # "cost" is redundant and can be computed from the "op" and "amount";
        # we add it for convenience
        self.cost = cost

        # If "op" is a "shift", then it is amount to shift.
        # if "op" is an "add or subtract", then it is either 1 if we
        # add/subtract one, and FACTOR_FLAG if we add/subtract a factor value.
        self.amount = amount

    def __repr__(self):
        return f"op: {self.op}({self.amount}),\tcost: {self.cost}"


def print_operations(n: int, cost: int, instrs: List[Instruction]) -> None:
    print("-" * 45)
    print(f"Instruction sequence:")
    if n == 0:
        i = 0
        assert len(instrs) == 1
    else:
        i = 1
    j = 1
    cost = 0
    for instr in instrs:
        cost += instr.cost
        if instr.op == "shift":
            j = i
            i <<= instr.amount
            print(f"op: {instr.op}({instr.amount}),\tvalue: {i}, cost: {instr.cost}")
        elif instr.op == "add":
            if instr.amount == 1:
                i += 1
                print(f"op: {instr.op},\tvalue: {i}, cost: {instr.cost}")
            else:
                i += j
                print(f"op: {instr.op}*,\tvalue: {i}, cost: {instr.cost}")
        elif instr.op == "subtract":
            if instr.amount == 1:
                i -= 1
                print(f"op: {instr.op},\tvalue: {i}, cost: {instr.cost}")
            else:
                i -= j
                print(f"op: {instr.op}*,\tvalue: {i}, cost: {instr.cost}")
        elif instr.op == "constant 0":
            print(f"op: {instr.op},\tvalue: {i}, cost: {instr.cost}")
        elif instr.op == "noop":
            print(f"op: {instr.op},\tvalue: {i}, cost: {instr.cost}")
        else:
            print(f"unknown op {instr.op}")
            print(instr)
        pass

    print(f"Multiplier {n}, total cost: {cost}")
    print("=" * 45)
    assert n == i, f"Multiplier should be {n}, not computed value {i}"
    return


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
        # cost. Otherwise, a cutoff occurred and searching wasn't
        # complete. However, on subsquent searches, we can query the
        # lower bound and do another cutoff if the current-search
        # lower bound is not less than the previously-recorded lower
        # bound.

        # FIXME: give an examples here. Also attach names "alpha" and
        # and "beta" with the different types of cutoffs.
        self.mult_cache: Dict[int, Tuple[int, int, bool, List[Instruction]]] = {}

        # The following help with search statistics
        self.cache_hits_exact = 0
        self.cache_hits_partial = 0
        self.cache_misses = 0

        self.debug = debug

    def cache_lookup(self, n: int) -> Tuple[int, int, bool, List[Instruction]]:
        """Check if we have cached search results for "n", and return that.
        If not in cached, we will return (0, 0, {}). Note that a prior
        result has been fully only searched if if the lower bound is equal to the
        upper bound.
        """
        cache_result = self.mult_cache.get(n, (0, 0, False, []))
        if cache_result[2]:
            # Have some sort of match. Update hit status
            if cache_result[0] == cache_result[1]:
                self.cache_hits_exact += 1
            else:
                self.cache_hits_partial += 1
                pass
        else:
            self.cache_misses += 1
        return cache_result

    def make_odd(self, n: int, cost: int, result: List[Instruction]) -> Tuple[int, int]:
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
        lower: int,  # cost on instruction sequence used so far
        upper: int,  # cost of a valid instruction sequence
        result: List[Instruction],  # An instruction sequence with cost "upper"
    ) -> int:
        if (n % factor) == 0:
            glue_cost = self.op_costs[op] + self.shift_cost(shift_amount)
            new_lower = lower + glue_cost
            if new_lower < upper:
                m = n // factor
                if self.debug:
                    print(f"trying factor {factor}")
                try_cost = self.alpha_beta_search(m, upper, new_lower, result)
                if try_cost < upper:
                    result.append(
                        Instruction("shift", self.shift_cost(shift_amount), shift_amount)
                    )
                    result.append(Instruction(op, self.op_costs[op], FACTOR_FLAG))
                    upper = try_cost
                pass
            pass
        return upper

    def binary_sequence(self, n: int) -> Tuple[int, List[Instruction]]:
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

        result: List[Instruction] = []  # Sequence of operations
        return self.binary_sequence_inner(n, result)

    def binary_sequence_inner(
        self, n: int, result: List[Instruction]
    ) -> Tuple[int, List[Instruction]]:
        if self.debug:
            print("binary method for", bin(n)[2:])

        assert n > 0

        cost = 0  # total cost of sequence
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
        return (cost, result)

    def find_mult_sequence(self, n: int) -> Tuple[int, List[Instruction]]:
        """Top-level searching routine. Computes binary method upper bound
        and then does setup to the alpha-beta search
        """

        # The binary sequence gives a workable upper bound on the cost
        bin_cost, bin_instrs = self.binary_sequence(n)

        result: List[Instruction] = []  # Sequence of operations
        cost = self.alpha_beta_search(n, bin_cost, 0, bin_instrs)
        return cost, result

    def alpha_beta_search(
        self, n: int, upper: int, lower: int, result: List[Instruction]
    ) -> int:
        """Alpha-beta search

        n: is the (sub-)multiplier we are seeking at this point in the
           search.  Note that it is *not* the initial multiplier
           sought.

        upper: is the cost of the best sequence of instructions we've
               seen so far, and that is recorded in "results".  We get
               this value initially using the binary method, but it
               can be lowered as we find better sequences.

        lower: is the cost of the candidate instruction prefix
               sequence we've seen so far.  This prefix sequence is
               not the full sequence. The cost of further sequences
               get added to this cost to make the entire sequence
               complete. If it exceeds "upper", then this sequence is
               abandoned because there's some other sequence that is
               better.

        We return the lowest cost we can find using "n" in the sequence. Note that we
        don't return the cost of computing "n", but rather of the total sequence. If
        you subtract the "lower" value *on entry* than that is the cost of computing "n".
        """
        if self.debug:
            print(f"alph-beta search for {n}")

        cache_lower, cache_upper, finished, cache_instr = self.cache_lookup(n)
        if finished:
            result = cache_instr
            assert lower <= upper
            return upper

        n, shift_cost = self.make_odd(n, 0, result)
        lower += shift_cost
        search_result = deepcopy(result)

        # The binary sequence gives a workable lower bound on the cost
        bin_cost, bin_instrs = self.binary_sequence_inner(n, result)
        assert bin_cost > 0
        bin_cost += lower

        if bin_cost > upper:
            # Seen a better result preivously. Do a cutoff.
            return upper

        upper = bin_cost
        assert lower < upper  # since binary_seqence cost > 0 and was added to lower
        self.mult_cache[n] = (lower, upper, False, [])

        sqrt_n = int(sqrt(n))

        # The first factors, 3 = 2+1, and 5 = 4+1, are done special
        # and out of the "while" loop below, because we don't want to
        # consider subtraction factors 2-1 = 1, or 4-1 = 3.
        #
        # The latter, 3, is covered by 2+1 of the "for" loop below
        for factor in (3, 5):
            if factor > sqrt_n:
                break
            upper = self.try_shift_op_factor(
                n, factor, "add", 1, lower, upper, search_result
            )
            pass

        i, j = 3, 8
        while i < sqrt_n:
            upper = self.try_shift_op_factor(
                n, j + 1, "add", i, lower, upper, search_result
            )
            upper = self.try_shift_op_factor(
                n, j - 1, "subtract", i, lower, upper, search_result
            )

            # Any other factors to try?

            i += 1
            j <<= 1
            pass

        # Try subtracting one
        glue_cost = self.op_costs["subtract"] + self.shift_cost(i)
        new_lower = lower + glue_cost
        if new_lower < upper:
            try_cost = self.alpha_beta_search(n - 1, upper, new_lower, search_result)
            if try_cost < upper:
                # FIXME: Save the sequence
                upper = try_cost

        # glue_cost = self.cost["add"] + self.shift_cost(i)
        # new_lower = lower + glue_cost
        # if new_lower < upper:
        #     try_cost = self.alpha_beta_search(n+1, upper, new_lower, result)
        #     if try_cost < min_cost:
        #         # FIXME: Save the sequence
        #         min_cost = try_cost

        assert bin_cost >= upper

        if bin_cost == upper:
            result = bin_instrs
        else:
            result = search_result
            pass

        # upper is the exact cost, for the ENTIRE SEQUENCE in request that we could find in this pass.
        self.mult_cache[n] = (lower, upper, True, result)
        return upper

    pass


if __name__ == "__main__":
    m = MultConst()
    for n in list(range(2)) + [53, 93]:
        cost, result = m.binary_sequence(n)
        print_operations(n, cost, result)

    # result: List[Instruction] = []
    # min_cost = 6
    # n = 27
    # assert min_cost == m.try_shift_op_factor(
    #     n, 5, "add", 1, 0, min_cost, result
    # ), "4 is not a factor of 27, so we keep old min_cost"

    # result = []
    # cost = m.try_shift_op_factor(n, 3, "add", 1, 0, min_cost, result)
    # assert 4 == cost, f"Result should use the fact that 3 is a factor of {n}"
    # print_operations(n, cost, result)

    n = 341
    min_cost, result = m.binary_sequence(n)
    print_operations(n, min_cost, result)
    result = []
    cost = m.try_shift_op_factor(n, 31, "subtract", 5, 0, min_cost, result)
    print(cost)
    # assert 4 == cost, f"Result should use the fact that 7 is a factor of {n}"
    print_operations(n, cost, result)

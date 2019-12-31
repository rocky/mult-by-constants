"""Multiplication sequence searching methods.

All searching methods start with "search" have the same interface:

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

"""

from typing import List, Tuple
from mult_by_const.binary_method import binary_sequence_inner
from mult_by_const.cpu import inf_cost
from mult_by_const.instruction import (
    OP_R1,
    FACTOR_FLAG,
    REVERSE_SUBTRACT_FACTOR,
    REVERSE_SUBTRACT_1,
    Instruction,
    instruction_sequence_cost,
    instruction_sequence_value,
)
from mult_by_const.util import signum


def search_add_one(
    self,
    n: int,
    upper: float,  # maximum allowed cost for an instruction sequence.
    lower: float,  # cost of instructions seen so far, or inf_cost
    instrs: List[Instruction],  # We build on this
    candidate_instrs: List[
        Instruction
    ],  # If not empty, the best instruction sequence seen so for with cost "limit".
) -> Tuple[float, List[Instruction]]:
    inc = signum(n) * -1
    return self.try_plus_offset(n, inc, upper, lower, instrs, candidate_instrs, OP_R1)


def search_binary_method_with_cache(
    self,
    n: int,
    upper: float,
    lower: float,
    instrs: List[Instruction],
    candidate_instrs: List[Instruction],
) -> Tuple[float, List[Instruction]]:

    cache_lower, cache_upper, finished, cache_instrs = self.mult_cache[n]
    if finished:
        return cache_upper, cache_instrs

    cache_upper, cache_instrs = binary_sequence_inner(self, n)
    try_cost = cache_upper + instruction_sequence_cost(instrs)
    if try_cost < upper:
        self.debug_msg(
            f"Include cache value {n} in sequence; cost {try_cost} < {upper}."
        )
        if n == 1:
            candidate_instrs = instrs
        else:
            candidate_instrs = instrs + cache_instrs
        upper = try_cost
    return upper, candidate_instrs


def search_cache(
    self,
    n: int,
    limit: float,
    lower: float,
    instrs: List[Instruction],
    candidate_instrs: List[Instruction],
) -> Tuple[float, List[Instruction]]:
    """Is what we want already in the cache?"""

    cache_lower, cache_upper, finished, cache_instrs = self.mult_cache[n]
    try_limit = cache_upper + instruction_sequence_cost(instrs)
    if try_limit < limit:
        self.debug_msg(
            f"*include cache value {n} in sequence; search limit {try_limit} < {limit}."
        )
        candidate_instrs = cache_instrs
        limit = cache_upper
    return limit, candidate_instrs


def search_add_or_subtract_one(
    self,
    n: int,
    upper: float,
    lower: float,
    instrs: List[Instruction],
    candidate_instrs: List[Instruction],
) -> Tuple[float, List[Instruction]]:

    # To improve searching and make use of the cache better search towards zero before
    # searching away from zero.
    if abs(n) == 1:
        cache_lower, cache_upper, finished, cache_instrs = self.mult_cache[n]
    elif n > 0:
        upper, candidate_instrs = search_subtract_one(
            self, n, upper, lower, instrs, candidate_instrs
        )
        upper, candidate_instrs = search_add_one(
            self, n, upper, lower, instrs, candidate_instrs
        )
    else:
        # We search on  "negate" first since that will succeed and give a close bound (within an instruction
        # of the optimal) to speed searching. The searches below this when they work will be better.
        # but we just don't know if they will succeed at all. Overall in alpha-beta searching it is useful
        # to start out with something that will always work so that we can set a reasonable bound on searching.
        upper, candidate_instrs = search_negate(
            self, n, upper, lower, instrs, candidate_instrs
        )
        upper, candidate_instrs = search_add_one(
            self, n, upper, lower, instrs, candidate_instrs
        )
        upper, candidate_instrs = search_subtract_one(
            self, n, upper, lower, instrs, candidate_instrs
        )
    return upper, candidate_instrs


def search_negate(
    self,
    n: int,
    upper: float,
    lower: float,
    instrs: List[Instruction],
    candidate_instrs: List[Instruction],
) -> Tuple[float, List[Instruction]]:

    if n < 0 and self.cpu_model.can_negate():
        if self.debug:
            self.debug_msg(f"Looking at cached positive value {-n} of {n}")

        negate_cost = self.op_costs["negate"]
        lower += negate_cost
        if lower >= upper:
            # We have another cutoff
            if self.debug:
                self.debug_msg(
                    f"**alpha cutoff in negate for {n} in cost {lower} >= {upper}"
                )
                return upper, candidate_instrs

        cache_lower, cache_upper, finished, instrs = self.mult_cache[-n]
        if cache_upper == inf_cost:
            cache_upper, instrs = binary_sequence_inner(self, -n)

        cache_upper += negate_cost
        if cache_upper < upper:
            if self.debug:
                self.debug_msg(f"Negation {n} update {cache_upper} < {upper} ...")
            instrs.append(Instruction("negate", 0, negate_cost))
            return cache_upper, instrs
    return upper, candidate_instrs


def search_negate_subtract_one(
    self,
    n: int,
    upper: float,
    lower: float,
    instrs: List[Instruction],
    candidate_instrs: List[Instruction],
) -> Tuple[float, List[Instruction]]:

    cache_lower, cache_upper, finished, cache_instrs = self.mult_cache[n]
    if finished:
        return cache_upper, cache_instrs if n != 1 else []
    if n > 1:
        # Negative numbers never take less then their positive counterpart,
        # so there is no benefit in reversing a subtraction here.
        return upper, candidate_instrs

    # FIXME: for some reason for -12345678 we get the wrong value 15
    # (under default cost model) when we combine the < 0 test below as part of the "if"
    # above. Investigate.
    op_flag = OP_R1 if instruction_sequence_value(candidate_instrs) < 0 else REVERSE_SUBTRACT_1
    return self.try_plus_offset(
        -n, +1, upper + self.eps, lower, instrs, candidate_instrs, op_flag
    )


def search_short_add_factors(
    self,
    n: int,
    upper: float,
    lower: float,
    instrs: List[Instruction],
    candidate_instrs: List[Instruction],
) -> Tuple[float, List[Instruction]]:

    i, j = 1, 2
    while j - 1 <= n:
        upper, candidate_instrs = self.try_shift_op_factor(
            n, j + 1, "add", i, upper, lower, instrs, candidate_instrs
        )

        # Any other factors to try?

        i += 1
        j <<= 1
        pass

    return upper, candidate_instrs

# FIXME: try with above
def search_short_factors(
    self,
    n: int,
    upper: float,
    lower: float,
    instrs: List[Instruction],
    candidate_instrs: List[Instruction],
) -> Tuple[float, List[Instruction]]:

    abs_n = abs(n)
    # The first factors, 3 = 2+1, and 5 = 4+1, are done special
    # and out of the "while" loop below, because we don't want to
    # consider subtraction factors 2-1 = 1, or 4-1 = 3.
    #
    # The latter, 3, is covered by 2+1 of the "for" loop below

    for factor, shift_amount in ((3, 1), (5, 2)):
        if factor > abs_n:
            break
        upper, candidate_instrs = self.try_shift_op_factor(
            n, factor, "add", shift_amount, upper, lower, instrs, candidate_instrs
        )
        pass

    i, j = 3, 8
    while j - 1 <= abs_n:
        if n < 0:
            # We'll increase upper, to allow equal ties to succeed with subtraction since
            # that's what we want when we have a negative number.
            try_cost, try_instrs = self.try_shift_op_factor(
                -n, j - 1, "subtract", i, upper + self.eps, lower, instrs, candidate_instrs
            )
            if try_cost < upper and try_instrs and try_instrs[-1].op == "subtract":
                self.debug_msg(
                    f"*update {n} using factor {j - 1}; cost {try_cost} < previous limit {upper}"
                )
                self.mult_cache.update_field(
                        n, upper=try_cost, instrs=try_instrs
                    )
                assert try_instrs[-1].amount == FACTOR_FLAG
                try_instrs[-1].amount = REVERSE_SUBTRACT_FACTOR
                candidate_instrs = try_instrs
                upper = try_cost

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


# FIXME add cache lookup as a decorator
def search_subtract_one(
    self,
    n: int,
    upper: float,  # maximum allowed cost for an instruction sequence.
    lower: float,  # cost of instructions seen so far, or inf_cost
    instrs: List[Instruction],  # We build on this
    candidate_instrs: List[Instruction],
) -> Tuple[float, List[Instruction]]:
    inc = signum(n) * 1
    return self.try_plus_offset(n, inc, upper, lower, instrs, candidate_instrs, OP_R1)

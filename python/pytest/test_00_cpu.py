"""
Test of cpu/cost
"""
import mult_by_const.cpu as cpu
import os


def test_cpu_profiles():
    for cpu_profile, can_negate, subtract_can_negate, shift1_cost, shift2_cost, in (
        (cpu.POWER_3addr_3reg, True, True, 1, 1),
        (cpu.chained_adds, False, False, 1, 2),
    ):
        assert cpu_profile.can_negate() == can_negate
        assert cpu_profile.subtract_can_negate() == subtract_can_negate
        assert cpu_profile.shift_cost_fn(1) == shift1_cost
        assert cpu_profile.shift_cost_fn(2) == shift2_cost


# If run as standalone
if __name__ == "__main__":
    test_cpu_profiles()

"""
Test of cpu/cost
"""
import mult_by_const.cpu as cpu
import os


def test_cpu_profiles():
    for cpu_profile, can_negate, subtract_can_negate in (
        (cpu.POWER_3addr_3reg, True, True),
        (cpu.chained_adds, False, False),
    ):
        assert cpu_profile.can_negate() == can_negate
        assert cpu_profile.subtract_can_negate() == subtract_can_negate


# If run as standalone
if __name__ == "__main__":
    test_cpu_profiles()

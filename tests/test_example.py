"""test_example.py — Starter template for PlatformIO / embedded C tests.

C/C++ source files cannot be imported in Python. Instead:
1. Read .c/.cpp/.h files to understand the algorithms
2. Re-implement the core logic in Python
3. Test with pytest

DO NOT modify conftest.py.
"""
import pytest

# Arduino utility functions (re-implemented for testing)
def arduino_map(value, from_low, from_high, to_low, to_high):
    """Arduino map function - maps a value from one range to another."""
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low

def arduino_constrain(value, min_val, max_val):
    """Arduino constrain function - constrains a value between min and max."""
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value


def test_value_mapping():
    """Test that value mapping works correctly."""
    result = arduino_map(512, 0, 1023, 0, 100)
    assert abs(result - 50.0) < 0.1


def test_arduino_constrain_basic():
    """Test basic constrain functionality."""
    assert arduino_constrain(50, 0, 100) == 50
    assert arduino_constrain(-10, 0, 100) == 0
    assert arduino_constrain(150, 0, 100) == 100


# TODO: Read source files and re-implement algorithms to test here

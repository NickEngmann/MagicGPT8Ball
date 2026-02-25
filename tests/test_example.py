"""test_example.py — Starter template for PlatformIO / embedded C tests.

C/C++ source files cannot be imported in Python. Instead:
1. Read .c/.cpp/.h files to understand the algorithms
2. Re-implement the core logic in Python
3. Test with pytest

DO NOT modify conftest.py.
"""
import pytest


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Arduino map function implementation."""
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def arduino_constrain(x, a, b):
    """Arduino constrain function implementation."""
    if x < a:
        return a
    elif x > b:
        return b
    return x


def test_value_mapping():
    """Test that value mapping works correctly."""
    assert arduino_map(512, 0, 1023, 0, 100) == 50


def test_constrain_function():
    """Test the constrain function."""
    assert arduino_constrain(50, 0, 100) == 50
    assert arduino_constrain(-10, 0, 100) == 0
    assert arduino_constrain(150, 0, 100) == 100


# TODO: Read source files and re-implement algorithms to test here

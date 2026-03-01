"""test_example.py — Starter template for PlatformIO / embedded C tests.

C/C++ source files cannot be imported in Python. Instead:
1. Read .c/.cpp/.h files to understand the algorithms
2. Re-implement the core logic in Python
3. Test with pytest

See embedded_mocks.py for I2C/SPI/UART/GPIO mocks.
DO NOT modify conftest.py.
"""
import pytest
from embedded_mocks import arduino_map, arduino_constrain, MockUART


def test_value_mapping():
    """Test that value mapping works correctly."""
    assert arduino_map(512, 0, 1023, 0, 100) == 50


# TODO: Read source files and re-implement algorithms to test here

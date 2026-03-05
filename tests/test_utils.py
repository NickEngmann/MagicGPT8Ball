"""Tests for utility functions (Arduino mappings)."""
import sys
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch

# Mock Arduino dependencies
sys.modules['Arduino'] = MagicMock()
sys.modules['Arduino.h'] = MagicMock()


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


def analog_to_voltage(analog_value, reference_voltage=3.3, adc_bits=12):
    """Convert analog reading to voltage."""
    max_value = 2 ** adc_bits - 1
    return (analog_value / max_value) * reference_voltage


def test_arduino_map_basic():
    """Test basic mapping from 0-1023 to 0-100."""
    result = arduino_map(512, 0, 1023, 0, 100)
    assert abs(result - 50.0) < 0.1


def test_arduino_map_exact_range():
    """Test mapping exact range boundaries."""
    result_low = arduino_map(0, 0, 1023, 0, 100)
    result_high = arduino_map(1023, 0, 1023, 0, 100)
    
    assert result_low == 0.0
    assert result_high == 100.0


def test_arduino_map_negative_range():
    """Test mapping to negative range."""
    result = arduino_map(512, 0, 1023, -100, 100)
    assert abs(result - 0.0) < 0.1


def test_arduino_map_same_range():
    """Test mapping same range (should return same value)."""
    result = arduino_map(50, 0, 100, 0, 100)
    assert result == 50.0


def test_arduino_map_out_of_range_low():
    """Test mapping value below range."""
    result = arduino_map(-100, 0, 1023, 0, 100)
    assert result < 0


def test_arduino_map_out_of_range_high():
    """Test mapping value above range."""
    result = arduino_map(2000, 0, 1023, 0, 100)
    assert result > 100


def test_arduino_map_float_input():
    """Test mapping with float input."""
    result = arduino_map(512.5, 0, 1023, 0, 100)
    assert abs(result - 50.049) < 0.1


def test_arduino_constrain_basic():
    """Test basic constraining."""
    result = arduino_constrain(50, 0, 100)
    assert result == 50


def test_arduino_constrain_below_min():
    """Test constraining value below minimum."""
    result = arduino_constrain(-10, 0, 100)
    assert result == 0


def test_arduino_constrain_above_max():
    """Test constraining value above maximum."""
    result = arduino_constrain(150, 0, 100)
    assert result == 100


def test_arduino_constrain_at_boundaries():
    """Test constraining at exact boundaries."""
    result_min = arduino_constrain(0, 0, 100)
    result_max = arduino_constrain(100, 0, 100)
    
    assert result_min == 0
    assert result_max == 100


def test_arduino_constrain_negative_range():
    """Test constraining with negative range."""
    result = arduino_constrain(-50, -100, 0)
    assert result == -50


def test_arduino_constrain_equal_min_max():
    """Test constraining when min equals max."""
    result = arduino_constrain(50, 100, 100)
    assert result == 100


def test_analog_to_voltage_3v3_12bit():
    """Test analog to voltage conversion with 3.3V reference and 12-bit ADC."""
    result = analog_to_voltage(2048, 3.3, 12)
    expected = (2048 / 4095) * 3.3
    assert abs(result - expected) < 0.01


def test_analog_to_voltage_full_scale():
    """Test analog to voltage at full scale."""
    result = analog_to_voltage(4095, 3.3, 12)
    expected = 3.3
    assert abs(result - expected) < 0.01


def test_analog_to_voltage_zero():
    """Test analog to voltage at zero."""
    result = analog_to_voltage(0, 3.3, 12)
    assert result == 0.0


def test_analog_to_voltage_5v_reference():
    """Test analog to voltage with 5V reference."""
    result = analog_to_voltage(2048, 5.0, 12)
    expected = (2048 / 4095) * 5.0
    assert abs(result - expected) < 0.01


def test_analog_to_voltage_10bit():
    """Test analog to voltage with 10-bit ADC."""
    result = analog_to_voltage(512, 3.3, 10)
    expected = (512 / 1023) * 3.3
    assert abs(result - expected) < 0.01


def test_arduino_map_round_trip():
    """Test that mapping and inverse mapping returns original value."""
    # Map from 0-1023 to 0-100
    mapped = arduino_map(750, 0, 1023, 0, 100)
    # Map back from 0-100 to 0-1023
    original = arduino_map(mapped, 0, 100, 0, 1023)
    
    assert abs(original - 750) < 1.0


def test_arduino_constrain_preserves_value():
    """Test that constrain preserves value within range."""
    test_values = [10, 50, 90, 0, 100, -10, 110]
    for val in test_values:
        constrained = arduino_constrain(val, 0, 100)
        if 0 <= val <= 100:
            assert constrained == val
        elif val < 0:
            assert constrained == 0
        else:
            assert constrained == 100


def test_analog_to_voltage_precision():
    """Test analog to voltage precision."""
    # Test various analog values
    test_cases = [
        (0, 0.0),
        (1024, 0.84),
        (2048, 1.68),
        (3072, 2.51),
        (4095, 3.3)
    ]
    
    for analog_val, expected_voltage in test_cases:
        result = analog_to_voltage(analog_val, 3.3, 12)
        assert abs(result - expected_voltage) < 0.1


def test_arduino_map_integer_result():
    """Test that arduino_map can produce integer results."""
    result = arduino_map(512, 0, 1023, 0, 100)
    # 512/1023 * 100 ≈ 50
    assert 49 <= result <= 51
    assert isinstance(result, float)


def test_arduino_constrain_float():
    """Test constrain with float values."""
    result = arduino_constrain(50.5, 0.0, 100.0)
    assert result == 50.5


def test_arduino_map_negative_input():
    """Test map with negative input value."""
    result = arduino_map(-100, 0, 1023, 0, 100)
    assert result < 0


def test_arduino_map_negative_output_range():
    """Test map with negative output range."""
    result = arduino_map(512, 0, 1023, -50, 50)
    assert abs(result) < 1


def test_analog_to_voltage_14bit():
    """Test analog to voltage with 14-bit ADC (ESP32)."""
    result = analog_to_voltage(8192, 3.3, 14)
    expected = (8192 / 16383) * 3.3
    assert abs(result - expected) < 0.01


def test_arduino_map_large_range():
    """Test map with large range values."""
    result = arduino_map(50000, 0, 100000, 0, 1000)
    assert result == 500.0


def test_arduino_constrain_large_values():
    """Test constrain with large values."""
    result = arduino_constrain(1000000, 0, 100000)
    assert result == 100000


def test_arduino_map_reverse():
    """Test mapping in reverse direction."""
    result = arduino_map(50, 100, 0, 0, 100)
    # 50 is midpoint of 100-0, maps to midpoint of 0-100 which is 50
    assert abs(result - 50.0) < 0.1


def test_arduino_constrain_negative_values():
    """Test constrain with negative values."""
    result = arduino_constrain(-50, -100, 0)
    assert result == -50

    result = arduino_constrain(-150, -100, 0)
    assert result == -100

    result = arduino_constrain(50, -100, 0)
    assert result == 0

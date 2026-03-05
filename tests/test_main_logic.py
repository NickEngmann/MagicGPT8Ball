"""test_main_logic.py — Tests for main.cpp logic."""
import pytest
from embedded_mocks import arduino_map, arduino_constrain


class TestValueMapping:
    """Test value mapping functions."""
    
    def test_arduino_map_basic(self):
        """Test basic Arduino map function."""
        assert arduino_map(512, 0, 1023, 0, 100) == 50
    
    def test_arduino_map_edge_cases(self):
        """Test edge cases for Arduino map."""
        assert arduino_map(0, 0, 1023, 0, 100) == 0
        assert arduino_map(1023, 0, 1023, 0, 100) == 100
    
    def test_arduino_map_negative(self):
        """Test mapping with negative values."""
        assert arduino_map(50, -100, 100, -10, 10) == 5


class TestValueConstrain:
    """Test value constrain function."""
    
    def test_arduino_constrain_basic(self):
        """Test basic Arduino constrain function."""
        assert arduino_constrain(50, 0, 100) == 50
    
    def test_arduino_constrain_below(self):
        """Test constrain when value is below minimum."""
        assert arduino_constrain(-10, 0, 100) == 0
    
    def test_arduino_constrain_above(self):
        """Test constrain when value is above maximum."""
        assert arduino_constrain(150, 0, 100) == 100
    
    def test_arduino_constrain_equal(self):
        """Test constrain when value equals boundary."""
        assert arduino_constrain(0, 0, 100) == 0
        assert arduino_constrain(100, 0, 100) == 100

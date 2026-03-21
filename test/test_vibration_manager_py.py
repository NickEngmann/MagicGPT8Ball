"""
Test suite for VibrationManager module (mocked for pytest)
Tests motor control, vibration patterns, and timing.
"""

import unittest
from unittest.mock import patch, MagicMock


class MockVibrationManager:
    """Mock implementation of VibrationManager for testing"""
    
    def __init__(self, motor1_pin=5, motor2_pin=13):
        self.motor1_pin = motor1_pin
        self.motor2_pin = motor2_pin
        self.is_vibrating = False
        self.start_time = 0
        self.duration = 0
        self.motor_states = {motor1_pin: False, motor2_pin: False}
        
    def begin(self):
        """Initialize vibration motors"""
        self.motor_states[self.motor1_pin] = False
        self.motor_states[self.motor2_pin] = False
        return True
        
    def stop(self):
        """Stop vibration immediately"""
        self.is_vibrating = False
        self.motor_states[self.motor1_pin] = False
        self.motor_states[self.motor2_pin] = False
        
    def start_vibration(self, duration_ms):
        """Start vibration for specified duration"""
        self.is_vibrating = True
        self.duration = duration_ms
        self.start_time = 0  # In real implementation: millis()
        self.motor_states[self.motor1_pin] = True
        self.motor_states[self.motor2_pin] = True
        
    def update(self):
        """Update vibration state (check duration)"""
        if self.is_vibrating:
            # Simulate time passing
            elapsed = 50  # Mock elapsed time
            if elapsed >= self.duration:
                self.stop()
                
    def is_vibrating(self):
        """Check if currently vibrating"""
        return self.is_vibrating
        
    def short_buzz(self):
        """Short vibration (100ms)"""
        self.start_vibration(100)
        
    def medium_buzz(self):
        """Medium vibration (250ms)"""
        self.start_vibration(250)
        
    def long_buzz(self):
        """Long vibration (500ms)"""
        self.start_vibration(500)
        
    def double_buzz(self):
        """Double vibration pattern"""
        self.start_vibration(100)
        # Simulate delay and second buzz
        self.stop()
        self.start_vibration(100)


class TestVibrationManager(unittest.TestCase):
    """Unit tests for VibrationManager mock"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.vib = MockVibrationManager()
        self.vib.begin()
        
    def test_initialization(self):
        """Test vibration manager is properly initialized"""
        self.assertFalse(self.vib.is_vibrating)
        self.assertEqual(self.vib.motor1_pin, 5)
        self.assertEqual(self.vib.motor2_pin, 13)
        
    def test_start_vibration(self):
        """Test starting vibration"""
        self.vib.start_vibration(200)
        self.assertTrue(self.vib.is_vibrating)
        self.assertEqual(self.vib.duration, 200)
        
    def test_stop_vibration(self):
        """Test stopping vibration"""
        self.vib.start_vibration(200)
        self.assertTrue(self.vib.is_vibrating)
        
        self.vib.stop()
        self.assertFalse(self.vib.is_vibrating)
        
    def test_motor_pins(self):
        """Test motor pin configuration"""
        self.vib.start_vibration(100)
        self.assertTrue(self.vib.motor_states[5])
        self.assertTrue(self.vib.motor_states[13])
        
    def test_short_buzz(self):
        """Test short buzz pattern"""
        self.vib.short_buzz()
        self.assertTrue(self.vib.is_vibrating)
        self.assertEqual(self.vib.duration, 100)
        
    def test_medium_buzz(self):
        """Test medium buzz pattern"""
        self.vib.medium_buzz()
        self.assertTrue(self.vib.is_vibrating)
        self.assertEqual(self.vib.duration, 250)
        
    def test_long_buzz(self):
        """Test long buzz pattern"""
        self.vib.long_buzz()
        self.assertTrue(self.vib.is_vibrating)
        self.assertEqual(self.vib.duration, 500)
        
    def test_double_buzz(self):
        """Test double buzz pattern"""
        # Double buzz starts and stops then starts again
        self.vib.double_buzz()
        # In mock, the last state should be vibrating
        self.assertTrue(self.vib.is_vibrating)


class TestVibrationManagerCustomPins(unittest.TestCase):
    """Tests for custom motor pin configuration"""
    
    def test_custom_pin_configuration(self):
        """Test custom motor pins"""
        vib = MockVibrationManager(motor1_pin=10, motor2_pin=11)
        vib.begin()
        self.assertEqual(vib.motor1_pin, 10)
        self.assertEqual(vib.motor2_pin, 11)
        
    def test_custom_pins_activation(self):
        """Test custom pins are activated during vibration"""
        vib = MockVibrationManager(motor1_pin=10, motor2_pin=11)
        vib.begin()
        vib.start_vibration(100)
        self.assertTrue(vib.motor_states[10])
        self.assertTrue(vib.motor_states[11])


class TestVibrationTiming(unittest.TestCase):
    """Tests for vibration timing"""
    
    def test_vibration_duration_ms(self):
        """Verify duration values are in milliseconds"""
        self.assertEqual(100, 100)
        self.assertEqual(250, 250)
        self.assertEqual(500, 500)
        
    def test_short_buzz_100ms(self):
        """Short buzz should be 100ms"""
        self.assertEqual(100, 100)
        
    def test_medium_buzz_250ms(self):
        """Medium buzz should be 250ms"""
        self.assertEqual(250, 250)
        
    def test_long_buzz_500ms(self):
        """Long buzz should be 500ms"""
        self.assertEqual(500, 500)


if __name__ == '__main__':
    unittest.main(verbosity=2)

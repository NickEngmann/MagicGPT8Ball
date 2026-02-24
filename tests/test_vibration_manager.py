"""Test VibrationManager class algorithms."""
import sys
import os
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch
import pytest

# Mock Arduino environment
sys.modules['Arduino'] = MagicMock()
sys.modules['WiFiManager'] = MagicMock()
sys.modules['WiFi'] = MagicMock()
sys.modules['HTTPClient'] = MagicMock()
sys.modules['QMI8658'] = MagicMock()
sys.modules['DEV_Config'] = MagicMock()
sys.modules['Recorder'] = MagicMock()
sys.modules['Animations'] = MagicMock()


class MockDigitalWrite:
    def __init__(self):
        self.pins = {}
    
    def __call__(self, pin, value):
        self.pins[pin] = value
    
    def get_pin(self, pin):
        return self.pins.get(pin, 0)


class MockMillis:
    def __init__(self):
        self._time = 0
    
    def __call__(self):
        return self._time
    
    def advance(self, ms):
        self._time += ms


def test_vibration_manager_initial_state():
    """Test that vibration manager starts with motors off."""
    from src.VibrationManager import VibrationManager
    
    mock_digital_write = MockDigitalWrite()
    mock_millis = MockMillis()
    
    with patch('digitalWrite', mock_digital_write):
        with patch('millis', mock_millis):
            with patch('pinMode'):
                manager = VibrationManager(5, 13)
                manager.begin()
                
                assert not manager.isVibrating()
                assert mock_digital_write.get_pin(5) == 0
                assert mock_digital_write.get_pin(13) == 0


def test_vibration_manager_start_stop():
    """Test starting and stopping vibration."""
    from src.VibrationManager import VibrationManager
    
    mock_digital_write = MockDigitalWrite()
    mock_millis = MockMillis()
    
    with patch('digitalWrite', mock_digital_write):
        with patch('millis', mock_millis):
            with patch('pinMode'):
                manager = VibrationManager(5, 13)
                manager.begin()
                
                manager.startVibration(1000)
                assert manager.isVibrating()
                assert mock_digital_write.get_pin(5) == 1
                assert mock_digital_write.get_pin(13) == 1
                
                manager.stop()
                assert not manager.isVibrating()
                assert mock_digital_write.get_pin(5) == 0
                assert mock_digital_write.get_pin(13) == 0


def test_vibration_manager_auto_stop():
    """Test that vibration stops automatically after duration."""
    from src.VibrationManager import VibrationManager
    
    mock_digital_write = MockDigitalWrite()
    mock_millis = MockMillis()
    
    with patch('digitalWrite', mock_digital_write):
        with patch('millis', mock_millis):
            with patch('pinMode'):
                manager = VibrationManager(5, 13)
                manager.begin()
                
                manager.startVibration(500)
                assert manager.isVibrating()
                
                mock_millis.advance(499)
                manager.update()
                assert manager.isVibrating()
                
                mock_millis.advance(1)
                manager.update()
                assert not manager.isVibrating()
                assert mock_digital_write.get_pin(5) == 0
                assert mock_digital_write.get_pin(13) == 0


def test_vibration_manager_patterns():
    """Test predefined vibration patterns."""
    from src.VibrationManager import VibrationManager
    
    mock_digital_write = MockDigitalWrite()
    mock_millis = MockMillis()
    
    with patch('digitalWrite', mock_digital_write):
        with patch('millis', mock_millis):
            with patch('pinMode'):
                manager = VibrationManager(5, 13)
                manager.begin()
                
                # Test short buzz
                manager.shortBuzz()
                assert manager.isVibrating()
                
                # Test medium buzz
                manager.mediumBuzz()
                assert manager.isVibrating()
                
                # Test long buzz
                manager.longBuzz()
                assert manager.isVibrating()

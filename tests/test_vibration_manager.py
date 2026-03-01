"""Tests for VibrationManager class - Python implementation."""
import sys
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch
import pytest


class MockDigitalWrite:
    """Mock digitalWrite function."""
    def __init__(self):
        self.pins = {}
        self.calls = []
    
    def __call__(self, pin, val):
        self.calls.append((pin, val))
        if pin not in self.pins:
            self.pins[pin] = 0
        self.pins[pin] = val
    
    def get_pin_value(self, pin):
        return self.pins.get(pin, 0)


class MockMillis:
    """Mock millis() function."""
    def __init__(self):
        self._time = 0
    
    def __call__(self):
        return self._time
    
    def increment(self, ms):
        self._time += ms


class MockPinMode:
    """Mock pinMode function."""
    def __init__(self):
        self.calls = []
    
    def __call__(self, pin, mode):
        self.calls.append((pin, mode))


class VibrationManager:
    """Python implementation of VibrationManager for testing."""
    def __init__(self, motor1Pin=5, motor2Pin=13):
        self._motor1Pin = motor1Pin
        self._motor2Pin = motor2Pin
        self._isVibrating = False
        self._startTime = 0
        self._duration = 0
        self.digitalWrite = MagicMock()
        self.pinMode = MagicMock()
        self.millis = MockMillis()
    
    def begin(self):
        self.pinMode(self._motor1Pin, 1)  # OUTPUT
        self.pinMode(self._motor2Pin, 1)  # OUTPUT
        self.stop()
    
    def startVibration(self, duration):
        self._isVibrating = True
        self._startTime = self.millis()
        self._duration = duration
        self.digitalWrite(self._motor1Pin, 1)  # HIGH
        self.digitalWrite(self._motor2Pin, 1)  # HIGH
    
    def stop(self):
        self._isVibrating = False
        self.digitalWrite(self._motor1Pin, 0)  # LOW
        self.digitalWrite(self._motor2Pin, 0)  # LOW
    
    def update(self):
        if self._isVibrating and (self.millis() - self._startTime >= self._duration):
            self.stop()
    
    def shortBuzz(self):
        self.startVibration(100)
    
    def mediumBuzz(self):
        self.startVibration(250)
    
    def longBuzz(self):
        self.startVibration(500)
    
    def doubleBuzz(self):
        self.startVibration(100)
        self.millis.increment(100)
        self.startVibration(100)
    
    def isVibrating(self):
        return self._isVibrating


@pytest.fixture
def vib_manager():
    """Create a VibrationManager instance with mocks."""
    return VibrationManager(5, 13)


def test_vibration_manager_initial_state(vib_manager):
    """Test that vibration manager starts with motors off."""
    assert not vib_manager.isVibrating()


def test_vibration_manager_begin(vib_manager):
    """Test begin() initializes pins correctly."""
    vib_manager.begin()
    
    # Check pinMode was called for both pins
    assert vib_manager.pinMode.call_count == 2
    vib_manager.pinMode.assert_any_call(5, 1)  # OUTPUT
    vib_manager.pinMode.assert_any_call(13, 1)  # OUTPUT


def test_vibration_manager_start_stop(vib_manager):
    """Test startVibration and stop methods."""
    vib_manager.startVibration(500)
    assert vib_manager.isVibrating()
    
    vib_manager.stop()
    assert not vib_manager.isVibrating()


def test_vibration_manager_update_stops(vib_manager):
    """Test update() stops vibration after duration."""
    vib_manager.startVibration(500)
    assert vib_manager.isVibrating()
    
    # Advance time past duration
    vib_manager.millis.increment(600)
    vib_manager.update()
    assert not vib_manager.isVibrating()


def test_vibration_manager_predefined_patterns(vib_manager):
    """Test predefined vibration patterns."""
    # Test short buzz (100ms)
    vib_manager.shortBuzz()
    assert vib_manager.isVibrating()
    
    vib_manager.millis.increment(200)
    vib_manager.update()
    assert not vib_manager.isVibrating()
    
    # Test medium buzz (250ms)
    vib_manager.mediumBuzz()
    assert vib_manager.isVibrating()
    
    vib_manager.millis.increment(300)
    vib_manager.update()
    assert not vib_manager.isVibrating()
    
    # Test long buzz (500ms)
    vib_manager.longBuzz()
    assert vib_manager.isVibrating()
    
    vib_manager.millis.increment(600)
    vib_manager.update()
    assert not vib_manager.isVibrating()


def test_vibration_manager_double_buzz(vib_manager):
    """Test double buzz pattern."""
    vib_manager.doubleBuzz()
    assert vib_manager.isVibrating()
    
    # First buzz should complete
    vib_manager.millis.increment(200)
    vib_manager.update()
    # Should still be vibrating (second buzz)
    assert vib_manager.isVibrating()
    
    # Second buzz should complete
    vib_manager.millis.increment(200)
    vib_manager.update()
    assert not vib_manager.isVibrating()


def test_vibration_manager_digital_write_calls(vib_manager):
    """Test that digitalWrite is called correctly."""
    vib_manager.begin()
    vib_manager.startVibration(100)
    
    # Check digitalWrite was called with HIGH for both pins
    assert vib_manager.digitalWrite.call_count == 2
    vib_manager.digitalWrite.assert_any_call(5, 1)  # HIGH
    vib_manager.digitalWrite.assert_any_call(13, 1)  # HIGH
    
    vib_manager.stop()
    # Check digitalWrite was called with LOW for both pins
    assert vib_manager.digitalWrite.call_count == 4
    vib_manager.digitalWrite.assert_any_call(5, 0)  # LOW
    vib_manager.digitalWrite.assert_any_call(13, 0)  # LOW

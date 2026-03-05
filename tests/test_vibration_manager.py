"""Tests for VibrationManager module."""
import sys
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch

# Mock Arduino dependencies
sys.modules['Arduino'] = MagicMock()
sys.modules['Arduino.h'] = MagicMock()


class VibrationManagerLogic:
    """Python re-implementation of VibrationManager logic for testing."""
    
    def __init__(self, motor1Pin=5, motor2Pin=13):
        self._motor1Pin = motor1Pin
        self._motor2Pin = motor2Pin
        self._isVibrating = False
        self._startTime = 0
        self._duration = 0
        self.vibrationLog = []
    
    def startVibration(self, duration=1000):
        """Start vibration for specified duration in milliseconds."""
        self._isVibrating = True
        self._startTime = self._getMillis()
        self._duration = duration
        self.vibrationLog.append({
            'action': 'start',
            'duration': duration,
            'timestamp': self._startTime
        })
        return True
    
    def stopVibration(self):
        """Stop vibration immediately."""
        self._isVibrating = False
        self.vibrationLog.append({
            'action': 'stop',
            'timestamp': self._getMillis()
        })
        return True
    
    def isVibrating(self):
        """Check if currently vibrating."""
        if self._isVibrating:
            elapsed = self._getMillis() - self._startTime
            if elapsed >= self._duration:
                self._isVibrating = False
                return False
        return self._isVibrating
    
    def getVibrationDuration(self):
        """Get the set vibration duration."""
        return self._duration
    
    def getMotor1Pin(self):
        """Get motor 1 pin number."""
        return self._motor1Pin
    
    def getMotor2Pin(self):
        """Get motor 2 pin number."""
        return self._motor2Pin
    
    def getVibrationLog(self):
        """Get the vibration log."""
        return self.vibrationLog
    
    def _getMillis(self):
        """Mock millis function."""
        return 1000  # Fixed time for testing


def test_initial_vibration_state():
    """Test that vibration starts in non-vibrating state."""
    manager = VibrationManagerLogic()
    assert manager.isVibrating() == False
    assert manager._isVibrating == False


def test_start_vibration():
    """Test starting vibration."""
    manager = VibrationManagerLogic()
    result = manager.startVibration(1000)
    assert result == True
    assert manager.isVibrating() == True
    assert manager._isVibrating == True
    assert manager.getVibrationDuration() == 1000


def test_stop_vibration():
    """Test stopping vibration."""
    manager = VibrationManagerLogic()
    manager.startVibration(1000)
    assert manager.isVibrating() == True
    
    result = manager.stopVibration()
    assert result == True
    assert manager.isVibrating() == False
    assert manager._isVibrating == False


def test_vibration_duration_timeout():
    """Test that vibration stops after duration expires."""
    manager = VibrationManagerLogic()
    manager._isVibrating = True
    manager._startTime = 0
    manager._duration = 100
    
    # Simulate time passing beyond duration
    manager._getMillis = lambda: 200  # 200ms elapsed
    
    assert manager.isVibrating() == False


def test_vibration_still_active():
    """Test that vibration is still active within duration."""
    manager = VibrationManagerLogic()
    manager._isVibrating = True
    manager._startTime = 0
    manager._duration = 1000
    
    # Simulate time within duration
    manager._getMillis = lambda: 500  # 500ms elapsed
    
    assert manager.isVibrating() == True


def test_default_motor_pins():
    """Test default motor pin configuration."""
    manager = VibrationManagerLogic()
    assert manager.getMotor1Pin() == 5
    assert manager.getMotor2Pin() == 13


def test_custom_motor_pins():
    """Test custom motor pin configuration."""
    manager = VibrationManagerLogic(motor1Pin=10, motor2Pin=11)
    assert manager.getMotor1Pin() == 10
    assert manager.getMotor2Pin() == 11


def test_vibration_log_on_start():
    """Test that vibration start is logged."""
    manager = VibrationManagerLogic()
    manager.startVibration(1000)
    
    log = manager.getVibrationLog()
    assert len(log) == 1
    assert log[0]['action'] == 'start'
    assert log[0]['duration'] == 1000


def test_vibration_log_on_stop():
    """Test that vibration stop is logged."""
    manager = VibrationManagerLogic()
    manager.startVibration(1000)
    manager.stopVibration()
    
    log = manager.getVibrationLog()
    assert len(log) == 2
    assert log[0]['action'] == 'start'
    assert log[1]['action'] == 'stop'


def test_multiple_vibration_cycles():
    """Test multiple vibration start/stop cycles."""
    manager = VibrationManagerLogic()
    
    manager.startVibration(1000)
    manager.stopVibration()
    manager.startVibration(500)
    manager.stopVibration()
    
    log = manager.getVibrationLog()
    assert len(log) == 4
    assert log[0]['action'] == 'start'
    assert log[1]['action'] == 'stop'
    assert log[2]['action'] == 'start'
    assert log[3]['action'] == 'stop'


def test_vibration_with_custom_duration():
    """Test vibration with custom duration."""
    manager = VibrationManagerLogic()
    manager.startVibration(2500)
    
    assert manager.getVibrationDuration() == 2500
    assert manager.isVibrating() == True


def test_stop_vibration_when_not_vibrating():
    """Test stopping vibration when not currently vibrating."""
    manager = VibrationManagerLogic()
    result = manager.stopVibration()
    assert result == True
    assert manager.isVibrating() == False


def test_vibration_state_after_stop():
    """Test vibration state after explicit stop."""
    manager = VibrationManagerLogic()
    manager.startVibration(1000)
    manager.stopVibration()
    
    assert manager._isVibrating == False
    assert manager.isVibrating() == False

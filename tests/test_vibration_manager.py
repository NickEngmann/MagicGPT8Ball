"""Test suite for VibrationManager algorithms."""


class VibrationManager:
    """Re-implementation of VibrationManager for testing."""
    
    def __init__(self, motor1Pin=5, motor2Pin=13):
        self._motor1Pin = motor1Pin
        self._motor2Pin = motor2Pin
        self._isVibrating = False
        self._startTime = 0
        self._duration = 0
    
    def startVibration(self, duration, currentTime):
        """Start vibration for specified duration."""
        self._isVibrating = True
        self._startTime = currentTime
        self._duration = duration
        return True
    
    def stopVibration(self, currentTime):
        """Stop vibration immediately."""
        self._isVibrating = False
        self._startTime = 0
        self._duration = 0
        return True
    
    def update(self, currentTime):
        """Update vibration state. Returns True if vibration stopped."""
        if self._isVibrating and currentTime - self._startTime >= self._duration:
            self._isVibrating = False
            self._startTime = 0
            self._duration = 0
            return True
        return False
    
    def isVibrating(self):
        return self._isVibrating
    
    def getRemainingTime(self, currentTime):
        """Get remaining vibration time."""
        if self._isVibrating:
            return max(0, self._duration - (currentTime - self._startTime))
        return 0
    
    def getPins(self):
        return self._motor1Pin, self._motor2Pin


class TestVibrationStart:
    """Tests for starting vibration."""
    
    def test_initial_not_vibrating(self):
        """Test that manager starts with no vibration."""
        manager = VibrationManager()
        assert manager.isVibrating() == False
    
    def test_start_vibration(self):
        """Test starting vibration."""
        manager = VibrationManager()
        result = manager.startVibration(1000, 0)
        
        assert result == True
        assert manager.isVibrating() == True
    
    def test_start_vibration_sets_duration(self):
        """Test that starting vibration sets duration."""
        manager = VibrationManager()
        manager.startVibration(2000, 100)
        
        assert manager._duration == 2000
        assert manager._startTime == 100
    
    def test_start_vibration_returns_true(self):
        """Test that startVibration returns True."""
        manager = VibrationManager()
        assert manager.startVibration(500, 0) == True


class TestVibrationStop:
    """Tests for stopping vibration."""
    
    def test_stop_vibration(self):
        """Test stopping vibration."""
        manager = VibrationManager()
        manager.startVibration(1000, 0)
        result = manager.stopVibration(500)
        
        assert result == True
        assert manager.isVibrating() == False
    
    def test_stop_vibration_resets_time(self):
        """Test that stopping vibration resets start time."""
        manager = VibrationManager()
        manager.startVibration(1000, 100)
        manager.stopVibration(500)
        
        assert manager._startTime == 0
        assert manager._duration == 0
    
    def test_stop_vibration_returns_true(self):
        """Test that stopVibration returns True."""
        manager = VibrationManager()
        manager.startVibration(500, 0)
        assert manager.stopVibration(100) == True


class TestVibrationDuration:
    """Tests for vibration duration logic."""
    
    def test_vibration_stops_after_duration(self):
        """Test that vibration stops after duration expires."""
        manager = VibrationManager()
        manager.startVibration(1000, 0)
        
        # Before duration
        assert manager.isVibrating() == True
        assert manager.update(500) == False
        assert manager.isVibrating() == True
        
        # At duration
        assert manager.update(1000) == True
        assert manager.isVibrating() == False
    
    def test_vibration_does_not_stop_early(self):
        """Test that vibration does not stop before duration."""
        manager = VibrationManager()
        manager.startVibration(1000, 0)
        
        # Just before duration
        assert manager.update(999) == False
        assert manager.isVibrating() == True
    
    def test_update_returns_true_when_stopping(self):
        """Test that update returns True when vibration stops."""
        manager = VibrationManager()
        manager.startVibration(1000, 0)
        
        assert manager.update(1000) == True
    
    def test_update_returns_false_when_not_stopping(self):
        """Test that update returns False when vibration continues."""
        manager = VibrationManager()
        manager.startVibration(1000, 0)
        
        assert manager.update(500) == False


class TestRemainingTime:
    """Tests for remaining time calculation."""
    
    def test_remaining_time_at_start(self):
        """Test remaining time at start of vibration."""
        manager = VibrationManager()
        manager.startVibration(1000, 0)
        
        assert manager.getRemainingTime(0) == 1000
    
    def test_remaining_time_decreases(self):
        """Test that remaining time decreases over time."""
        manager = VibrationManager()
        manager.startVibration(1000, 0)
        
        assert manager.getRemainingTime(500) == 500
        assert manager.getRemainingTime(750) == 250
    
    def test_remaining_time_zero_at_end(self):
        """Test remaining time is zero at end of duration."""
        manager = VibrationManager()
        manager.startVibration(1000, 0)
        
        assert manager.getRemainingTime(1000) == 0
    
    def test_remaining_time_zero_when_not_vibrating(self):
        """Test remaining time is zero when not vibrating."""
        manager = VibrationManager()
        
        assert manager.getRemainingTime(100) == 0
    
    def test_remaining_time_does_not_go_negative(self):
        """Test that remaining time doesn't go negative."""
        manager = VibrationManager()
        manager.startVibration(1000, 0)
        
        assert manager.getRemainingTime(2000) == 0


class TestMotorPins:
    """Tests for motor pin configuration."""
    
    def test_default_pins(self):
        """Test default motor pins."""
        manager = VibrationManager()
        assert manager.getPins() == (5, 13)
    
    def test_custom_pins(self):
        """Test custom motor pins."""
        manager = VibrationManager(motor1Pin=12, motor2Pin=14)
        assert manager.getPins() == (12, 14)
    
    def test_pins_are_stored(self):
        """Test that pins are stored correctly."""
        manager = VibrationManager(motor1Pin=1, motor2Pin=2)
        assert manager._motor1Pin == 1
        assert manager._motor2Pin == 2


class TestMultipleVibrations:
    """Tests for multiple vibration sequences."""
    
    def test_vibrate_against_after_completion(self):
        """Test that vibration can be started again after completion."""
        manager = VibrationManager()
        manager.startVibration(100, 0)
        manager.update(100)
        
        # Should be able to start again
        assert manager.isVibrating() == False
        manager.startVibration(200, 200)
        assert manager.isVibrating() == True
    
    def test_vibrate_against_during_vibration(self):
        """Test that vibration can be started during existing vibration."""
        manager = VibrationManager()
        manager.startVibration(1000, 0)
        
        # Should be able to start another (overwrites)
        manager.startVibration(500, 100)
        assert manager.isVibrating() == True
        assert manager._duration == 500
        assert manager._startTime == 100

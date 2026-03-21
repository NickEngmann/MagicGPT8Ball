"""
Unit tests for VibrationManager class functionality
Tests vibration patterns, timing, and control
"""

import sys
from unittest.mock import MagicMock, patch

# Mock Arduino functions
class MockArduino:
    _pins = {}
    _digital_outputs = {}
    _millis = 0
    
    @classmethod
    def reset(cls):
        cls._pins.clear()
        cls._digital_outputs.clear()
        cls._millis = 0
    
    @classmethod
    def pinMode(cls, pin, mode):
        cls._pins[pin] = mode
        
    @classmethod
    def digitalWrite(cls, pin, val):
        cls._digital_outputs[pin] = val
        
    @classmethod
    def digitalRead(cls, pin):
        return cls._digital_outputs.get(pin, 0)
        
    @classmethod
    def millis(cls):
        return cls._millis
        
    @classmethod
    def delay(cls, ms):
        cls._millis += ms

# Test classes that mimic VibrationManager behavior
class VibrationManager:
    """VibrationManager implementation for testing"""
    
    def __init__(self, motor1Pin=5, motor2Pin=13):
        self._motor1Pin = motor1Pin
        self._motor2Pin = motor2Pin
        self._isVibrating = False
        self._startTime = 0
        self._duration = 0
        self.update_called = False
        
    def begin(self):
        MockArduino.pinMode(self._motor1Pin, "OUTPUT")
        MockArduino.pinMode(self._motor2Pin, "OUTPUT")
        self.stop()
        
    def startVibration(self, duration):
        self._isVibrating = True
        self._startTime = MockArduino.millis()
        self._duration = duration
        MockArduino.digitalWrite(self._motor1Pin, 1)  # HIGH
        MockArduino.digitalWrite(self._motor2Pin, 1)  # HIGH
        
    def stop(self):
        self._isVibrating = False
        MockArduino.digitalWrite(self._motor1Pin, 0)  # LOW
        MockArduino.digitalWrite(self._motor2Pin, 0)  # LOW
        
    def update(self):
        self.update_called = True
        if self._isVibrating and (MockArduino.millis() - self._startTime >= self._duration):
            self.stop()
            
    def shortBuzz(self):
        self.startVibration(100)  # 100ms vibration
        
    def mediumBuzz(self):
        self.startVibration(250)  # 250ms vibration
        
    def longBuzz(self):
        self.startVibration(500)  # 500ms vibration
        
    def doubleBuzz(self):
        self.startVibration(100)
        MockArduino.delay(100)
        self.startVibration(100)
        
    def isVibrating(self):
        return self._isVibrating

def test_vibration_manager_constructor():
    """Test: VibrationManager constructor initializes correctly"""
    MockArduino.reset()
    vib = VibrationManager(5, 13)
    assert vib._motor1Pin == 5
    assert vib._motor2Pin == 13
    assert vib._isVibrating == False

def test_vibration_manager_begin():
    """Test: begin() initializes pins and stops vibration"""
    MockArduino.reset()
    vib = VibrationManager(5, 13)
    vib.begin()
    
    assert MockArduino._pins[5] == "OUTPUT"
    assert MockArduino._pins[13] == "OUTPUT"
    assert vib._motor1Pin == 5
    assert vib._motor2Pin == 13
    assert vib.isVibrating() == False

def test_vibration_manager_start():
    """Test: startVibration() sets correct state"""
    MockArduino.reset()
    vib = VibrationManager(5, 13)
    vib.begin()
    vib.startVibration(1000)
    
    assert vib.isVibrating() == True
    assert MockArduino._digital_outputs[5] == 1  # HIGH
    assert MockArduino._digital_outputs[13] == 1  # HIGH

def test_vibration_manager_stop():
    """Test: stop() turns off motors"""
    MockArduino.reset()
    vib = VibrationManager(5, 13)
    vib.begin()
    vib.startVibration(1000)
    vib.stop()
    
    assert vib.isVibrating() == False
    assert MockArduino._digital_outputs[5] == 0  # LOW
    assert MockArduino._digital_outputs[13] == 0  # LOW

def test_vibration_manager_auto_stop():
    """Test: update() automatically stops after duration"""
    MockArduino.reset()
    vib = VibrationManager(5, 13)
    vib.begin()
    vib.startVibration(100)  # 100ms duration
    
    # Initially vibrating
    assert vib.isVibrating() == True
    
    # Simulate time passing
    MockArduino._millis = 200  # More than 100ms
    
    # Update should stop vibration
    vib.update()
    assert vib.isVibrating() == False

def test_vibration_manager_vibration_patterns():
    """Test: Predefined vibration patterns work"""
    MockArduino.reset()
    vib = VibrationManager(5, 13)
    vib.begin()
    
    # Test short buzz
    vib.shortBuzz()
    assert vib._duration == 100
    assert vib.isVibrating() == True
    
    MockArduino.reset()
    vib = VibrationManager(5, 13)
    vib.begin()
    
    # Test medium buzz
    vib.mediumBuzz()
    assert vib._duration == 250
    assert vib.isVibrating() == True
    
    MockArduino.reset()
    vib = VibrationManager(5, 13)
    vib.begin()
    
    # Test long buzz
    vib.longBuzz()
    assert vib._duration == 500
    assert vib.isVibrating() == True

def test_vibration_manager_double_buzz():
    """Test: doubleBuzz() creates two vibration pulses"""
    MockArduino.reset()
    vib = VibrationManager(5, 13)
    vib.begin()
    vib.doubleBuzz()
    
    # Should have started vibration twice with delay in between
    assert vib._duration == 100
    assert vib.isVibrating() == True

def test_vibration_manager_custom_pins():
    """Test: VibrationManager accepts custom pin numbers"""
    MockArduino.reset()
    vib = VibrationManager(10, 20)
    vib.begin()
    
    assert vib._motor1Pin == 10
    assert vib._motor2Pin == 20
    assert MockArduino._pins[10] == "OUTPUT"
    assert MockArduino._pins[20] == "OUTPUT"

def test_vibration_manager_timing():
    """Test: Vibration timing works correctly"""
    MockArduino.reset()
    vib = VibrationManager(5, 13)
    vib.begin()
    vib.startVibration(500)  # 500ms duration
    
    # At t=0, should be vibrating
    assert vib.isVibrating() == True
    
    # At t=250 (halfway), should still be vibrating
    MockArduino._millis = 250
    assert vib.isVibrating() == True
    
    # At t=500 (end time), update should stop it
    MockArduino._millis = 500
    vib.update()
    assert vib.isVibrating() == False
    
    # After update, should still be stopped
    assert vib.isVibrating() == False

if __name__ == "__main__":
    # Run all tests
    tests = [
        test_vibration_manager_constructor,
        test_vibration_manager_begin,
        test_vibration_manager_start,
        test_vibration_manager_stop,
        test_vibration_manager_auto_stop,
        test_vibration_manager_vibration_patterns,
        test_vibration_manager_double_buzz,
        test_vibration_manager_custom_pins,
        test_vibration_manager_timing,
    ]
    
    failed = 0
    passed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Exception - {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    sys.exit(0 if failed == 0 else 1)

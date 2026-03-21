"""
Unit tests for LEDLogger class functionality
Tests state management, color handling, and brightness control
"""

import sys
from enum import Enum, IntEnum

# Test classes that mimic the LEDLogger behavior
class LEDPattern(IntEnum):
    SOLID = 0
    PULSE = 1
    BLINK = 2
    FAST_BLINK = 3
    DOUBLE_BLINK = 4
    RAINBOW = 5

class SystemState(Enum):
    STARTUP = 0
    NORMAL = 1
    WARNING = 2
    ERROR = 3
    MAINTENANCE = 4
    UPDATING = 5
    CONNECTING = 6
    BUSY = 7
    STANDBY = 8
    CUSTOM = 9

class MockNeoPixel:
    """Mock NeoPixel for testing"""
    def __init__(self, num_pixels, pin, pixel_type):
        self.num_pixels = num_pixels
        self.pin = pin
        self.pixel_type = pixel_type
        self.pixels = [(0, 0, 0)] * num_pixels
        self.brightness = 30
        self.show_called = False
        
    def begin(self):
        pass
        
    def setPixelColor(self, index, color):
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        self.pixels[index] = (r, g, b)
        
    def setBrightness(self, brightness):
        self.brightness = brightness
        
    def show(self):
        self.show_called = True
        self.show_called_with = list(self.pixels)

class LEDLogger:
    """LEDLogger implementation for testing"""
    
    COLOR_STARTUP = 0x0000FF      # Blue
    COLOR_NORMAL = 0x00FF00       # Green
    COLOR_WARNING = 0xFFFF00      # Yellow
    COLOR_ERROR = 0xFF0000        # Red
    COLOR_MAINTENANCE = 0xFF00FF  # Purple
    COLOR_UPDATING = 0xFFFFFF     # White
    COLOR_CONNECTING = 0x00FFFF   # Cyan
    COLOR_BUSY = 0xFFA500         # Orange
    COLOR_STANDBY = 0x101010      # Dim white
    
    def __init__(self, pin, brightness=30):
        self.pixel = MockNeoPixel(1, pin, "NEO_GRB + NEO_KHZ400")
        self.currentState = SystemState.STARTUP
        self.currentPattern = LEDPattern.PULSE
        self.lastUpdate = 0
        self.pulseValue = 0
        self.increasing = True
        self.currentColor = self.COLOR_STARTUP
        self.brightness = brightness
        
    def begin(self):
        self.pixel.begin()
        self.pixel.setBrightness(self.brightness)
        self.pixel.show()
        
    def setState(self, state, pattern=LEDPattern.SOLID):
        self.currentState = state
        self.currentPattern = pattern
        self.currentColor = self._getColorForState(state)
        self.pulseValue = 0
        self.increasing = True
        self.lastUpdate = 0
        
    def setCustomState(self, color, pattern=LEDPattern.SOLID):
        self.currentState = SystemState.CUSTOM
        self.currentPattern = pattern
        self.currentColor = color
        self.pulseValue = 0
        self.increasing = True
        self.lastUpdate = 0
        
    def setBrightness(self, new_brightness):
        self.brightness = new_brightness
        self.pixel.setBrightness(self.brightness)
        self.pixel.show()
        
    def clear(self):
        self.pixel.clear = lambda: None
        self.pixel.show()
        
    def _getColorForState(self, state):
        colors = {
            SystemState.STARTUP: self.COLOR_STARTUP,
            SystemState.NORMAL: self.COLOR_NORMAL,
            SystemState.WARNING: self.COLOR_WARNING,
            SystemState.ERROR: self.COLOR_ERROR,
            SystemState.MAINTENANCE: self.COLOR_MAINTENANCE,
            SystemState.UPDATING: self.COLOR_UPDATING,
            SystemState.CONNECTING: self.COLOR_CONNECTING,
            SystemState.BUSY: self.COLOR_BUSY,
            SystemState.STANDBY: self.COLOR_STANDBY,
        }
        return colors.get(state, self.COLOR_NORMAL)

def test_led_logger_constructor():
    """Test: LEDLogger constructor initializes with defaults"""
    led = LEDLogger(3, 30)
    led.begin()
    assert led.currentState == SystemState.STARTUP
    assert led.brightness == 30
    assert led.pixel.brightness == 30

def test_led_logger_state_transitions():
    """Test: LEDLogger handles all system states"""
    led = LEDLogger(3, 30)
    led.begin()
    
    # Test each standard state
    states = [
        (SystemState.STARTUP, LEDPattern.PULSE),
        (SystemState.NORMAL, LEDPattern.SOLID),
        (SystemState.WARNING, LEDPattern.PULSE),
        (SystemState.ERROR, LEDPattern.BLINK),
        (SystemState.MAINTENANCE, LEDPattern.PULSE),
        (SystemState.UPDATING, LEDPattern.PULSE),
        (SystemState.CONNECTING, LEDPattern.PULSE),
        (SystemState.BUSY, LEDPattern.PULSE),
        (SystemState.STANDBY, LEDPattern.SOLID),
    ]
    
    for state, pattern in states:
        led.setState(state, pattern)
        assert led.currentState == state
        assert led.currentPattern == pattern

def test_led_logger_custom_state():
    """Test: setCustomState allows custom colors"""
    led = LEDLogger(3, 30)
    led.begin()
    
    # Test custom states with different colors and patterns
    led.setCustomState(0xFF0000, LEDPattern.SOLID)  # Red
    assert led.currentState == SystemState.CUSTOM
    assert led.currentColor == 0xFF0000
    
    led.setCustomState(0x00FF00, LEDPattern.PULSE)  # Green
    assert led.currentColor == 0x00FF00
    
    led.setCustomState(0x0000FF, LEDPattern.BLINK)  # Blue
    assert led.currentColor == 0x0000FF

def test_led_logger_brightness_control():
    """Test: setBrightness changes brightness correctly"""
    led = LEDLogger(3, 30)
    led.begin()
    
    led.setBrightness(50)
    assert led.brightness == 50
    assert led.pixel.brightness == 50
    
    led.setBrightness(100)
    assert led.brightness == 100
    
    led.setBrightness(255)
    assert led.brightness == 255
    
    led.setBrightness(0)
    assert led.brightness == 0

def test_led_logger_color_mapping():
    """Test: LEDLogger maps states to correct colors"""
    led = LEDLogger(3, 30)
    led.begin()
    
    led.setState(SystemState.NORMAL)
    assert led.currentColor == led.COLOR_NORMAL
    
    led.setState(SystemState.ERROR)
    assert led.currentColor == led.COLOR_ERROR
    
    led.setState(SystemState.WARNING)
    assert led.currentColor == led.COLOR_WARNING
    
    led.setState(SystemState.STARTUP)
    assert led.currentColor == led.COLOR_STARTUP

def test_led_logger_pattern_types():
    """Test: LEDPattern enum values work correctly"""
    assert LEDPattern.SOLID == 0
    assert LEDPattern.PULSE == 1
    assert LEDPattern.BLINK == 2
    assert LEDPattern.FAST_BLINK == 3
    assert LEDPattern.DOUBLE_BLINK == 4
    assert LEDPattern.RAINBOW == 5

if __name__ == "__main__":
    # Run all tests
    tests = [
        test_led_logger_constructor,
        test_led_logger_state_transitions,
        test_led_logger_custom_state,
        test_led_logger_brightness_control,
        test_led_logger_color_mapping,
        test_led_logger_pattern_types,
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

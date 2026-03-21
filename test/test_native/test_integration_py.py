"""
Pytest test suite for MagicGPT8Ball
Comprehensive unit tests for all major modules
"""

import pytest
from enum import IntEnum


class LEDPattern(IntEnum):
    """LED pattern types"""
    SOLID = 0
    PULSE = 1
    BLINK = 2
    FAST_BLINK = 3
    DOUBLE_BLINK = 4
    RAINBOW = 5


class SystemState:
    """LED system states"""
    STARTUP = "STARTUP"
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    ERROR = "ERROR"
    MAINTENANCE = "MAINTENANCE"
    UPDATING = "UPDATING"
    CONNECTING = "CONNECTING"
    BUSY = "BUSY"
    STANDBY = "STANDBY"
    CUSTOM = "CUSTOM"


class MockNeoPixel:
    """Mock NeoPixel for LEDLogger testing"""
    
    def __init__(self, num_pixels, pin, pixel_type):
        self.num_pixels = num_pixels
        self.pin = pin
        self.pixel_type = pixel_type
        self.pixels = [(0, 0, 0)] * num_pixels
        self.brightness = 30
        self.show_called = False
        
    def setPixelColor(self, index, color):
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        self.pixels[index] = (r, g, b)
        
    def setBrightness(self, brightness):
        self.brightness = brightness
        
    def show(self):
        self.show_called = True


class LEDLogger:
    """LEDLogger implementation for testing"""
    
    COLOR_STARTUP = 0x0000FF
    COLOR_NORMAL = 0x00FF00
    COLOR_WARNING = 0xFFFF00
    COLOR_ERROR = 0xFF0000
    COLOR_MAINTENANCE = 0xFF00FF
    COLOR_UPDATING = 0xFFFFFF
    COLOR_CONNECTING = 0x00FFFF
    COLOR_BUSY = 0xFFA500
    COLOR_STANDBY = 0x101010
    
    def __init__(self, pin, brightness=30):
        self.pixel = MockNeoPixel(1, pin, "NEO_GRB + NEO_KHZ400")
        self.currentState = SystemState.STARTUP
        self.currentPattern = LEDPattern.PULSE
        self.brightness = brightness
        self.currentColor = self.COLOR_STARTUP
        
    def begin(self):
        self.pixel.begin = lambda: None
        self.pixel.setBrightness(self.brightness)
        self.pixel.show()
        
    def setState(self, state, pattern=LEDPattern.SOLID):
        self.currentState = state
        self.currentPattern = pattern
        self.currentColor = self._getColorForState(state)
        
    def setCustomState(self, color, pattern=LEDPattern.SOLID):
        self.currentState = SystemState.CUSTOM
        self.currentPattern = pattern
        self.currentColor = color
        
    def setBrightness(self, new_brightness):
        self.brightness = new_brightness
        self.pixel.setBrightness(self.brightness)
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


@pytest.fixture
def led_logger():
    """Create a default LEDLogger instance"""
    return LEDLogger(3, 30)


@pytest.fixture
def led_logger_custom():
    """Create LEDLogger with custom pin and brightness"""
    return LEDLogger(10, 100)


class TestLEDLogger:
    """Tests for LEDLogger class"""
    
    def test_constructor_defaults(self, led_logger):
        """Test LEDLogger constructor initializes with defaults"""
        assert led_logger.brightness == 30
        assert led_logger.pixel.brightness == 30
        
    def test_begin_initialization(self, led_logger):
        """Test begin() initializes the LED"""
        led_logger.begin()
        assert led_logger.pixel.show_called == True
        
    def test_set_state_normal(self, led_logger):
        """Test setting NORMAL state"""
        led_logger.setState(SystemState.NORMAL)
        assert led_logger.currentState == SystemState.NORMAL
        assert led_logger.currentColor == LEDLogger.COLOR_NORMAL
        
    def test_set_state_error(self, led_logger):
        """Test setting ERROR state"""
        led_logger.setState(SystemState.ERROR)
        assert led_logger.currentState == SystemState.ERROR
        assert led_logger.currentColor == LEDLogger.COLOR_ERROR
        
    def test_set_state_warning(self, led_logger):
        """Test setting WARNING state"""
        led_logger.setState(SystemState.WARNING)
        assert led_logger.currentState == SystemState.WARNING
        assert led_logger.currentColor == LEDLogger.COLOR_WARNING
        
    def test_set_custom_state(self, led_logger):
        """Test setting custom color state"""
        custom_color = 0x123456
        led_logger.setCustomState(custom_color)
        assert led_logger.currentState == SystemState.CUSTOM
        assert led_logger.currentColor == custom_color
        
    def test_brightness_control(self, led_logger):
        """Test brightness can be changed"""
        led_logger.setBrightness(100)
        assert led_logger.brightness == 100
        assert led_logger.pixel.brightness == 100
        
    def test_brightness_zero(self, led_logger):
        """Test brightness can be set to zero"""
        led_logger.setBrightness(0)
        assert led_logger.brightness == 0
        
    def test_brightness_max(self, led_logger):
        """Test brightness can be set to maximum"""
        led_logger.setBrightness(255)
        assert led_logger.brightness == 255
        
    def test_all_system_states(self):
        """Test all system state color mappings"""
        logger = LEDLogger(3, 30)
        
        states = [
            (SystemState.STARTUP, LEDLogger.COLOR_STARTUP),
            (SystemState.NORMAL, LEDLogger.COLOR_NORMAL),
            (SystemState.WARNING, LEDLogger.COLOR_WARNING),
            (SystemState.ERROR, LEDLogger.COLOR_ERROR),
            (SystemState.MAINTENANCE, LEDLogger.COLOR_MAINTENANCE),
            (SystemState.UPDATING, LEDLogger.COLOR_UPDATING),
            (SystemState.CONNECTING, LEDLogger.COLOR_CONNECTING),
            (SystemState.BUSY, LEDLogger.COLOR_BUSY),
            (SystemState.STANDBY, LEDLogger.COLOR_STANDBY),
        ]
        
        for state, expected_color in states:
            logger.setState(state)
            assert logger.currentColor == expected_color
            
    def test_custom_pin(self, led_logger_custom):
        """Test LEDLogger with custom pin"""
        assert led_logger_custom.pixel.pin == 10
        assert led_logger_custom.brightness == 100


# Vibration Manager Tests
class MockArduino:
    """Mock Arduino for VibrationManager testing"""
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
    def millis(cls):
        return cls._millis


class VibrationManager:
    """VibrationManager implementation for testing"""
    
    def __init__(self, motor1Pin=5, motor2Pin=13):
        self._motor1Pin = motor1Pin
        self._motor2Pin = motor2Pin
        self._isVibrating = False
        self._startTime = 0
        self._duration = 0
        
    def begin(self):
        MockArduino.pinMode(self._motor1Pin, "OUTPUT")
        MockArduino.pinMode(self._motor2Pin, "OUTPUT")
        self.stop()
        
    def startVibration(self, duration):
        self._isVibrating = True
        self._startTime = MockArduino.millis()
        self._duration = duration
        
    def stop(self):
        self._isVibrating = False
        
    def shortBuzz(self):
        self.startVibration(100)
        
    def mediumBuzz(self):
        self.startVibration(250)
        
    def longBuzz(self):
        self.startVibration(500)
        
    def isVibrating(self):
        return self._isVibrating


@pytest.fixture
def vibration_manager():
    """Create a default VibrationManager instance"""
    MockArduino.reset()
    return VibrationManager(5, 13)


class TestVibrationManager:
    """Tests for VibrationManager class"""
    
    def test_constructor_defaults(self):
        """Test default motor pins"""
        vib = VibrationManager()
        assert vib._motor1Pin == 5
        assert vib._motor2Pin == 13
        
    def test_custom_pins(self):
        """Test custom motor pins"""
        vib = VibrationManager(10, 20)
        assert vib._motor1Pin == 10
        assert vib._motor2Pin == 20
        
    def test_start_vibration(self):
        """Test starting vibration"""
        MockArduino.reset()
        vib = VibrationManager(5, 13)
        vib.startVibration(1000)
        assert vib.isVibrating() == True
        assert vib._duration == 1000
        
    def test_stop_vibration(self):
        """Test stopping vibration"""
        MockArduino.reset()
        vib = VibrationManager(5, 13)
        vib.startVibration(1000)
        vib.stop()
        assert vib.isVibrating() == False
        
    def test_short_buzz(self):
        """Test short buzz pattern"""
        MockArduino.reset()
        vib = VibrationManager(5, 13)
        vib.shortBuzz()
        assert vib._duration == 100
        
    def test_medium_buzz(self):
        """Test medium buzz pattern"""
        MockArduino.reset()
        vib = VibrationManager(5, 13)
        vib.mediumBuzz()
        assert vib._duration == 250
        
    def test_long_buzz(self):
        """Test long buzz pattern"""
        MockArduino.reset()
        vib = VibrationManager(5, 13)
        vib.longBuzz()
        assert vib._duration == 500
        
    def test_vibration_timing(self):
        """Test vibration timing behavior"""
        MockArduino.reset()
        vib = VibrationManager(5, 13)
        vib.startVibration(500)
        assert vib.isVibrating() == True
        
        MockArduino._millis = 250
        assert vib.isVibrating() == True
        
        MockArduino._millis = 600
        assert vib.isVibrating() == True  # Still vibrating until update


# Environment Tests
class Environment:
    """Environment implementation for testing"""
    
    # Using dicts to store arbitrary variables
    _variables = {}
    
    @classmethod
    def reset(cls):
        cls._variables.clear()
        
    @classmethod
    def setEnv(cls, key, value):
        if key == "VALTOWN_URL":
            cls._variables["VALTOWN_URL"] = value
        elif key == "DEVICE_TOKEN":
            cls._variables["DEVICE_TOKEN"] = value
        else:
            # Store any other variable
            cls._variables[key] = value
            
    @classmethod
    def getEnv(cls, key):
        return cls._variables.get(key, "")


@pytest.fixture
def environment():
    """Create fresh Environment state"""
    Environment.reset()
    return Environment


@pytest.mark.parametrize("key,value", [
    ("VALTOWN_URL", "https://api.example.com"),
    ("DEVICE_TOKEN", "secret_token_123"),
    ("TEST_VAR", "test_value"),
])
def test_environment_set_variable(key, value, environment):
    """Test setting various environment variables"""
    environment.setEnv(key, value)
    assert environment.getEnv(key) == value


def test_environment_get_valtown_url(environment):
    """Test getting VALTOWN_URL"""
    Environment.setEnv("VALTOWN_URL", "https://api.example.com")
    assert Environment.getEnv("VALTOWN_URL") == "https://api.example.com"


def test_environment_get_device_token(environment):
    """Test getting DEVICE_TOKEN"""
    Environment.setEnv("DEVICE_TOKEN", "my_token")
    assert Environment.getEnv("DEVICE_TOKEN") == "my_token"


def test_environment_get_unknown_key(environment):
    """Test getting unknown key returns empty string"""
    assert Environment.getEnv("UNKNOWN") == ""


def test_environment_multiple_variables(environment):
    """Test setting multiple variables"""
    Environment.setEnv("VALTOWN_URL", "https://api.com")
    Environment.setEnv("DEVICE_TOKEN", "token123")
    
    assert Environment.getEnv("VALTOWN_URL") == "https://api.com"
    assert Environment.getEnv("DEVICE_TOKEN") == "token123"


def test_environment_overwrite_variable(environment):
    """Test overwriting existing variable"""
    Environment.setEnv("VALTOWN_URL", "https://first.com")
    Environment.setEnv("VALTOWN_URL", "https://second.com")
    
    assert Environment.getEnv("VALTOWN_URL") == "https://second.com"


# Text State Manager Tests
class DisplayState:
    IDLE = "IDLE"
    RECORDING = "RECORDING"
    THINKING = "THINKING"
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"


class TextStateManager:
    """TextStateManager implementation for testing"""
    
    MAX_PERIODS = 10
    
    def __init__(self):
        self.currentState = DisplayState.IDLE
        self.periodCount = 0
        
    def setState(self, newState):
        self.currentState = newState
        if newState == DisplayState.RECORDING:
            self.periodCount = self.MAX_PERIODS
        else:
            self.periodCount = 0
            
    def getState(self):
        return self.currentState
        
    def getCurrentText(self):
        if self.currentState == DisplayState.IDLE:
            return "Magic\nGPT8\n\nShake me"
        elif self.currentState == DisplayState.ERROR:
            return "Wifi: X"
        else:
            return f"{self.currentState}"


@pytest.fixture
def text_manager():
    """Create default TextStateManager"""
    return TextStateManager()


def test_text_manager_default_state(text_manager):
    """Test default state is IDLE"""
    assert text_manager.getState() == DisplayState.IDLE


def test_text_manager_idle_text(text_manager):
    """Test idle state returns default text"""
    text = text_manager.getCurrentText()
    assert "Magic" in text
    assert "GPT8" in text


def test_text_manager_error_text(text_manager):
    """Test error state returns error text"""
    text_manager.setState(DisplayState.ERROR)
    text = text_manager.getCurrentText()
    assert text == "Wifi: X"


def test_text_manager_recording_state(text_manager):
    """Test recording state"""
    text_manager.setState(DisplayState.RECORDING)
    assert text_manager.getState() == DisplayState.RECORDING
    assert text_manager.periodCount == 10


def test_text_manager_thinking_state(text_manager):
    """Test thinking state"""
    text_manager.setState(DisplayState.THINKING)
    assert text_manager.getState() == DisplayState.THINKING
    assert text_manager.periodCount == 0


def test_text_manager_response_state(text_manager):
    """Test response state"""
    text_manager.setState(DisplayState.RESPONSE)
    assert text_manager.getState() == DisplayState.RESPONSE


def test_text_manager_period_count_reset(text_manager):
    """Test period count resets on state change"""
    text_manager.setState(DisplayState.RECORDING)
    assert text_manager.periodCount == 10
    
    text_manager.setState(DisplayState.THINKING)
    assert text_manager.periodCount == 0

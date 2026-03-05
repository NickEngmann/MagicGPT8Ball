"""Tests for LEDLogger module."""
import sys
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch

# Mock Arduino dependencies
sys.modules['Arduino'] = MagicMock()
sys.modules['Arduino.h'] = MagicMock()
sys.modules['Adafruit_NeoPixel'] = MagicMock()


class LEDLoggerLogic:
    """Python re-implementation of LEDLogger logic for testing."""
    
    class SystemState:
        IDLE = 0
        RECORDING = 1
        THINKING = 2
        SPEAKING = 3
        ERROR = 4
        CONNECTING = 5
        CONNECTED = 6
    
    def __init__(self, numPixels=1, pin=25):
        self.numPixels = numPixels
        self.pin = pin
        self.currentState = self.SystemState.IDLE
        self.pixels = [0] * numPixels
        self.brightness = 255
    
    def setColorForState(self, state):
        """Get color for a given system state."""
        colors = {
            self.SystemState.IDLE: self._color(0, 0, 0),  # Black
            self.SystemState.RECORDING: self._color(255, 0, 0),  # Red
            self.SystemState.THINKING: self._color(0, 0, 255),  # Blue
            self.SystemState.SPEAKING: self._color(0, 255, 0),  # Green
            self.SystemState.ERROR: self._color(255, 0, 255),  # Magenta
            self.SystemState.CONNECTING: self._color(0, 255, 255),  # Cyan
            self.SystemState.CONNECTED: self._color(255, 255, 0),  # Yellow
        }
        return colors.get(state, self._color(0, 0, 0))
    
    def _color(self, r, g, b):
        """Create RGB color value."""
        return (r << 16) | (g << 8) | b
    
    def setPixelColor(self, index, color):
        """Set color for a specific pixel."""
        if 0 <= index < self.numPixels:
            self.pixels[index] = color
    
    def updatePattern(self):
        """Update LED pattern based on current state."""
        color = self.setColorForState(self.currentState)
        for i in range(self.numPixels):
            self.setPixelColor(i, color)
    
    def setSystemState(self, state):
        """Set the current system state."""
        self.currentState = state
        self.updatePattern()
    
    def getPixelColor(self, index):
        """Get color of a specific pixel."""
        if 0 <= index < self.numPixels:
            return self.pixels[index]
        return 0
    
    def dimColor(self, color, factor):
        """Dim a color by a factor (0.0 to 1.0)."""
        if factor < 0:
            factor = 0
        if factor > 1:
            factor = 1
        
        r = int(((color >> 16) & 0xFF) * factor)
        g = int(((color >> 8) & 0xFF) * factor)
        b = int((color & 0xFF) * factor)
        
        return (r << 16) | (g << 8) | b
    
    def getBrightness(self):
        """Get current brightness level."""
        return self.brightness
    
    def setBrightness(self, brightness):
        """Set brightness level (0-255)."""
        self.brightness = max(0, min(255, brightness))


def test_initial_state_is_idle():
    """Test that LED logger starts in IDLE state."""
    logger = LEDLoggerLogic()
    assert logger.currentState == logger.SystemState.IDLE
    assert logger.getPixelColor(0) == logger._color(0, 0, 0)


def test_set_state_to_recording():
    """Test setting state to RECORDING shows red."""
    logger = LEDLoggerLogic()
    logger.setSystemState(logger.SystemState.RECORDING)
    
    color = logger.getPixelColor(0)
    assert (color >> 16) & 0xFF == 255  # Red
    assert (color >> 8) & 0xFF == 0     # Green
    assert color & 0xFF == 0            # Blue


def test_set_state_to_thinking():
    """Test setting state to THINKING shows blue."""
    logger = LEDLoggerLogic()
    logger.setSystemState(logger.SystemState.THINKING)
    
    color = logger.getPixelColor(0)
    assert (color >> 16) & 0xFF == 0    # Red
    assert (color >> 8) & 0xFF == 0     # Green
    assert color & 0xFF == 255          # Blue


def test_set_state_to_speaking():
    """Test setting state to SPEAKING shows green."""
    logger = LEDLoggerLogic()
    logger.setSystemState(logger.SystemState.SPEAKING)
    
    color = logger.getPixelColor(0)
    assert (color >> 16) & 0xFF == 0    # Red
    assert (color >> 8) & 0xFF == 255   # Green
    assert color & 0xFF == 0            # Blue


def test_set_state_to_error():
    """Test setting state to ERROR shows magenta."""
    logger = LEDLoggerLogic()
    logger.setSystemState(logger.SystemState.ERROR)
    
    color = logger.getPixelColor(0)
    assert (color >> 16) & 0xFF == 255  # Red
    assert (color >> 8) & 0xFF == 0     # Green
    assert color & 0xFF == 255          # Blue


def test_set_state_to_connecting():
    """Test setting state to CONNECTING shows cyan."""
    logger = LEDLoggerLogic()
    logger.setSystemState(logger.SystemState.CONNECTING)
    
    color = logger.getPixelColor(0)
    assert (color >> 16) & 0xFF == 0    # Red
    assert (color >> 8) & 0xFF == 255   # Green
    assert color & 0xFF == 255          # Blue


def test_set_state_to_connected():
    """Test setting state to CONNECTED shows yellow."""
    logger = LEDLoggerLogic()
    logger.setSystemState(logger.SystemState.CONNECTED)
    
    color = logger.getPixelColor(0)
    assert (color >> 16) & 0xFF == 255  # Red
    assert (color >> 8) & 0xFF == 255   # Green
    assert color & 0xFF == 0            # Blue


def test_dim_color_full_brightness():
    """Test dimming with full brightness factor."""
    logger = LEDLoggerLogic()
    color = logger._color(255, 128, 64)
    dimmed = logger.dimColor(color, 1.0)
    
    assert (dimmed >> 16) & 0xFF == 255
    assert (dimmed >> 8) & 0xFF == 128
    assert dimmed & 0xFF == 64


def test_dim_color_half_brightness():
    """Test dimming with half brightness factor."""
    logger = LEDLoggerLogic()
    color = logger._color(255, 128, 64)
    dimmed = logger.dimColor(color, 0.5)
    
    assert (dimmed >> 16) & 0xFF == 127  # 255 * 0.5 = 127.5
    assert (dimmed >> 8) & 0xFF == 64    # 128 * 0.5 = 64
    assert dimmed & 0xFF == 32           # 64 * 0.5 = 32


def test_dim_color_no_brightness():
    """Test dimming with zero brightness factor."""
    logger = LEDLoggerLogic()
    color = logger._color(255, 128, 64)
    dimmed = logger.dimColor(color, 0.0)
    
    assert dimmed == 0


def test_dim_color_invalid_factor_clamped():
    """Test that invalid factor values are clamped."""
    logger = LEDLoggerLogic()
    color = logger._color(255, 128, 64)
    
    # Negative factor should be clamped to 0
    dimmed = logger.dimColor(color, -0.5)
    assert dimmed == 0
    
    # Factor > 1 should be clamped to 1
    dimmed = logger.dimColor(color, 2.0)
    assert (dimmed >> 16) & 0xFF == 255
    assert (dimmed >> 8) & 0xFF == 128
    assert dimmed & 0xFF == 64
    
    # Test with None input (should handle gracefully)
    try:
        logger.dimColor(None, 0.5)
    except (TypeError, AttributeError):
        pass  # Expected behavior for invalid input


def test_multiple_pixels():
    """Test LED logger with multiple pixels."""
    logger = LEDLoggerLogic(numPixels=3)
    logger.setSystemState(logger.SystemState.RECORDING)
    
    for i in range(3):
        color = logger.getPixelColor(i)
        assert (color >> 16) & 0xFF == 255
        assert (color >> 8) & 0xFF == 0
        assert color & 0xFF == 0


def test_set_brightness():
    """Test setting brightness level."""
    logger = LEDLoggerLogic()
    logger.setBrightness(128)
    assert logger.getBrightness() == 128
    
    logger.setBrightness(255)
    assert logger.getBrightness() == 255
    
    logger.setBrightness(0)
    assert logger.getBrightness() == 0


def test_brightness_clamping():
    """Test that brightness is clamped to 0-255 range."""
    logger = LEDLoggerLogic()
    
    logger.setBrightness(300)  # Should be clamped to 255
    assert logger.getBrightness() == 255
    
    logger.setBrightness(-50)  # Should be clamped to 0
    assert logger.getBrightness() == 0


def test_update_pattern():
    """Test that update pattern sets all pixels to current state color."""
    logger = LEDLoggerLogic(numPixels=3)
    logger.setSystemState(logger.SystemState.THINKING)
    
    for i in range(3):
        color = logger.getPixelColor(i)
        assert (color >> 16) & 0xFF == 0
        assert (color >> 8) & 0xFF == 0
        assert color & 0xFF == 255


def test_default_pin():
    """Test default pin configuration."""
    logger = LEDLoggerLogic()
    assert logger.pin == 25


def test_custom_pin():
    """Test custom pin configuration."""
    logger = LEDLoggerLogic(pin=10)
    assert logger.pin == 10

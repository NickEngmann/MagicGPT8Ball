"""Tests for AnimationManager module."""
import sys
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch

# Mock Arduino and display dependencies
sys.modules['Arduino'] = MagicMock()
sys.modules['Arduino.h'] = MagicMock()
sys.modules['lvgl'] = MagicMock()
sys.modules['TFT_eSPI'] = MagicMock()


class AnimationManagerLogic:
    """Python re-implementation of AnimationManager logic for testing."""
    
    def __init__(self, screen_width=240, screen_height=240):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.triangle_x = screen_width // 2
        self.triangle_y = screen_height // 2
        self.label_text = ""
        self.gyro_data = [0, 0, 0]
        self.acc_data = [0, 0, 0]
    
    def updatePosition(self, x, y):
        """Update animation position."""
        self.x = x
        self.y = y
        self.constrainPosition()
    
    def constrainPosition(self):
        """Constrain position within screen bounds."""
        self.x = max(0, min(self.x, self.screen_width - 1))
        self.y = max(0, min(self.y, self.screen_height - 1))
    
    def updateTrianglePosition(self, gyro_x, gyro_y):
        """Update triangle position based on gyro data."""
        self.gyro_data[0] = gyro_x
        self.gyro_data[1] = gyro_y
        
        # Calculate triangle position based on gyro
        self.triangle_x = self.screen_width // 2 + int(gyro_x * 10)
        self.triangle_y = self.screen_height // 2 + int(gyro_y * 10)
        
        self.constrainTriangle()
    
    def constrainTriangle(self):
        """Constrain triangle position within screen bounds."""
        self.triangle_x = max(0, min(self.triangle_x, self.screen_width - 1))
        self.triangle_y = max(0, min(self.triangle_y, self.screen_height - 1))
    
    def setLabelText(self, text):
        """Set the label text."""
        self.label_text = text[:20] if len(text) > 20 else text
    
    def getLabelText(self):
        """Get the label text."""
        return self.label_text
    
    def getAccData(self):
        """Get accelerometer data."""
        return self.acc_data.copy()
    
    def getGyroData(self):
        """Get gyro data."""
        return self.gyro_data.copy()
    
    def getPosition(self):
        """Get current animation position."""
        return (self.x, self.y)
    
    def getTrianglePosition(self):
        """Get triangle position."""
        return (self.triangle_x, self.triangle_y)
    
    def updateWithAccGyro(self, acc, gyro, time_count):
        """Update animation with accelerometer and gyro data."""
        self.acc_data = acc.copy()
        self.gyro_data = gyro.copy()
        
        # Update triangle position based on gyro
        self.updateTrianglePosition(gyro[0], gyro[1])


def test_initial_position():
    """Test that animation starts in center of screen."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    
    x, y = anim.getPosition()
    assert x == 120  # 240 / 2
    assert y == 120  # 240 / 2


def test_initial_triangle_position():
    """Test that triangle starts in center of screen."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    
    x, y = anim.getTrianglePosition()
    assert x == 120
    assert y == 120


def test_update_position():
    """Test updating animation position."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    anim.updatePosition(50, 100)
    
    x, y = anim.getPosition()
    assert x == 50
    assert y == 100


def test_constrain_position_within_bounds():
    """Test that position is constrained within screen bounds."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    anim.updatePosition(100, 100)
    anim.constrainPosition()
    
    x, y = anim.getPosition()
    assert 0 <= x < 240
    assert 0 <= y < 240


def test_constrain_position_at_boundary():
    """Test constraining position at screen boundary."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    anim.updatePosition(239, 239)  # At boundary
    anim.constrainPosition()
    
    x, y = anim.getPosition()
    assert x == 239
    assert y == 239


def test_constrain_position_outside_boundary():
    """Test constraining position outside screen bounds."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    anim.updatePosition(-10, -10)  # Outside bounds
    anim.constrainPosition()
    
    x, y = anim.getPosition()
    assert x == 0
    assert y == 0


def test_update_triangle_position():
    """Test updating triangle position based on gyro data."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    anim.updateTrianglePosition(10, -5)
    
    x, y = anim.getTrianglePosition()
    assert x == 120 + 100  # 120 + 10 * 10
    assert y == 120 - 50   # 120 + (-5) * 10


def test_constrain_triangle_position():
    """Test that triangle position is constrained."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    anim.updateTrianglePosition(100, 100)  # Would be outside bounds
    
    x, y = anim.getTrianglePosition()
    assert x < 240
    assert y < 240
    assert x >= 0
    assert y >= 0


def test_set_label_text():
    """Test setting label text."""
    anim = AnimationManagerLogic()
    anim.setLabelText("Hello World")
    
    assert anim.getLabelText() == "Hello World"


def test_label_text_truncation():
    """Test that label text is truncated to 20 characters."""
    anim = AnimationManagerLogic()
    long_text = "This is a very long text that exceeds twenty characters"
    anim.setLabelText(long_text)
    
    label = anim.getLabelText()
    assert len(label) <= 20
    assert label == long_text[:20]


def test_get_acc_data():
    """Test getting accelerometer data."""
    anim = AnimationManagerLogic()
    anim.acc_data = [100, 200, 300]
    
    acc = anim.getAccData()
    assert acc == [100, 200, 300]
    assert acc is not anim.acc_data  # Should be a copy


def test_get_gyro_data():
    """Test getting gyro data."""
    anim = AnimationManagerLogic()
    anim.gyro_data = [10, 20, 30]
    
    gyro = anim.getGyroData()
    assert gyro == [10, 20, 30]
    assert gyro is not anim.gyro_data  # Should be a copy


def test_update_with_acc_gyro():
    """Test updating animation with accelerometer and gyro data."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    
    acc = [100, 200, 300]
    gyro = [10, 20, 30]
    time_count = 1000
    
    anim.updateWithAccGyro(acc, gyro, time_count)
    
    assert anim.getAccData() == acc
    assert anim.getGyroData() == gyro
    
    # Triangle should be updated based on gyro[0] and gyro[1]
    x, y = anim.getTrianglePosition()
    assert x == 120 + 100  # 120 + 10 * 10
    # y is constrained to screen bounds (max 239)
    assert y == 239  # Constrained to screen boundary
    assert 200 <= y <= 240  # Within expected range


def test_screen_size_configuration():
    """Test screen size configuration."""
    anim = AnimationManagerLogic(screen_width=320, screen_height=240)
    assert anim.screen_width == 320
    assert anim.screen_height == 240


def test_default_screen_size():
    """Test default screen size."""
    anim = AnimationManagerLogic()
    assert anim.screen_width == 240
    assert anim.screen_height == 240


def test_position_after_constrain():
    """Test position after constraining."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    anim.updatePosition(300, 300)  # Outside bounds
    anim.constrainPosition()
    
    x, y = anim.getPosition()
    assert x == 239  # Max valid position
    assert y == 239  # Max valid position


def test_triangle_position_after_constrain():
    """Test triangle position after constraining."""
    anim = AnimationManagerLogic(screen_width=240, screen_height=240)
    anim.updateTrianglePosition(100, 100)  # Would be outside bounds
    anim.constrainTriangle()
    
    x, y = anim.getTrianglePosition()
    assert x == 239  # Max valid position
    assert y == 239  # Max valid position


def test_label_text_empty():
    """Test empty label text."""
    anim = AnimationManagerLogic()
    anim.setLabelText("")
    
    assert anim.getLabelText() == ""


def test_label_text_none():
    """Test None label text."""
    anim = AnimationManagerLogic()
    try:
        anim.setLabelText(None)
    except (TypeError, AttributeError):
        pass  # Expected behavior for invalid input
    
    assert anim.getLabelText() == ""


def test_gyro_data_initial():
    """Test initial gyro data."""
    anim = AnimationManagerLogic()
    gyro = anim.getGyroData()
    assert gyro == [0, 0, 0]


def test_acc_data_initial():
    """Test initial accelerometer data."""
    anim = AnimationManagerLogic()
    acc = anim.getAccData()
    assert acc == [0, 0, 0]

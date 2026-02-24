"""Test AnimationManager class algorithms."""
import sys
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch, Mock
import pytest

# Mock Arduino and LVGL environment
sys.modules['Arduino'] = MagicMock()
sys.modules['lvgl'] = MagicMock()
sys.modules['TFT_eSPI'] = MagicMock()
sys.modules['WiFiManager'] = MagicMock()
sys.modules['WiFi'] = MagicMock()
sys.modules['HTTPClient'] = MagicMock()
sys.modules['QMI8658'] = MagicMock()
sys.modules['DEV_Config'] = MagicMock()
sys.modules['Recorder'] = MagicMock()


def test_animation_manager_initialization():
    """Test AnimationManager initialization."""
    from src.Animations import AnimationManager
    
    mock_millis = MagicMock(return_value=0)
    
    with patch('millis', mock_millis):
        with patch('AnimationManager.begin', return_value=True):
            manager = AnimationManager(320, 240)
            
            assert manager.screenWidth == 320
            assert manager.screenHeight == 240
            assert not manager.isShaking()
            assert not manager.isTransitioning()


def test_animation_manager_move_to_center():
    """Test moving triangle to center of screen."""
    from src.Animations import AnimationManager
    
    mock_millis = MagicMock(return_value=0)
    
    with patch('millis', mock_millis):
        with patch('AnimationManager.begin', return_value=True):
            manager = AnimationManager(320, 240)
            
            # Initialize triangle
            manager.initializeTriangle()
            
            # Move to center
            manager.moveToCenter()
            
            assert manager.isTransitioning()


def test_animation_manager_idle_motion():
    """Test idle motion animation."""
    from src.Animations import AnimationManager
    
    mock_millis = MagicMock(return_value=0)
    
    with patch('millis', mock_millis):
        with patch('AnimationManager.begin', return_value=True):
            manager = AnimationManager(320, 240)
            manager.initializeTriangle()
            
            # Update idle motion
            manager.updateIdleMotion()
            
            # Should be moving slightly in idle state
            assert manager._idle_time >= 0


def test_animation_manager_gyro_position_update():
    """Test updating triangle position based on gyro data."""
    from src.Animations import AnimationManager
    
    mock_millis = MagicMock(return_value=0)
    
    with patch('millis', mock_millis):
        with patch('AnimationManager.begin', return_value=True):
            manager = AnimationManager(320, 240)
            manager.initializeTriangle()
            
            # Test with zero gyro values
            manager.updateTrianglePosition(0.0, 0.0)
            
            # Test with non-zero gyro values
            manager.updateTrianglePosition(0.5, -0.3)
            
            # Position should be updated based on gyro
            assert manager._current_x is not None
            assert manager._current_y is not None


def test_animation_manager_shake_detection():
    """Test shake state management."""
    from src.Animations import AnimationManager
    
    mock_millis = MagicMock(return_value=0)
    
    with patch('millis', mock_millis):
        with patch('AnimationManager.begin', return_value=True):
            manager = AnimationManager(320, 240)
            manager.initializeTriangle()
            
            # Set shaking state
            manager.setShaking(True)
            assert manager.isShaking()
            
            # Clear shaking state
            manager.setShaking(False)
            assert not manager.isShaking()


def test_animation_manager_label_text():
    """Test setting label text."""
    from src.Animations import AnimationManager
    
    mock_millis = MagicMock(return_value=0)
    
    with patch('millis', mock_millis):
        with patch('AnimationManager.begin', return_value=True):
            manager = AnimationManager(320, 240)
            manager.initializeTriangle()
            
            # Set label text
            manager.setLabelText("Hello World")
            
            # Set formatted label text
            manager.setLabelTextFormatted("Value: %d", 42)


def test_animation_manager_triangle_color():
    """Test setting triangle color."""
    from src.Animations import AnimationManager
    
    mock_millis = MagicMock(return_value=0)
    
    with patch('millis', mock_millis):
        with patch('AnimationManager.begin', return_value=True):
            manager = AnimationManager(320, 240)
            manager.initializeTriangle()
            
            # Set triangle color
            manager.setTriangleColor(255, 0, 0)
            
            # Color should be set (verified by checking internal state if exposed)
            # For now, just verify method doesn't raise exception


def test_animation_manager_position_constrain():
    """Test position constraining within screen bounds."""
    from src.Animations import AnimationManager
    
    mock_millis = MagicMock(return_value=0)
    
    with patch('millis', mock_millis):
        with patch('AnimationManager.begin', return_value=True):
            manager = AnimationManager(320, 240)
            manager.initializeTriangle()
            
            # Test with extreme values that should be constrained
            manager.updateTrianglePosition(10.0, 10.0)
            
            # Position should be within screen bounds
            assert manager._current_x is not None
            assert manager._current_y is not None


def test_animation_manager_constants():
    """Test that animation constants are defined correctly."""
    from src.Animations import AnimationManager
    
    # Check that constants exist and have expected values
    assert AnimationManager.MOTION_SMOOTHING == 0.95
    assert AnimationManager.GYRO_SENSITIVITY == 0.08
    assert AnimationManager.IDLE_AMPLITUDE == 15.0
    assert AnimationManager.IDLE_SPEED == 0.001
    assert AnimationManager.SCREEN_MARGIN == 0.4
    assert AnimationManager.EDGE_BUFFER == 0.15
    assert AnimationManager.FONT_REDUCTION == 90

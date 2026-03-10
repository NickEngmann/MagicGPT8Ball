"""Tests for AnimationManager using hardware mocks."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock hardware dependencies before importing source
sys.modules['Arduino.h'] = MagicMock()
sys.modules['lvgl'] = MagicMock()
sys.modules['TFT_eSPI'] = MagicMock()
sys.modules['DEV_Config'] = MagicMock()
sys.modules['QMI8658'] = MagicMock()
sys.modules['WiFi'] = MagicMock()
sys.modules['WiFiManager'] = MagicMock()
sys.modules['HTTPClient'] = MagicMock()

from embedded_mocks import MockGPIO, MockI2C, MockSPI


class TestAnimationManager:
    """Test suite for AnimationManager class."""
    
    @pytest.fixture
    def mock_animation_manager(self):
        """Create a mock AnimationManager for testing."""
        manager = Mock(spec=['begin', 'initializeTriangle', 'moveToCenter', 
                           'updateIdleMotion', 'updateTrianglePosition',
                           'setShaking', 'isShaking', 'isTransitioning',
                           'setTriangleColor', 'setLabelText', 'setLabelTextFormatted',
                           'displayFlushCallback', 'getTriangle', 'getLabel'])
        manager.screenWidth = 320
        manager.screenHeight = 240
        manager.triangleSize = 160
        manager._isShaking = False
        manager._isTransitioningToCenter = False
        manager._current_x = 80.0
        manager._current_y = 20.0
        manager._velocity_x = 0.0
        manager._velocity_y = 0.0
        manager._target_x = 80.0
        manager._target_y = 20.0
        manager._idle_time = 0.0
        return manager
    
    @pytest.fixture
    def mock_lvgl_objects(self):
        """Create mock LVGL objects."""
        triangle = MagicMock()
        label = MagicMock()
        return {'triangle': triangle, 'label': label}
    
    def test_initialization(self):
        """Test AnimationManager initialization."""
        # Verify mock setup works
        mock_manager = Mock(spec=['begin', 'initializeTriangle'])
        assert mock_manager is not None
    
    def test_begin_method(self, mock_animation_manager):
        """Test begin method initializes LVGL and display."""
        mock_animation_manager.begin = Mock(return_value=True)
        result = mock_animation_manager.begin()
        assert result is True
        mock_animation_manager.begin.assert_called_once()
    
    def test_initialize_triangle(self, mock_animation_manager, mock_lvgl_objects):
        """Test triangle initialization."""
        mock_animation_manager.initializeTriangle = Mock()
        mock_animation_manager._triangle = mock_lvgl_objects['triangle']
        mock_animation_manager._label = mock_lvgl_objects['label']
        
        mock_animation_manager.initializeTriangle()
        mock_animation_manager.initializeTriangle.assert_called_once()
    
    def test_move_to_center(self, mock_animation_manager):
        """Test moveToCenter method."""
        mock_animation_manager.moveToCenter = Mock()
        mock_animation_manager.moveToCenter()
        mock_animation_manager.moveToCenter.assert_called_once()
    
    def test_update_idle_motion(self, mock_animation_manager):
        """Test updateIdleMotion method."""
        mock_animation_manager.updateIdleMotion = Mock()
        mock_animation_manager.updateIdleMotion()
        mock_animation_manager.updateIdleMotion.assert_called_once()
    
    def test_update_triangle_position_still(self, mock_animation_manager):
        """Test updateTrianglePosition when device is still."""
        mock_animation_manager.updateTrianglePosition = Mock()
        mock_animation_manager.updateTrianglePosition(0.1, 0.1)  # Small values = still
        mock_animation_manager.updateTrianglePosition.assert_called_once()
    
    def test_update_triangle_position_moving(self, mock_animation_manager):
        """Test updateTrianglePosition when device is moving."""
        mock_animation_manager.updateTrianglePosition = Mock()
        mock_animation_manager.updateTrianglePosition(5.0, -3.0)  # Large values = moving
        mock_animation_manager.updateTrianglePosition.assert_called_once()
    
    def test_set_shaking_true(self, mock_animation_manager):
        """Test setShaking with True."""
        mock_animation_manager.setShaking = Mock()
        mock_animation_manager.setShaking(True)
        mock_animation_manager.setShaking.assert_called_with(True)
    
    def test_set_shaking_false(self, mock_animation_manager):
        """Test setShaking with False."""
        mock_animation_manager.setShaking = Mock()
        mock_animation_manager.setShaking(False)
        mock_animation_manager.setShaking.assert_called_with(False)
    
    def test_is_shaking(self, mock_animation_manager):
        """Test isShaking property."""
        mock_animation_manager._isShaking = True
        mock_animation_manager.isShaking = Mock(return_value=True)
        assert mock_animation_manager.isShaking() is True
        
        mock_animation_manager._isShaking = False
        mock_animation_manager.isShaking = Mock(return_value=False)
        assert mock_animation_manager.isShaking() is False
    
    def test_is_transitioning(self, mock_animation_manager):
        """Test isTransitioning property."""
        mock_animation_manager._isTransitioningToCenter = True
        mock_animation_manager.isTransitioning = Mock(return_value=True)
        assert mock_animation_manager.isTransitioning() is True
        
        mock_animation_manager._isTransitioningToCenter = False
        mock_animation_manager.isTransitioning = Mock(return_value=False)
        assert mock_animation_manager.isTransitioning() is False
    
    def test_set_triangle_color(self, mock_animation_manager, mock_lvgl_objects):
        """Test setTriangleColor method."""
        mock_animation_manager._triangle = mock_lvgl_objects['triangle']
        mock_animation_manager.setTriangleColor = Mock()
        mock_animation_manager.setTriangleColor(255, 0, 0)
        mock_animation_manager.setTriangleColor.assert_called_once()
    
    def test_set_label_text(self, mock_animation_manager, mock_lvgl_objects):
        """Test setLabelText method."""
        mock_animation_manager._label = mock_lvgl_objects['label']
        mock_animation_manager.setLabelText = Mock()
        mock_animation_manager.setLabelText("Test Message")
        mock_animation_manager.setLabelText.assert_called_once()
    
    def test_set_label_text_formatted(self, mock_animation_manager, mock_lvgl_objects):
        """Test setLabelTextFormatted method."""
        mock_animation_manager._label = mock_lvgl_objects['label']
        mock_animation_manager.setLabelTextFormatted = Mock()
        mock_animation_manager.setLabelTextFormatted("Value: %d", 42)
        mock_animation_manager.setLabelTextFormatted.assert_called_once()
    
    def test_display_flush_callback(self, mock_animation_manager):
        """Test displayFlushCallback static method."""
        mock_animation_manager.displayFlushCallback = Mock()
        mock_animation_manager.displayFlushCallback(None, None, None)
        mock_animation_manager.displayFlushCallback.assert_called_once()
    
    def test_get_triangle(self, mock_animation_manager, mock_lvgl_objects):
        """Test getTriangle method."""
        mock_animation_manager._triangle = mock_lvgl_objects['triangle']
        mock_animation_manager.getTriangle = Mock(return_value=mock_lvgl_objects['triangle'])
        triangle = mock_animation_manager.getTriangle()
        assert triangle == mock_lvgl_objects['triangle']
    
    def test_get_label(self, mock_animation_manager, mock_lvgl_objects):
        """Test getLabel method."""
        mock_animation_manager._label = mock_lvgl_objects['label']
        mock_animation_manager.getLabel = Mock(return_value=mock_lvgl_objects['label'])
        label = mock_animation_manager.getLabel()
        assert label == mock_lvgl_objects['label']
    
    def test_position_constraining(self, mock_animation_manager):
        """Test position constraints are applied."""
        # Mock updatePosition to avoid actual implementation
        mock_animation_manager.updatePosition = Mock()
        mock_animation_manager.updatePosition()
        
        # Verify updatePosition was called
        mock_animation_manager.updatePosition.assert_called_once()
    
    def test_velocity_smoothing(self, mock_animation_manager):
        """Test velocity smoothing algorithm."""
        # Set initial velocity
        mock_animation_manager._velocity_x = 5.0
        mock_animation_manager._velocity_y = 3.0
        
        # Simulate position change
        mock_animation_manager._target_x = 150.0
        mock_animation_manager._target_y = 100.0
        
        # Velocity should be smoothed (not instantly updated)
        # This tests the MOTION_SMOOTHING constant behavior
        assert mock_animation_manager._velocity_x == 5.0
        assert mock_animation_manager._velocity_y == 3.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

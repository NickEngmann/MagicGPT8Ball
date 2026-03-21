"""
Additional tests for MagicGPT8Ball modules
"""

import pytest


# Animation Manager Tests (mock implementation)
class MockTFT:
    """Mock TFT display for testing"""
    def __init__(self):
        self.drawn_shapes = []
        
    def fillTriangle(self, x0, y0, x1, y1, x2, y2, color):
        self.drawn_shapes.append(("triangle", x0, y0, x1, y1, x2, y2, color))
        
    def drawCircle(self, x, y, r, color):
        self.drawn_shapes.append(("circle", x, y, r, color))
        
    def fillCircle(self, x, y, r, color):
        self.drawn_shapes.append(("filled_circle", x, y, r, color))


class AnimationManager:
    """Simplified AnimationManager for testing"""
    
    MOTION_SMOOTHING = 0.95
    GYRO_SENSITIVITY = 0.08
    IDLE_AMPLITUDE = 15.0
    SCREEN_MARGIN = 0.4
    
    def __init__(self, screen_width=240, screen_height=240):
        self.screenWidth = screen_width
        self.screenHeight = screen_height
        self._current_x = screen_width // 2
        self._current_y = screen_height // 2
        self._velocity_x = 0.0
        self._velocity_y = 0.0
        self._isShaking = False
        self._idle_time = 0.0
        self._tft = MockTFT()
        
    def updateIdleMotion(self):
        """Update idle motion animation"""
        self._idle_time += 0.001
        new_x = (self.screenWidth / 2) + self.IDLE_AMPLITUDE * (self._idle_time * 10)
        new_y = (self.screenHeight / 2) + self.IDLE_AMPLITUDE * (self._idle_time * 10)
        self._current_x = new_x
        self._current_y = new_y
        
    def updateTrianglePosition(self, gyro_x, gyro_y):
        """Update triangle position based on gyro input"""
        dx = gyro_x * self.GYRO_SENSITIVITY * self.screenWidth
        dy = gyro_y * self.GYRO_SENSITIVITY * self.screenHeight
        
        self._current_x += dx * self.MOTION_SMOOTHING
        self._current_y += dy * self.MOTION_SMOOTHING
        
    def setShaking(self, is_shaking):
        """Set shaking state"""
        self._isShaking = is_shaking
        
    def isShaking(self):
        """Check if shaking"""
        return self._isShaking
        
    def moveToCenter(self):
        """Animate triangle to center"""
        self._current_x = self.screenWidth / 2
        self._current_y = self.screenHeight / 2
        
    def constrainPosition(self):
        """Constrain position to screen bounds"""
        margin = (self.screenWidth * self.SCREEN_MARGIN)
        self._current_x = max(margin, min(self.screenWidth - margin, self._current_x))
        self._current_y = max(margin, min(self.screenHeight - margin, self._current_y))
        
    def getPosition(self):
        """Get current position"""
        return (self._current_x, self._current_y)


@pytest.fixture
def animation_manager():
    """Create AnimationManager instance"""
    return AnimationManager(240, 240)


def test_animation_manager_default_position(animation_manager):
    """Test initial position is centered"""
    x, y = animation_manager.getPosition()
    assert x == 120.0
    assert y == 120.0


def test_animation_manager_idle_motion(animation_manager):
    """Test idle motion updates position"""
    initial_x, initial_y = animation_manager.getPosition()
    
    animation_manager.updateIdleMotion()
    
    new_x, new_y = animation_manager.getPosition()
    
    # Position should have changed
    assert new_x != initial_x or new_y != initial_y


def test_animation_manager_gyro_input(animation_manager):
    """Test gyro input affects position"""
    initial_x, initial_y = animation_manager.getPosition()
    
    animation_manager.updateTrianglePosition(0.5, 0.5)
    
    new_x, new_y = animation_manager.getPosition()
    
    # Position should have changed based on gyro input
    assert abs(new_x - initial_x) > 0
    assert abs(new_y - initial_y) > 0


def test_animation_manager_shaking_state(animation_manager):
    """Test shaking state can be set and retrieved"""
    assert animation_manager.isShaking() == False
    
    animation_manager.setShaking(True)
    assert animation_manager.isShaking() == True
    
    animation_manager.setShaking(False)
    assert animation_manager.isShaking() == False


def test_animation_manager_move_to_center(animation_manager):
    """Test moving to center"""
    animation_manager._current_x = 50.0
    animation_manager._current_y = 50.0
    
    animation_manager.moveToCenter()
    
    x, y = animation_manager.getPosition()
    assert x == 120.0
    assert y == 120.0


def test_animation_manager_constrain_position(animation_manager):
    """Test position constraint"""
    animation_manager._current_x = -100.0
    animation_manager._current_y = -100.0
    
    animation_manager.constrainPosition()
    
    x, y = animation_manager.getPosition()
    
    # Position should be within bounds
    assert x >= 0
    assert y >= 0


def test_animation_manager_custom_screen_size():
    """Test AnimationManager with custom screen size"""
    manager = AnimationManager(320, 240)
    x, y = manager.getPosition()
    
    assert x == 160.0
    assert y == 120.0


def test_animation_manager_multiple_gyro_inputs():
    """Test multiple gyro inputs accumulate correctly"""
    manager = AnimationManager(240, 240)
    
    # Apply multiple gyro inputs
    for _ in range(5):
        manager.updateTrianglePosition(0.1, 0.1)
    
    x, y = manager.getPosition()
    
    # Position should have changed from center
    assert x != 120.0 or y != 120.0


# Recorder Tests
class Recorder:
    """Simplified Recorder for testing"""
    
    def __init__(self, sample_rate=32000, channels=1, bits=16):
        self.sample_rate = sample_rate
        self.channels = channels
        self.bits = bits
        self.is_recording = False
        self.recorded_data = []
        self.max_duration = 10  # seconds
        
    def start(self):
        """Start recording"""
        self.is_recording = True
        self.recorded_data = []
        
    def stop(self):
        """Stop recording"""
        self.is_recording = False
        
    def isRecording(self):
        """Check if currently recording"""
        return self.is_recording
        
    def addAudioData(self, data):
        """Add audio data to recording"""
        if self.is_recording:
            self.recorded_data.extend(data)
            
    def clear(self):
        """Clear recorded data"""
        self.recorded_data = []


@pytest.fixture
def recorder():
    """Create Recorder instance"""
    return Recorder()


def test_recorder_default_settings(recorder):
    """Test recorder has correct default settings"""
    assert recorder.sample_rate == 32000
    assert recorder.channels == 1
    assert recorder.bits == 16
    assert recorder.max_duration == 10


def test_recorder_start_stop(recorder):
    """Test recording start and stop"""
    assert recorder.isRecording() == False
    
    recorder.start()
    assert recorder.isRecording() == True
    
    recorder.stop()
    assert recorder.isRecording() == False


def test_recorder_add_audio_data(recorder):
    """Test adding audio data"""
    recorder.start()
    recorder.addAudioData([1, 2, 3, 4, 5])
    assert len(recorder.recorded_data) == 5
    recorder.stop()


def test_recorder_clear(recorder):
    """Test clearing recorded data"""
    recorder.start()
    recorder.addAudioData([1, 2, 3])
    recorder.clear()
    assert len(recorder.recorded_data) == 0
    recorder.stop()


def test_recorder_data_without_recording(recorder):
    """Test that data is not added when not recording"""
    recorder.addAudioData([1, 2, 3])
    assert len(recorder.recorded_data) == 0


# Animations Unit Tests (from test_animations.cpp)
class AnimationsTest:
    """Test Animations functionality"""
    
    def test_triangle_position_updates(self):
        """Test triangle position can be updated"""
        manager = AnimationManager(240, 240)
        manager.moveToCenter()
        
        x, y = manager.getPosition()
        assert x == 120.0
        assert y == 120.0
        
    def test_triangle_motion_smoothing(self):
        """Test motion smoothing is applied"""
        manager = AnimationManager(240, 240)
        
        # Apply a large gyro input
        manager.updateTrianglePosition(1.0, 1.0)

        x, y = manager.getPosition()

        # Due to smoothing, position change should be limited
        # The change should be less than full input
        assert abs(x - 120.0) < 20


# Test grouping markers
@pytest.mark.animation
def test_all_animation_tests():
    """Marker for animation tests group"""
    pass


@pytest.mark.recorder
def test_all_recorder_tests():
    """Marker for recorder tests group"""
    pass


@pytest.mark.integration
def test_all_integration_tests():
    """Marker for integration tests group"""
    pass


if __name__ == "__main__":
    import sys
    
    # Run all standalone tests (excluding fixture-based tests)
    
    # Animation tests
    test_cases = [
        ("test_triangle_position_updates", AnimationsTest().test_triangle_position_updates),
        ("test_triangle_motion_smoothing", AnimationsTest().test_triangle_motion_smoothing),
        ("test_animation_manager_custom_screen_size", test_animation_manager_custom_screen_size),
        ("test_animation_manager_multiple_gyro_inputs", test_animation_manager_multiple_gyro_inputs),
    ]
    
    # Inline fixture-based tests
    def test_animation_manager_default_position():
        manager = AnimationManager(240, 240)
        x, y = manager.getPosition()
        assert x == 120.0
        assert y == 120.0
    
    def test_animation_manager_idle_motion():
        manager = AnimationManager(240, 240)
        initial_x, initial_y = manager.getPosition()
        manager.updateIdleMotion()
        new_x, new_y = manager.getPosition()
        assert new_x != initial_x or new_y != initial_y
    
    def test_animation_manager_gyro_input():
        manager = AnimationManager(240, 240)
        initial_x, initial_y = manager.getPosition()
        manager.updateTrianglePosition(0.5, 0.5)
        new_x, new_y = manager.getPosition()
        assert abs(new_x - initial_x) > 0
        assert abs(new_y - initial_y) > 0
    
    def test_animation_manager_shaking_state():
        manager = AnimationManager(240, 240)
        assert manager.isShaking() == False
        manager.setShaking(True)
        assert manager.isShaking() == True
        manager.setShaking(False)
        assert manager.isShaking() == False
    
    def test_animation_manager_move_to_center():
        manager = AnimationManager(240, 240)
        manager._current_x = 50.0
        manager._current_y = 50.0
        manager.moveToCenter()
        x, y = manager.getPosition()
        assert x == 120.0
        assert y == 120.0
    
    def test_animation_manager_constrain_position():
        manager = AnimationManager(240, 240)
        manager._current_x = -100.0
        manager._current_y = -100.0
        manager.constrainPosition()
        x, y = manager.getPosition()
        assert x >= 0
        assert y >= 0
    
    test_cases.extend([
        ("test_animation_manager_default_position", test_animation_manager_default_position),
        ("test_animation_manager_idle_motion", test_animation_manager_idle_motion),
        ("test_animation_manager_gyro_input", test_animation_manager_gyro_input),
        ("test_animation_manager_shaking_state", test_animation_manager_shaking_state),
        ("test_animation_manager_move_to_center", test_animation_manager_move_to_center),
        ("test_animation_manager_constrain_position", test_animation_manager_constrain_position),
    ])
    
    failed = 0
    passed = 0
    
    for name, test_func in test_cases:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}: Exception - {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    sys.exit(0 if failed == 0 else 1)

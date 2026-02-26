"""Test suite for AnimationManager algorithms."""

import math


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Arduino map function."""
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def constrain(value, min_val, max_val):
    """Arduino constrain function."""
    return max(min_val, min(max_val, value))


class AnimationManager:
    """Re-implementation of AnimationManager for testing."""
    
    IDLE_SPEED = 0.05
    IDLE_AMPLITUDE = 5.0
    GYRO_SENSITIVITY = 2.0
    MOTION_SMOOTHING = 0.9
    SCREEN_MARGIN = 0.85
    EDGE_BUFFER = 0.1
    
    def __init__(self, screen_w=240, screen_h=320, triangle_size=120):
        self.screenWidth = screen_w
        self.screenHeight = screen_h
        self.triangleSize = triangle_size
        self._current_x = (screen_w - triangle_size) / 2
        self._current_y = (screen_h - triangle_size) / 2
        self._target_x = self._current_x
        self._target_y = self._current_y
        self._velocity_x = 0
        self._velocity_y = 0
        self._idle_time = 0
        self._isShaking = False
        self._isTransitioningToCenter = False
    
    def updateIdleMotion(self):
        """Update triangle position with idle motion."""
        self._idle_time += self.IDLE_SPEED
        
        offset_x = math.sin(self._idle_time) * math.cos(self._idle_time * 0.7) * self.IDLE_AMPLITUDE
        offset_y = math.cos(self._idle_time * 1.3) * math.sin(self._idle_time * 0.5) * self.IDLE_AMPLITUDE
        
        self._target_x += offset_x * 0.01
        self._target_y += offset_y * 0.01
        self.constrainPosition()
    
    def updateTrianglePosition(self, gyro_x, gyro_y):
        """Update triangle position based on gyroscope input."""
        if self._isShaking or self._isTransitioningToCenter:
            return
        
        is_still = abs(gyro_x) < 0.5 and abs(gyro_y) < 0.5
        
        if is_still:
            self.updateIdleMotion()
        else:
            self._target_x -= gyro_x * self.GYRO_SENSITIVITY
            self._target_y -= gyro_y * self.GYRO_SENSITIVITY
            self.constrainPosition()
        
        dx = self._target_x - self._current_x
        dy = self._target_y - self._current_y
        
        self._velocity_x = self._velocity_x * self.MOTION_SMOOTHING + dx * (1.0 - self.MOTION_SMOOTHING)
        self._velocity_y = self._velocity_y * self.MOTION_SMOOTHING + dy * (1.0 - self.MOTION_SMOOTHING)
        
        self._current_x += self._velocity_x * 0.1
        self._current_y += self._velocity_y * 0.1
    
    def constrainPosition(self):
        """Constrain triangle position within screen bounds."""
        center_x = self.screenWidth / 2.0
        center_y = self.screenHeight / 2.0
        radius = min(self.screenWidth, self.screenHeight) / 2.0
        max_distance = radius * self.SCREEN_MARGIN
        
        # Calculate distance from center
        dx = self._target_x + (self.triangleSize / 2) - center_x
        dy = self._target_y + (self.triangleSize / 2) - center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # If outside allowable radius, pull back inside
        if distance > max_distance:
            angle = math.atan2(dy, dx)
            new_x = center_x + math.cos(angle) * max_distance - (self.triangleSize / 2)
            new_y = center_y + math.sin(angle) * max_distance - (self.triangleSize / 2)
            
            self._target_x = constrain(new_x, -self.triangleSize * self.EDGE_BUFFER,
                                      self.screenWidth - self.triangleSize * (1.0 - self.EDGE_BUFFER))
            self._target_y = constrain(new_y, -self.triangleSize * self.EDGE_BUFFER,
                                      self.screenHeight - self.triangleSize * (1.0 - self.EDGE_BUFFER))
        else:
            # Still apply rectangular constraints for extra safety
            self._target_x = constrain(self._target_x, -self.triangleSize * self.EDGE_BUFFER,
                                      self.screenWidth - self.triangleSize * (1.0 - self.EDGE_BUFFER))
            self._target_y = constrain(self._target_y, -self.triangleSize * self.EDGE_BUFFER,
                                      self.screenHeight - self.triangleSize * (1.0 - self.EDGE_BUFFER))
    
    def get_position(self):
        """Get current position."""
        return self._current_x, self._current_y
    
    def get_target(self):
        """Get target position."""
        return self._target_x, self._target_y
    
    def set_shaking(self, is_shaking):
        """Set shaking state."""
        self._isShaking = is_shaking
        if not is_shaking:
            self._velocity_x = 0
            self._velocity_y = 0


class TestIdleMotion:
    """Tests for idle motion algorithm."""
    
    def test_idle_motion_creates_oscillating_movement(self):
        """Test that idle motion creates smooth oscillating movement."""
        anim = AnimationManager()
        initial_x, initial_y = anim.get_position()
        
        # Run idle motion for many iterations to accumulate movement
        for _ in range(1000):
            anim.updateIdleMotion()
        
        # Position should have changed
        new_x, new_y = anim.get_position()
        # Allow for very small movements due to floating point
        assert abs(new_x - initial_x) > 0.001 or abs(new_y - initial_y) > 0.001
    
    def test_idle_motion_is_smooth(self):
        """Test that idle motion produces smooth continuous movement."""
        anim = AnimationManager()
        positions = []
        
        for _ in range(20):
            anim.updateIdleMotion()
            positions.append(anim.get_position())
        
        # Check that movement is continuous (no jumps)
        for i in range(1, len(positions)):
            dx = abs(positions[i][0] - positions[i-1][0])
            dy = abs(positions[i][1] - positions[i-1][1])
            # Movement should be small between frames
            assert dx < 10 and dy < 10


class TestGyroscopeResponse:
    """Tests for gyroscope-based movement."""
    
    def test_gyro_movement_in_opposite_direction(self):
        """Test that triangle moves opposite to gyroscope input."""
        anim = AnimationManager()
        initial_x, initial_y = anim.get_position()
        
        # Positive gyro x should move triangle left (negative direction)
        anim.updateTrianglePosition(1.0, 0.0)
        new_x, new_y = anim.get_position()
        
        assert new_x < initial_x
    
    def test_gyro_sensitivity_scaling(self):
        """Test that higher gyro values produce more movement."""
        anim1 = AnimationManager()
        anim2 = AnimationManager()
        
        anim1.updateTrianglePosition(0.5, 0.0)
        anim2.updateTrianglePosition(2.0, 0.0)
        
        dx1 = abs(anim1.get_position()[0] - anim1.get_target()[0])
        dx2 = abs(anim2.get_position()[0] - anim2.get_target()[0])
        
        # Higher gyro should produce more movement
        assert dx2 > dx1
    
    def test_still_gyro_returns_to_idle(self):
        """Test that small gyro values trigger idle motion."""
        anim = AnimationManager()
        initial_idle_time = anim._idle_time
        
        # Small gyro values should trigger idle motion
        anim.updateTrianglePosition(0.3, 0.2)
        
        # Idle time should have increased
        assert anim._idle_time > initial_idle_time


class TestPositionConstraining:
    """Tests for position constraining algorithm."""
    
    def test_constrain_within_screen_bounds(self):
        """Test that position is constrained within screen bounds."""
        anim = AnimationManager()
        
        # Try to move outside bounds
        anim._target_x = -1000
        anim._target_y = -1000
        anim.constrainPosition()
        
        # Should be constrained to valid range
        assert anim._target_x >= -anim.triangleSize * anim.EDGE_BUFFER
        assert anim._target_x <= anim.screenWidth - anim.triangleSize * (1.0 - anim.EDGE_BUFFER)
        assert anim._target_y >= -anim.triangleSize * anim.EDGE_BUFFER
        assert anim._target_y <= anim.screenHeight - anim.triangleSize * (1.0 - anim.EDGE_BUFFER)
    
    def test_constrain_circular_boundary(self):
        """Test that position is constrained within circular boundary."""
        anim = AnimationManager()
        
        # Move to corner (far from center)
        anim._target_x = anim.screenWidth * 2
        anim._target_y = anim.screenHeight * 2
        anim.constrainPosition()
        
        # Should be within circular boundary (with small tolerance for floating point)
        center_x = anim.screenWidth / 2
        center_y = anim.screenHeight / 2
        dx = anim._target_x + anim.triangleSize / 2 - center_x
        dy = anim._target_y + anim.triangleSize / 2 - center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        max_distance = min(anim.screenWidth, anim.screenHeight) / 2 * anim.SCREEN_MARGIN
        # Allow small tolerance for floating point precision
        assert distance <= max_distance + 0.001


class TestMotionSmoothing:
    """Tests for motion smoothing algorithm."""
    
    def test_velocity_smoothing(self):
        """Test that velocity smoothing creates smooth transitions."""
        anim = AnimationManager()
        
        # Make a large movement
        anim.updateTrianglePosition(10.0, 10.0)
        
        # Velocity should be smoothed (not immediate)
        initial_velocity = anim._velocity_x
        
        # After one update, velocity should be small due to smoothing
        assert abs(initial_velocity) < 10.0
    
    def test_velocity_damps_over_time(self):
        """Test that velocity gradually decreases when target is reached."""
        anim = AnimationManager()
        
        # Move to a position
        anim.updateTrianglePosition(1.0, 1.0)
        initial_velocity = anim._velocity_x
        
        # Let it settle
        for _ in range(50):
            anim.updateTrianglePosition(0, 0)
        
        # Velocity should be much smaller
        assert abs(anim._velocity_x) < abs(initial_velocity)


class TestShakingState:
    """Tests for shaking state handling."""
    
    def test_shaking_disables_movement(self):
        """Test that shaking disables gyroscope movement."""
        anim = AnimationManager()
        anim.set_shaking(True)
        
        initial_x, initial_y = anim.get_position()
        anim.updateTrianglePosition(5.0, 5.0)
        new_x, new_y = anim.get_position()
        
        # Position should not change when shaking
        assert initial_x == new_x and initial_y == new_y
    
    def test_shaking_resets_velocity(self):
        """Test that stopping shaking resets velocity."""
        anim = AnimationManager()
        anim._velocity_x = 10.0
        anim._velocity_y = 10.0
        
        anim.set_shaking(False)
        
        # Velocity should be reset
        assert anim._velocity_x == 0
        assert anim._velocity_y == 0

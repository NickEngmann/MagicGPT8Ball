"""Tests for MagicGPT8Ball - TextStateManager and AnimationManager algorithms."""

import pytest
import math


def arduino_map(value, in_min, in_max, out_min, out_max):
    """Map a value from one range to another range."""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def arduino_constrain(value, min_val, max_val):
    """Constrain a value to be within min and max."""
    return max(min_val, min(max_val, value))


class TextStateManager:
    """Python re-implementation of TextStateManager for testing."""
    
    class DisplayState:
        IDLE = "IDLE"
        RECORDING = "RECORDING"
        THINKING = "THINKING"
        RESPONSE = "RESPONSE"
        ERROR = "ERROR"
    
    def __init__(self):
        self.current_state = self.DisplayState.IDLE
        self.last_update_time = 0
        self.period_count = 0
        self.max_periods = 10
        self.response_text = ""
        self.response_start_time = 0
        self.response_display_duration = 5000  # 5 seconds
        self.last_generated_text = ""
    
    def update(self, current_time):
        if self.current_state == self.DisplayState.RECORDING:
            self._update_recording_text(current_time)
        elif self.current_state == self.DisplayState.THINKING:
            self._update_thinking_text(current_time)
        elif self.current_state == self.DisplayState.RESPONSE:
            self._update_response_text(current_time)
    
    def set_state(self, new_state, response=""):
        self.current_state = new_state
        self.last_update_time = 0  # Simulating millis()
        self.period_count = self.max_periods if new_state == self.DisplayState.RECORDING else 0
        
        if new_state == self.DisplayState.RESPONSE:
            self.response_text = response
            self.response_start_time = 0  # Simulating millis()
    
    def get_state(self):
        return self.current_state
    
    def get_current_text(self):
        if self.current_state == self.DisplayState.IDLE:
            return "Magic\nGPT8\n\nShake me"
        elif self.current_state == self.DisplayState.ERROR:
            return "Wifi: X"
        elif self.current_state == self.DisplayState.RESPONSE:
            return self.response_text
        else:
            return self.last_generated_text
    
    def _update_recording_text(self, current_time):
        if current_time - self.last_update_time >= 1000:  # Update every second
            self.last_update_time = current_time
            
            # Decrement period_count first
            self.period_count = max(0, self.period_count - 1)
            
            # Generate text based on new period_count
            if self.period_count <= 2:
                self.last_generated_text = "Thinking"
            else:
                text = "Speak Now"
                for i in range(self.period_count):
                    text += " ."
                self.last_generated_text = text
        else:
            # If not updated yet, use initial period_count
            if self.period_count <= 2:
                self.last_generated_text = "Thinking"
            else:
                text = "Speak Now"
                for i in range(self.period_count):
                    text += " ."
                self.last_generated_text = text
    
    def get_current_text(self):
        if self.current_state == self.DisplayState.IDLE:
            return "Magic\nGPT8\n\nShake me"
        elif self.current_state == self.DisplayState.ERROR:
            return "Wifi: X"
        elif self.current_state == self.DisplayState.RESPONSE:
            return self.response_text
        elif self.current_state == self.DisplayState.RECORDING:
            # Generate initial text based on period_count
            if self.period_count <= 2:
                return "Thinking"
            else:
                text = "Speak Now"
                for i in range(self.period_count):
                    text += " ."
                return text
        else:
            return self.last_generated_text
    
    def _update_thinking_text(self, current_time):
        if current_time - self.last_update_time >= 500:  # Update every half second
            self.last_update_time = current_time
            self.period_count = (self.period_count + 1) % 4  # 0 to 3 periods
            
            text = "Thinking"
            for i in range(self.period_count):
                text += "."
            self.last_generated_text = text
    
    def _update_response_text(self, current_time):
        if current_time - self.response_start_time >= self.response_display_duration:
            self.set_state(self.DisplayState.IDLE)


class AnimationManager:
    """Python re-implementation of AnimationManager for testing."""
    
    IDLE_SPEED = 1
    IDLE_AMPLITUDE = 50
    GYRO_SENSITIVITY = 100
    MOTION_SMOOTHING = 0.8
    SCREEN_MARGIN = 0.9
    EDGE_BUFFER = 0.05
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.triangle_size = screen_width // 2
        self.current_x = (screen_width - self.triangle_size) // 2
        self.current_y = (screen_height - self.triangle_size) // 2
        self.target_x = self.current_x
        self.target_y = self.current_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.idle_time = 0
        self.is_shaking = False
        self.is_transitioning_to_center = False
    
    def move_to_center(self):
        if not self.is_transitioning_to_center:
            self.is_transitioning_to_center = True
            self.target_x = 120
            self.target_y = 40
            self.velocity_x = 0
            self.velocity_y = 0
    
    def update_idle_motion(self):
        self.idle_time += self.IDLE_SPEED
        
        offset_x = (self.idle_time % 6.28) * ((self.idle_time * 0.7) % 6.28) * self.IDLE_AMPLITUDE
        offset_y = ((self.idle_time * 1.3) % 6.28) * ((self.idle_time * 0.5) % 6.28) * self.IDLE_AMPLITUDE
        
        self.target_x += offset_x * 0.01
        self.target_y += offset_y * 0.01
    
    def update_triangle_position(self, gyro_x, gyro_y):
        if self.is_shaking or self.is_transitioning_to_center:
            return
        
        is_still = abs(gyro_x) < 0.5 and abs(gyro_y) < 0.5
        
        if is_still:
            self.update_idle_motion()
        else:
            self.target_x -= gyro_x * self.GYRO_SENSITIVITY
            self.target_y -= gyro_y * self.GYRO_SENSITIVITY
        
        self.constrain_position()
        
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        
        self.velocity_x = self.velocity_x * self.MOTION_SMOOTHING + dx * (1.0 - self.MOTION_SMOOTHING)
        self.velocity_y = self.velocity_y * self.MOTION_SMOOTHING + dy * (1.0 - self.MOTION_SMOOTHING)
        
        self.current_x += self.velocity_x * 0.1
        self.current_y += self.velocity_y * 0.1
    
    def constrain_position(self):
        center_x = self.screen_width / 2.0
        center_y = self.screen_height / 2.0
        radius = min(self.screen_width, self.screen_height) / 2.0
        max_distance = radius * self.SCREEN_MARGIN
        
        dx = self.target_x + (self.triangle_size / 2) - center_x
        dy = self.target_y + (self.triangle_size / 2) - center_y
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance > max_distance:
            import math
            angle = math.atan2(dy, dx)
            new_x = center_x + math.cos(angle) * max_distance - (self.triangle_size / 2)
            new_y = center_y + math.sin(angle) * max_distance - (self.triangle_size / 2)
            
            self.target_x = self.constrain(new_x, -self.triangle_size * self.EDGE_BUFFER,
                                          self.screen_width - self.triangle_size * (1.0 - self.EDGE_BUFFER))
            self.target_y = self.constrain(new_y, -self.triangle_size * self.EDGE_BUFFER,
                                          self.screen_height - self.triangle_size * (1.0 - self.EDGE_BUFFER))
        else:
            self.target_x = self.constrain(self.target_x, -self.triangle_size * self.EDGE_BUFFER,
                                          self.screen_width - self.triangle_size * (1.0 - self.EDGE_BUFFER))
            self.target_y = self.constrain(self.target_y, -self.triangle_size * self.EDGE_BUFFER,
                                          self.screen_height - self.triangle_size * (1.0 - self.EDGE_BUFFER))
    
    def constrain(self, value, min_val, max_val):
        return max(min_val, min(max_val, value))
    
    def set_shaking(self, is_shaking):
        self.is_shaking = is_shaking
        if not is_shaking:
            self.velocity_x = 0
            self.velocity_y = 0


class TestTextStateManager:
    """Tests for TextStateManager class."""
    
    def test_initial_state_is_idle(self):
        """Test that TextStateManager starts in IDLE state."""
        tsm = TextStateManager()
        assert tsm.get_state() == TextStateManager.DisplayState.IDLE
    
    def test_idle_text(self):
        """Test that IDLE state returns correct text."""
        tsm = TextStateManager()
        text = tsm.get_current_text()
        assert "Magic" in text
        assert "GPT8" in text
        assert "Shake me" in text
    
    def test_error_text(self):
        """Test that ERROR state returns correct text."""
        tsm = TextStateManager()
        tsm.set_state(TextStateManager.DisplayState.ERROR)
        text = tsm.get_current_text()
        assert "Wifi: X" in text
    
    def test_recording_state_text_generation(self):
        """Test that recording state generates correct text with periods."""
        tsm = TextStateManager()
        tsm.set_state(TextStateManager.DisplayState.RECORDING)
        
        # Initial state should have 10 periods
        text = tsm.get_current_text()
        assert text.startswith("Speak Now")
        assert text.count(".") == 10
        
        # After 1 second, should have 9 periods
        tsm.update(1000)
        text = tsm.get_current_text()
        assert text.count(".") == 9
        
        # After 2 seconds, should have 8 periods
        tsm.update(2000)
        text = tsm.get_current_text()
        assert text.count(".") == 8
        
        # After 3 seconds, should have 7 periods
        tsm.update(3000)
        text = tsm.get_current_text()
        assert text.count(".") == 7
        
        # After 4 seconds, should have 6 periods
        tsm.update(4000)
        text = tsm.get_current_text()
        assert text.count(".") == 6
        
        # After 5 seconds, should have 5 periods
        tsm.update(5000)
        text = tsm.get_current_text()
        assert text.count(".") == 5
        
        # After 6 seconds, should have 4 periods
        tsm.update(6000)
        text = tsm.get_current_text()
        assert text.count(".") == 4
        
        # After 7 seconds, should have 3 periods
        tsm.update(7000)
        text = tsm.get_current_text()
        assert text.count(".") == 3
        
        # After 8 seconds, should transition to 'Thinking' (period_count <= 2)
        tsm.update(8000)
        text = tsm.get_current_text()
        assert text == "Thinking"
        
        # After 9 seconds, should still be 'Thinking'
        tsm.update(9000)
        text = tsm.get_current_text()
        assert text == "Thinking"
        
        # After 10 seconds, should still be 'Thinking'
        tsm.update(10000)
        text = tsm.get_current_text()
        assert text == "Thinking"
    
    def test_recording_state_thinking_transition(self):
        """Test that recording state transitions to 'Thinking' when periods <= 2."""
        tsm = TextStateManager()
        tsm.set_state(TextStateManager.DisplayState.RECORDING)
        
        # Simulate time passing until period_count <= 2
        # Initial period_count is 10, so after 7 updates (7 seconds), period_count should be 3
        # After 8 updates (8 seconds), period_count should be 2, which triggers 'Thinking'
        tsm.update(8000)  # After 8 seconds, should transition to 'Thinking'
        
        text = tsm.get_current_text()
        assert text == "Thinking"
    
    def test_thinking_state_text_generation(self):
        """Test that thinking state generates text with varying dots."""
        tsm = TextStateManager()
        tsm.set_state(TextStateManager.DisplayState.THINKING)
        
        # Initial state should have 0 dots (period_count starts at 0)
        # But since update hasn't been called yet, text is empty
        text = tsm.get_current_text()
        assert text == ""  # Initial state before first update
        
        # After 500ms, should have 1 dot
        tsm.update(500)
        text = tsm.get_current_text()
        assert text == "Thinking."
        
        # After 1000ms, should have 2 dots
        tsm.update(1000)
        text = tsm.get_current_text()
        assert text == "Thinking.."
        
        # After 1500ms, should have 3 dots
        tsm.update(1500)
        text = tsm.get_current_text()
        assert text == "Thinking..."
        
        # After 2000ms, should cycle back to 0 dots
        tsm.update(2000)
        text = tsm.get_current_text()
        assert text == "Thinking"
        
        # After 2500ms, should have 1 dot again
        tsm.update(2500)
        text = tsm.get_current_text()
        assert text == "Thinking."
        
        # After 3000ms, should have 2 dots again
        tsm.update(3000)
        text = tsm.get_current_text()
        assert text == "Thinking.."
        
        # After 3500ms, should have 3 dots again
        tsm.update(3500)
        text = tsm.get_current_text()
        assert text == "Thinking..."
        
        # After 4000ms, should cycle back to 0 dots
        tsm.update(4000)
        text = tsm.get_current_text()
        assert text == "Thinking"
        
        # After 4500ms, should have 1 dot again
        tsm.update(4500)
        text = tsm.get_current_text()
        assert text == "Thinking."
        
        # After 5000ms, should have 2 dots again
        tsm.update(5000)
        text = tsm.get_current_text()
        assert text == "Thinking.."
        
        # After 5500ms, should have 3 dots again
        tsm.update(5500)
        text = tsm.get_current_text()
        assert text == "Thinking..."
        
        # After 6000ms, should cycle back to 0 dots
        tsm.update(6000)
        text = tsm.get_current_text()
        assert text == "Thinking"
        
        # After 6500ms, should have 1 dot again
        tsm.update(6500)
        text = tsm.get_current_text()
        assert text == "Thinking."
        
        # After 7000ms, should have 2 dots again
        tsm.update(7000)
        text = tsm.get_current_text()
        assert text == "Thinking.."
        
        # After 7500ms, should have 3 dots again
        tsm.update(7500)
        text = tsm.get_current_text()
        assert text == "Thinking..."
        
        # After 8000ms, should cycle back to 0 dots
        tsm.update(8000)
        text = tsm.get_current_text()
        assert text == "Thinking"
        
        # After 8500ms, should have 1 dot again
        tsm.update(8500)
        text = tsm.get_current_text()
        assert text == "Thinking."
        
        # After 9000ms, should have 2 dots again
        tsm.update(9000)
        text = tsm.get_current_text()
        assert text == "Thinking.."
        
        # After 9500ms, should have 3 dots again
        tsm.update(9500)
        text = tsm.get_current_text()
        assert text == "Thinking..."
        
        # After 10000ms, should cycle back to 0 dots
        tsm.update(10000)
        text = tsm.get_current_text()
        assert text == "Thinking"
    
    def test_response_state_text(self):
        """Test that RESPONSE state returns the response text."""
        tsm = TextStateManager()
        response = "The answer is 42"
        tsm.set_state(TextStateManager.DisplayState.RESPONSE, response)
        
        text = tsm.get_current_text()
        assert text == response
    
    def test_response_state_auto_transition_to_idle(self):
        """Test that RESPONSE state transitions to IDLE after 5 seconds."""
        tsm = TextStateManager()
        tsm.set_state(TextStateManager.DisplayState.RESPONSE, "Test response")
        
        # Before 5 seconds, should still be in RESPONSE state
        tsm.update(4000)
        assert tsm.get_state() == TextStateManager.DisplayState.RESPONSE
        
        # After 5 seconds, should transition to IDLE
        tsm.update(5001)
        assert tsm.get_state() == TextStateManager.DisplayState.IDLE
    
    def test_state_transition_from_recording_to_thinking(self):
        """Test state transitions between different states."""
        tsm = TextStateManager()
        
        tsm.set_state(TextStateManager.DisplayState.RECORDING)
        assert tsm.get_state() == TextStateManager.DisplayState.RECORDING
        
        tsm.set_state(TextStateManager.DisplayState.THINKING)
        assert tsm.get_state() == TextStateManager.DisplayState.THINKING
        
        tsm.set_state(TextStateManager.DisplayState.RESPONSE, "Answer")
        assert tsm.get_state() == TextStateManager.DisplayState.RESPONSE
    
    def test_period_count_reset_on_state_change(self):
        """Test that period_count is reset when changing states."""
        tsm = TextStateManager()
        tsm.set_state(TextStateManager.DisplayState.RECORDING)
        
        # Simulate some time passing
        tsm.update(5000)
        
        # Change to another state
        tsm.set_state(TextStateManager.DisplayState.THINKING)
        
        # Period count should be reset
        # After 500ms, should have 1 dot
        tsm.update(500)
        text = tsm.get_current_text()
        assert text == "Thinking."  # Should have 1 dot initially


class TestAnimationManager:
    """Tests for AnimationManager class."""
    
    def test_initial_position_centered(self):
        """Test that triangle starts centered on screen."""
        am = AnimationManager(240, 240)
        expected_x = (240 - 120) // 2
        expected_y = (240 - 120) // 2
        assert am.current_x == expected_x
        assert am.current_y == expected_y
    
    def test_move_to_center(self):
        """Test that move_to_center sets target position."""
        am = AnimationManager(240, 240)
        am.move_to_center()
        assert am.target_x == 120
        assert am.target_y == 40
        assert am.is_transitioning_to_center is True
    
    def test_idle_motion_updates_position(self):
        """Test that idle motion updates target position."""
        am = AnimationManager(240, 240)
        initial_target_x = am.target_x
        initial_target_y = am.target_y
        
        am.update_idle_motion()
        
        # Position should change due to idle motion
        assert am.target_x != initial_target_x or am.target_y != initial_target_y
    
    def test_gyro_input_affects_position(self):
        """Test that gyro input affects triangle position."""
        am = AnimationManager(240, 240)
        initial_x = am.current_x
        initial_y = am.current_y
        
        # Apply gyro input
        am.update_triangle_position(0.5, 0.5)
        
        # Position should change
        assert am.current_x != initial_x or am.current_y != initial_y
    
    def test_still_gyro_triggers_idle_motion(self):
        """Test that still gyro readings trigger idle motion."""
        am = AnimationManager(240, 240)
        initial_target_x = am.target_x
        
        # Apply still gyro readings
        am.update_triangle_position(0.1, 0.1)
        
        # Should trigger idle motion
        assert am.target_x != initial_target_x
    
    def test_shaking_mode_blocks_position_update(self):
        """Test that shaking mode blocks position updates."""
        am = AnimationManager(240, 240)
        am.set_shaking(True)
        
        initial_x = am.current_x
        initial_y = am.current_y
        
        # Apply gyro input while shaking
        am.update_triangle_position(1.0, 1.0)
        
        # Position should not change
        assert am.current_x == initial_x
        assert am.current_y == initial_y
    
    def test_shaking_resets_velocity(self):
        """Test that stopping shaking resets velocity."""
        am = AnimationManager(240, 240)
        am.set_shaking(True)
        am.velocity_x = 10
        am.velocity_y = 10
        
        am.set_shaking(False)
        
        assert am.velocity_x == 0
        assert am.velocity_y == 0
    
    def test_position_constrained_to_screen(self):
        """Test that position is constrained within screen bounds."""
        am = AnimationManager(240, 240)
        
        # Set target position far outside screen
        am.target_x = 1000
        am.target_y = 1000
        
        am.constrain_position()
        
        # Position should be constrained
        assert 0 <= am.target_x <= 240
        assert 0 <= am.target_y <= 240
    
    def test_transitioning_to_center_blocks_gyro(self):
        """Test that transitioning to center blocks gyro updates."""
        am = AnimationManager(240, 240)
        am.move_to_center()
        
        initial_x = am.current_x
        initial_y = am.current_y
        
        # Apply gyro input while transitioning
        am.update_triangle_position(1.0, 1.0)
        
        # Position should not change
        assert am.current_x == initial_x
        assert am.current_y == initial_y
    
    def test_velocity_smoothing(self):
        """Test that velocity is smoothed over time."""
        am = AnimationManager(240, 240)
        
        # Apply multiple gyro inputs
        for i in range(10):
            am.update_triangle_position(0.1, 0.1)
        
        # Velocity should be smoothed, not jumping to full value
        # The smoothing factor is 0.8, so velocity should be less than raw input
        assert 0 < abs(am.velocity_x) < 50
        assert 0 < abs(am.velocity_y) < 50


class TestArduinoHelpers:
    """Tests for Arduino helper functions."""
    
    def test_arduino_map_basic(self):
        """Test basic value mapping."""
        result = arduino_map(512, 0, 1023, 0, 100)
        assert abs(result - 50) < 0.1
    
    def test_arduino_map_edge_cases(self):
        """Test mapping at boundaries."""
        assert arduino_map(0, 0, 1023, 0, 100) == 0
        assert arduino_map(1023, 0, 1023, 0, 100) == 100
    
    def test_arduino_constrain_basic(self):
        """Test basic constraining."""
        assert arduino_constrain(50, 0, 100) == 50
        assert arduino_constrain(-10, 0, 100) == 0
        assert arduino_constrain(110, 0, 100) == 100
    
    def test_arduino_constrain_edge_cases(self):
        """Test constraining at exact boundaries."""
        assert arduino_constrain(0, 0, 100) == 0
        assert arduino_constrain(100, 0, 100) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

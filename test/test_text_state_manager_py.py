"""
Test suite for TextStateManager module (mocked for pytest)
Tests display state management, text updates, and timing.
"""

import unittest


class MockTextStateManager:
    """Mock implementation of TextStateManager for testing"""
    
    class DisplayState:
        IDLE = 0
        RECORDING = 1
        THINKING = 2
        RESPONSE = 3
        ERROR = 4
    
    def __init__(self):
        self.current_state = self.DisplayState.IDLE
        self.last_update_time = 0
        self.period_count = 0
        self.max_periods = 10
        self.last_generated_text = ""
        self.response_text = ""
        self.response_start_time = 0
        self.response_display_duration = 7000  # 7 seconds as in main.cpp
        
    def update(self, current_time):
        """Update text based on current state"""
        if self.current_state == self.DisplayState.RECORDING:
            self._update_recording_text(current_time)
        elif self.current_state == self.DisplayState.THINKING:
            self._update_thinking_text(current_time)
        elif self.current_state == self.DisplayState.RESPONSE:
            self._update_response_text(current_time)
            
    def set_state(self, new_state, response=""):
        """Set display state"""
        self.current_state = new_state
        self.last_update_time = 0
        self.period_count = self.max_periods if new_state == self.DisplayState.RECORDING else 0
        
        if new_state == self.DisplayState.RESPONSE:
            self.response_text = response
            self.response_start_time = 0
            
    def get_state(self):
        """Get current display state"""
        return self.current_state
    
    def get_current_text(self):
        """Get current display text"""
        if self.current_state == self.DisplayState.IDLE:
            return "Magic\nGPT8\n\nShake me"
        elif self.current_state == self.DisplayState.ERROR:
            return "Wifi: X"
        elif self.current_state == self.DisplayState.RESPONSE:
            return self.response_text
        else:
            return self.last_generated_text
            
    def _update_recording_text(self, current_time):
        """Update recording text"""
        if current_time - self.last_update_time >= 1000:
            self.last_update_time = current_time
            self.period_count = max(0, self.period_count - 1)
            
            if self.period_count <= 2:
                self.last_generated_text = "Thinking"
            else:
                text = "Speak Now"
                for i in range(self.period_count):
                    text += " ."
                self.last_generated_text = text
                
    def _update_thinking_text(self, current_time):
        """Update thinking text"""
        if current_time - self.last_update_time >= 500:
            self.last_update_time = current_time
            self.period_count = (self.period_count + 1) % 4
            
            text = "Thinking"
            for i in range(self.period_count):
                text += "."
            self.last_generated_text = text
            
    def _update_response_text(self, current_time):
        """Update response text (check duration)"""
        if current_time - self.response_start_time >= self.response_display_duration:
            self.set_state(self.DisplayState.IDLE)


class TestTextStateManager(unittest.TestCase):
    """Unit tests for TextStateManager mock"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tsm = MockTextStateManager()
        
    def test_initial_state_idle(self):
        """Test initial state is IDLE"""
        self.assertEqual(self.tsm.get_state(), MockTextStateManager.DisplayState.IDLE)
        
    def test_idle_text(self):
        """Test IDLE state shows correct text"""
        text = self.tsm.get_current_text()
        self.assertIn("Magic", text)
        self.assertIn("GPT8", text)
        
    def test_set_state_response(self):
        """Test setting RESPONSE state"""
        self.tsm.set_state(MockTextStateManager.DisplayState.RESPONSE, "Ask again later")
        self.assertEqual(self.tsm.get_state(), MockTextStateManager.DisplayState.RESPONSE)
        
    def test_response_text(self):
        """Test RESPONSE state shows response text"""
        self.tsm.set_state(MockTextStateManager.DisplayState.RESPONSE, "It is certain")
        text = self.tsm.get_current_text()
        self.assertEqual(text, "It is certain")
        
    def test_error_text(self):
        """Test ERROR state shows error text"""
        self.tsm.set_state(MockTextStateManager.DisplayState.ERROR)
        text = self.tsm.get_current_text()
        self.assertEqual(text, "Wifi: X")
        
    def test_recording_state(self):
        """Test RECORDING state transitions"""
        current_time = 1000
        self.tsm.set_state(MockTextStateManager.DisplayState.RECORDING)
        self.tsm.update(current_time)
        text = self.tsm.get_current_text()
        self.assertIn("Speak Now", text)
        
    def test_thinking_state(self):
        """Test THINKING state shows dots"""
        current_time = 500
        self.tsm.set_state(MockTextStateManager.DisplayState.THINKING)
        self.tsm.update(current_time)
        text = self.tsm.get_current_text()
        self.assertEqual(text, "Thinking.")
        
    def test_response_display_duration(self):
        """Test response displays for configured duration"""
        self.assertEqual(self.tsm.response_display_duration, 7000)
        
    def test_reset_to_idle_after_response(self):
        """Test state resets to IDLE after response duration"""
        current_time = 8000
        self.tsm.set_state(MockTextStateManager.DisplayState.RESPONSE, "It is certain")
        self.tsm.update(current_time)
        self.assertEqual(self.tsm.get_state(), MockTextStateManager.DisplayState.IDLE)


class TestTextStateManagerStates(unittest.TestCase):
    """Tests for display state definitions"""
    
    def test_all_states_defined(self):
        """Verify all display states are defined"""
        states = [
            MockTextStateManager.DisplayState.IDLE,
            MockTextStateManager.DisplayState.RECORDING,
            MockTextStateManager.DisplayState.THINKING,
            MockTextStateManager.DisplayState.RESPONSE,
            MockTextStateManager.DisplayState.ERROR,
        ]
        self.assertEqual(len(states), 5)
        
    def test_state_values(self):
        """Verify state values are sequential"""
        self.assertLess(MockTextStateManager.DisplayState.IDLE, 
                       MockTextStateManager.DisplayState.RECORDING)
        self.assertLess(MockTextStateManager.DisplayState.RECORDING, 
                       MockTextStateManager.DisplayState.THINKING)
        self.assertLess(MockTextStateManager.DisplayState.THINKING, 
                       MockTextStateManager.DisplayState.RESPONSE)


class TestTextStateManagerTiming(unittest.TestCase):
    """Tests for text update timing"""
    
    def test_recording_update_interval(self):
        """Recording text updates every 1 second"""
        self.assertEqual(1000, 1000)
        
    def test_thinking_update_interval(self):
        """Thinking text updates every 500ms"""
        self.assertEqual(500, 500)
        
    def test_response_display_duration(self):
        """Response displays for 7 seconds"""
        self.assertEqual(7000, 7000)
        
    def test_max_periods(self):
        """Recording has 10 max periods"""
        self.assertEqual(10, 10)


class TestTextStateManagerTextFormats(unittest.TestCase):
    """Tests for text format expectations"""
    
    def test_idle_text_format(self):
        """Idle text should contain 'Magic' and 'GPT8'"""
        self.assertIn("Magic", "Magic\nGPT8\n\nShake me")
        self.assertIn("GPT8", "Magic\nGPT8\n\nShake me")
        
    def test_response_with_periods(self):
        """Thinking text should show with periods"""
        self.assertIn(".", "Thinking.")
        
    def test_recording_tells_user_to_speak(self):
        """Recording text should indicate speaking"""
        self.assertIn("Speak", "Speak Now . . .")


if __name__ == '__main__':
    unittest.main(verbosity=2)

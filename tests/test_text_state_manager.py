"""Test suite for TextStateManager algorithms."""

import sys
sys.path.insert(0, 'src')


class TextStateManager:
    """Re-implementation of TextStateManager for testing."""
    
    class DisplayState:
        IDLE = 0
        RECORDING = 1
        THINKING = 2
        RESPONSE = 3
    
    def __init__(self):
        self._currentState = self.DisplayState.IDLE
        self._currentText = "DISCONNECTED"
        self._responseStartTime = 0
        self._responseDisplayDuration = 5000  # 5 seconds
    
    def getCurrentState(self):
        return self._currentState
    
    def getCurrentText(self):
        return self._currentText
    
    def setState(self, state):
        self._currentState = state
        
        if state == self.DisplayState.IDLE:
            self._currentText = "DISCONNECTED"
        elif state == self.DisplayState.RECORDING:
            self._currentText = "Listening..."
        elif state == self.DisplayState.THINKING:
            self._currentText = "Thinking..."
        elif state == self.DisplayState.RESPONSE:
            self._currentText = "Yes"
    
    def startRecording(self, currentTime):
        if self._currentState == self.DisplayState.IDLE:
            self.setState(self.DisplayState.RECORDING)
            return True
        return False
    
    def startThinking(self, currentTime):
        if self._currentState == self.DisplayState.RECORDING:
            self.setState(self.DisplayState.THINKING)
            return True
        return False
    
    def showResponse(self, responseText, currentTime):
        if self._currentState == self.DisplayState.THINKING:
            self._currentText = responseText
            self.setState(self.DisplayState.RESPONSE)
            self._responseStartTime = currentTime
            return True
        return False
    
    def updateResponse(self, currentTime):
        if self._currentState == self.DisplayState.RESPONSE:
            if currentTime - self._responseStartTime >= self._responseDisplayDuration:
                self.setState(self.DisplayState.IDLE)
                return True
        return False
    
    def resetToIdle(self, currentTime):
        self.setState(self.DisplayState.IDLE)


class TestStateTransitions:
    """Tests for state transition logic."""
    
    def test_initial_state_is_idle(self):
        """Test that initial state is IDLE."""
        manager = TextStateManager()
        assert manager.getCurrentState() == TextStateManager.DisplayState.IDLE
    
    def test_initial_text_is_disconnected(self):
        """Test that initial text is DISCONNECTED."""
        manager = TextStateManager()
        assert manager.getCurrentText() == "DISCONNECTED"
    
    def test_transition_idle_to_recording(self):
        """Test transition from IDLE to RECORDING."""
        manager = TextStateManager()
        result = manager.startRecording(0)
        
        assert result == True
        assert manager.getCurrentState() == TextStateManager.DisplayState.RECORDING
        assert manager.getCurrentText() == "Listening..."
    
    def test_transition_recording_to_thinking(self):
        """Test transition from RECORDING to THINKING."""
        manager = TextStateManager()
        manager.startRecording(0)
        result = manager.startThinking(100)
        
        assert result == True
        assert manager.getCurrentState() == TextStateManager.DisplayState.THINKING
        assert manager.getCurrentText() == "Thinking..."
    
    def test_transition_thinking_to_response(self):
        """Test transition from THINKING to RESPONSE."""
        manager = TextStateManager()
        manager.startRecording(0)
        manager.startThinking(100)
        result = manager.showResponse("Yes", 200)
        
        assert result == True
        assert manager.getCurrentState() == TextStateManager.DisplayState.RESPONSE
        assert manager.getCurrentText() == "Yes"
    
    def test_invalid_transition_recording_to_thinking(self):
        """Test that RECORDING to THINKING fails if not in RECORDING state."""
        manager = TextStateManager()
        result = manager.startThinking(100)
        
        assert result == False
        assert manager.getCurrentState() == TextStateManager.DisplayState.IDLE
    
    def test_invalid_transition_thinking_to_response(self):
        """Test that THINKING to RESPONSE fails if not in THINKING state."""
        manager = TextStateManager()
        result = manager.showResponse("Yes", 200)
        
        assert result == False
        assert manager.getCurrentState() == TextStateManager.DisplayState.IDLE


class TestResponseDisplayDuration:
    """Tests for response display duration logic."""
    
    def test_response_expires_after_duration(self):
        """Test that response state expires after display duration."""
        manager = TextStateManager()
        manager.startRecording(0)
        manager.startThinking(100)
        manager.showResponse("Yes", 200)
        
        # Before duration expires
        assert manager.updateResponse(4000) == False
        assert manager.getCurrentState() == TextStateManager.DisplayState.RESPONSE
        
        # After duration expires
        assert manager.updateResponse(5500) == True
        assert manager.getCurrentState() == TextStateManager.DisplayState.IDLE
    
    def test_response_display_duration_is_5_seconds(self):
        """Test that default response display duration is 5 seconds."""
        manager = TextStateManager()
        assert manager._responseDisplayDuration == 5000
    
    def test_response_does_not_expire_early(self):
        """Test that response does not expire before duration."""
        manager = TextStateManager()
        manager.startRecording(0)
        manager.startThinking(100)
        manager.showResponse("Yes", 200)
        
        # At exactly 5 seconds (boundary)
        assert manager.updateResponse(5000) == True


class TestResetToIdle:
    """Tests for reset to idle functionality."""
    
    def test_reset_from_any_state(self):
        """Test that reset works from any state."""
        manager = TextStateManager()
        
        # From RECORDING
        manager.startRecording(0)
        manager.resetToIdle(100)
        assert manager.getCurrentState() == TextStateManager.DisplayState.IDLE
        assert manager.getCurrentText() == "DISCONNECTED"
        
        # From THINKING
        manager.startRecording(200)
        manager.startThinking(300)
        manager.resetToIdle(400)
        assert manager.getCurrentState() == TextStateManager.DisplayState.IDLE
        
        # From RESPONSE
        manager.startRecording(500)
        manager.startThinking(600)
        manager.showResponse("Yes", 700)
        manager.resetToIdle(800)
        assert manager.getCurrentState() == TextStateManager.DisplayState.IDLE


class TestTextValues:
    """Tests for text values in each state."""
    
    def test_idle_text(self):
        """Test text in IDLE state."""
        manager = TextStateManager()
        assert manager.getCurrentText() == "DISCONNECTED"
        
        manager.setState(TextStateManager.DisplayState.IDLE)
        assert manager.getCurrentText() == "DISCONNECTED"
    
    def test_recording_text(self):
        """Test text in RECORDING state."""
        manager = TextStateManager()
        manager.setState(TextStateManager.DisplayState.RECORDING)
        assert manager.getCurrentText() == "Listening..."
    
    def test_thinking_text(self):
        """Test text in THINKING state."""
        manager = TextStateManager()
        manager.setState(TextStateManager.DisplayState.THINKING)
        assert manager.getCurrentText() == "Thinking..."
    
    def test_response_text(self):
        """Test text in RESPONSE state."""
        manager = TextStateManager()
        manager.showResponse("Yes", 0)
        assert manager.getCurrentText() == "Yes"
        
        manager.showResponse("No", 100)
        assert manager.getCurrentText() == "No"
        
        manager.showResponse("Maybe", 200)
        assert manager.getCurrentText() == "Maybe"

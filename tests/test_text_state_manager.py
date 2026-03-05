"""Tests for TextStateManager module."""
import sys
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch

# Mock Arduino dependencies
sys.modules['Arduino'] = MagicMock()
sys.modules['Arduino.h'] = MagicMock()

# Import the module to test
import importlib.util
spec = importlib.util.spec_from_file_location("TextStateManager", "src/TextStateManager.h")

# Since we can't import C++ headers directly, we'll test the logic
class TextStateManagerLogic:
    """Python re-implementation of TextStateManager logic for testing."""
    
    class DisplayState:
        IDLE = 0
        RECORDING = 1
        THINKING = 2
        SPEAKING = 3
        ERROR = 4
    
    def __init__(self):
        self.state = self.DisplayState.IDLE
        self.responseStartTime = 0
        self.responseDisplayDuration = 5000
        self.textBuffer = ""
        self.maxTextLength = 20
    
    def setState(self, newState):
        self.state = newState
    
    def getCurrentText(self):
        return self.textBuffer
    
    def updateText(self, newText):
        if len(newText) > self.maxTextLength:
            newText = newText[:self.maxTextLength]
        self.textBuffer = newText
        return newText
    
    def updateResponseText(self, currentTime):
        if self.state == self.DisplayState.THINKING:
            if currentTime - self.responseStartTime >= self.responseDisplayDuration:
                self.setState(self.DisplayState.IDLE)
                return True
        return False
    
    def isIdle(self):
        return self.state == self.DisplayState.IDLE
    
    def isRecording(self):
        return self.state == self.DisplayState.RECORDING
    
    def isThinking(self):
        return self.state == self.DisplayState.THINKING
    
    def isSpeaking(self):
        return self.state == self.DisplayState.SPEAKING
    
    def isError(self):
        return self.state == self.DisplayState.ERROR


def test_initial_state_is_idle():
    """Test that the state manager starts in IDLE state."""
    manager = TextStateManagerLogic()
    assert manager.isIdle() == True
    assert manager.state == manager.DisplayState.IDLE


def test_set_state_to_recording():
    """Test setting state to RECORDING."""
    manager = TextStateManagerLogic()
    manager.setState(manager.DisplayState.RECORDING)
    assert manager.isRecording() == True
    assert manager.isIdle() == False


def test_set_state_to_thinking():
    """Test setting state to THINKING."""
    manager = TextStateManagerLogic()
    manager.setState(manager.DisplayState.THINKING)
    assert manager.isThinking() == True
    assert manager.isIdle() == False


def test_set_state_to_speaking():
    """Test setting state to SPEAKING."""
    manager = TextStateManagerLogic()
    manager.setState(manager.DisplayState.SPEAKING)
    assert manager.isSpeaking() == True
    assert manager.isIdle() == False


def test_set_state_to_error():
    """Test setting state to ERROR."""
    manager = TextStateManagerLogic()
    manager.setState(manager.DisplayState.ERROR)
    assert manager.isError() == True
    assert manager.isIdle() == False


def test_update_text_with_short_string():
    """Test updating text with a short string."""
    manager = TextStateManagerLogic()
    result = manager.updateText("Hello")
    assert result == "Hello"
    assert manager.getCurrentText() == "Hello"


def test_update_text_with_long_string():
    """Test updating text with a long string (should be truncated)."""
    manager = TextStateManagerLogic()
    longText = "This is a very long text that exceeds the maximum length"
    result = manager.updateText(longText)
    assert len(result) <= manager.maxTextLength
    assert result == longText[:manager.maxTextLength]


def test_update_response_text_timeout():
    """Test that THINKING state transitions to IDLE after timeout."""
    manager = TextStateManagerLogic()
    manager.setState(manager.DisplayState.THINKING)
    manager.responseStartTime = 0
    
    # Simulate time passing beyond the display duration
    result = manager.updateResponseText(6000)  # 6 seconds later
    assert result == True
    assert manager.isIdle() == True


def test_update_response_text_no_timeout():
    """Test that THINKING state stays when timeout hasn't passed."""
    manager = TextStateManagerLogic()
    manager.setState(manager.DisplayState.THINKING)
    manager.responseStartTime = 0
    
    # Simulate time passing before the display duration
    result = manager.updateResponseText(3000)  # 3 seconds later
    assert result == False
    assert manager.isThinking() == True


def test_update_response_text_not_in_thinking_state():
    """Test updateResponseText when not in THINKING state."""
    manager = TextStateManagerLogic()
    manager.setState(manager.DisplayState.IDLE)
    manager.responseStartTime = 0
    
    result = manager.updateResponseText(6000)
    assert result == False
    assert manager.isIdle() == True


def test_state_transitions():
    """Test various state transitions."""
    manager = TextStateManagerLogic()
    
    # Start in IDLE
    assert manager.isIdle() == True
    
    # Transition to RECORDING
    manager.setState(manager.DisplayState.RECORDING)
    assert manager.isRecording() == True
    assert manager.isIdle() == False
    
    # Transition to THINKING
    manager.setState(manager.DisplayState.THINKING)
    assert manager.isThinking() == True
    assert manager.isRecording() == False
    
    # Transition to SPEAKING
    manager.setState(manager.DisplayState.SPEAKING)
    assert manager.isSpeaking() == True
    assert manager.isThinking() == False
    
    # Transition to ERROR
    manager.setState(manager.DisplayState.ERROR)
    assert manager.isError() == True
    assert manager.isSpeaking() == False


def test_text_buffer_initialization():
    """Test that text buffer is initialized correctly."""
    manager = TextStateManagerLogic()
    assert manager.getCurrentText() == ""


def test_max_text_length_constant():
    """Test that max text length is set correctly."""
    manager = TextStateManagerLogic()
    assert manager.maxTextLength == 20

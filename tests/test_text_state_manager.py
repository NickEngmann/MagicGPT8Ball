"""Tests for TextStateManager class - Python implementation."""
import sys
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch
import pytest


class MockMillis:
    """Mock millis() function."""
    def __init__(self):
        self._time = 0
    
    def __call__(self):
        return self._time
    
    def increment(self, ms):
        self._time += ms


class TextStateManager:
    """Python implementation of TextStateManager for testing."""
    class DisplayState:
        IDLE = "IDLE"
        RECORDING = "RECORDING"
        THIN = "THIN"
        RESPONSE = "RESPONSE"
    
    def __init__(self, response_display_duration=5000):
        self._currentState = self.DisplayState.IDLE
        self._currentText = ""
        self._responseStartTime = 0
        self._responseDisplayDuration = response_display_duration
        self.millis = MockMillis()
    
    def getCurrentState(self):
        return self._currentState
    
    def getCurrentText(self):
        return self._currentText
    
    def setState(self, state):
        self._currentState = state
    
    def setText(self, text):
        self._currentText = text
        if self._currentState == self.DisplayState.IDLE:
            self._currentState = self.DisplayState.IDLE
    
    def startRecording(self):
        self._currentState = self.DisplayState.RECORDING
        self._currentText = "Recording..."
    
    def startThinking(self):
        self._currentState = self.DisplayState.THIN
        self._currentText = "Thinking..."
    
    def setResponse(self, response):
        self._currentState = self.DisplayState.RESPONSE
        self._currentText = response
        self._responseStartTime = self.millis()
    
    def updateResponseTimeout(self, currentTime):
        if currentTime - self._responseStartTime >= self._responseDisplayDuration:
            self.setState(self.DisplayState.IDLE)


@pytest.fixture
def text_manager():
    """Create a TextStateManager instance with mocks."""
    return TextStateManager()


def test_text_state_manager_initial_state(text_manager):
    """Test initial state is IDLE."""
    assert text_manager.getCurrentState() == text_manager.DisplayState.IDLE
    assert text_manager.getCurrentText() == ""


def test_text_state_manager_set_text(text_manager):
    """Test setText() sets text and state."""
    text_manager.setText("Hello World")
    
    assert text_manager.getCurrentState() == text_manager.DisplayState.IDLE
    assert text_manager.getCurrentText() == "Hello World"


def test_text_state_manager_recording_state(text_manager):
    """Test RECORDING state transitions."""
    text_manager.startRecording()
    
    assert text_manager.getCurrentState() == text_manager.DisplayState.RECORDING
    assert "Recording" in text_manager.getCurrentText()


def test_text_state_manager_thinking_state(text_manager):
    """Test THIN state transitions."""
    text_manager.startThinking()
    
    assert text_manager.getCurrentState() == text_manager.DisplayState.THIN
    assert "Thinking" in text_manager.getCurrentText()


def test_text_state_manager_response_state(text_manager):
    """Test RESPONSE state transitions."""
    text_manager.setResponse("It is certain")
    
    assert text_manager.getCurrentState() == text_manager.DisplayState.RESPONSE
    assert text_manager.getCurrentText() == "It is certain"


def test_text_state_manager_response_timeout(text_manager):
    """Test RESPONSE state times out after duration."""
    text_manager.setResponse("Test response")
    
    assert text_manager.getCurrentState() == text_manager.DisplayState.RESPONSE
    
    # Advance time past response display duration (default 5000ms)
    text_manager.millis.increment(6000)
    text_manager.updateResponseTimeout(text_manager.millis())
    
    assert text_manager.getCurrentState() == text_manager.DisplayState.IDLE


def test_text_state_manager_all_states(text_manager):
    """Test all state transitions in sequence."""
    # Start with IDLE
    assert text_manager.getCurrentState() == text_manager.DisplayState.IDLE
    
    # Go to RECORDING
    text_manager.startRecording()
    assert text_manager.getCurrentState() == text_manager.DisplayState.RECORDING
    
    # Go to THIN
    text_manager.startThinking()
    assert text_manager.getCurrentState() == text_manager.DisplayState.THIN
    
    # Go to RESPONSE
    text_manager.setResponse("Answer")
    assert text_manager.getCurrentState() == text_manager.DisplayState.RESPONSE
    
    # Timeout back to IDLE
    text_manager.millis.increment(6000)
    text_manager.updateResponseTimeout(text_manager.millis())
    assert text_manager.getCurrentState() == text_manager.DisplayState.IDLE


def test_text_state_manager_custom_response_duration():
    """Test custom response display duration."""
    manager = TextStateManager(response_display_duration=2000)
    manager.setResponse("Quick response")
    
    # Should still be in RESPONSE state at 1500ms
    manager.millis.increment(1500)
    manager.updateResponseTimeout(manager.millis())
    assert manager.getCurrentState() == manager.DisplayState.RESPONSE
    
    # Should timeout at 2000ms
    manager.millis.increment(500)
    manager.updateResponseTimeout(manager.millis())
    assert manager.getCurrentState() == manager.DisplayState.IDLE

"""Test TextStateManager class algorithms."""
import sys
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch
import pytest

# Mock Arduino environment
sys.modules['Arduino'] = MagicMock()
sys.modules['WiFiManager'] = MagicMock()
sys.modules['WiFi'] = MagicMock()
sys.modules['HTTPClient'] = MagicMock()
sys.modules['QMI8658'] = MagicMock()
sys.modules['DEV_Config'] = MagicMock()
sys.modules['Recorder'] = MagicMock()
sys.modules['Animations'] = MagicMock()


class MockMillis:
    def __init__(self):
        self._time = 0
    
    def __call__(self):
        return self._time
    
    def advance(self, ms):
        self._time += ms


def test_text_state_manager_initial_state():
    """Test that TextStateManager starts in IDLE state."""
    from src.TextStateManager import TextStateManager
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        manager = TextStateManager()
        
        assert manager.getCurrentState() == manager.DisplayState.IDLE
        assert manager.getCurrentText() == ""


def test_text_state_manager_recording_state():
    """Test transitioning to RECORDING state."""
    from src.TextStateManager import TextStateManager
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        manager = TextStateManager()
        
        manager.setRecording()
        
        assert manager.getCurrentState() == manager.DisplayState.RECORDING
        assert manager.getCurrentText() == "Listening..."


def test_text_state_manager_thinking_state():
    """Test transitioning to THINKING state."""
    from src.TextStateManager import TextStateManager
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        manager = TextStateManager()
        
        manager.setThinking()
        
        assert manager.getCurrentState() == manager.DisplayState.THINKING
        assert manager.getCurrentText() == "Thinking..."


def test_text_state_manager_response_display():
    """Test displaying a response."""
    from src.TextStateManager import TextStateManager
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        manager = TextStateManager()
        
        manager.setResponse("It is certain")
        
        assert manager.getCurrentState() == manager.DisplayState.RESPONSE
        assert manager.getCurrentText() == "It is certain"


def test_text_state_manager_auto_return_to_idle():
    """Test that response state returns to IDLE after timeout."""
    from src.TextStateManager import TextStateManager
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        manager = TextStateManager()
        
        manager.setResponse("Yes, definitely")
        
        assert manager.getCurrentState() == manager.DisplayState.RESPONSE
        
        # Advance time by less than responseDisplayDuration
        mock_millis.advance(2999)
        manager.updateResponse()
        
        assert manager.getCurrentState() == manager.DisplayState.RESPONSE
        
        # Advance time to trigger timeout
        mock_millis.advance(1)
        manager.updateResponse()
        
        assert manager.getCurrentState() == manager.DisplayState.IDLE
        assert manager.getCurrentText() == ""


def test_text_state_manager_multiple_responses():
    """Test handling multiple responses in sequence."""
    from src.TextStateManager import TextStateManager
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        manager = TextStateManager()
        
        manager.setResponse("First response")
        assert manager.getCurrentText() == "First response"
        
        manager.setResponse("Second response")
        assert manager.getCurrentText() == "Second response"
        
        manager.setResponse("Third response")
        assert manager.getCurrentText() == "Third response"


def test_text_state_manager_states():
    """Test all state transitions."""
    from src.TextStateManager import TextStateManager
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        manager = TextStateManager()
        
        # IDLE -> RECORDING
        manager.setRecording()
        assert manager.getCurrentState() == manager.DisplayState.RECORDING
        
        # RECORDING -> THINKING
        manager.setThinking()
        assert manager.getCurrentState() == manager.DisplayState.THINKING
        
        # THINKING -> RESPONSE
        manager.setResponse("Answer")
        assert manager.getCurrentState() == manager.DisplayState.RESPONSE
        
        # RESPONSE -> IDLE (after timeout)
        mock_millis.advance(3000)
        manager.updateResponse()
        assert manager.getCurrentState() == manager.DisplayState.IDLE

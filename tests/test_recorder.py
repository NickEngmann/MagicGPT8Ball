"""Test Recorder class algorithms."""
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
sys.modules['Animations'] = MagicMock()
sys.modules['TextStateManager'] = MagicMock()
sys.modules['VibrationManager'] = MagicMock()


class MockMillis:
    def __init__(self):
        self._time = 0
    
    def __call__(self):
        return self._time
    
    def advance(self, ms):
        self._time += ms


def test_recorder_initial_state():
    """Test that Recorder starts in idle state."""
    from src.Recorder import Recorder
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        with patch('pinMode'):
            with patch('analogRead', return_value=0):
                recorder = Recorder()
                
                assert not recorder.isRecording()
                assert recorder.getRecordingTime() == 0


def test_recorder_start_stop():
    """Test starting and stopping recording."""
    from src.Recorder import Recorder
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        with patch('pinMode'):
            with patch('analogRead', return_value=0):
                recorder = Recorder()
                
                # Start recording
                recorder.startRecording()
                assert recorder.isRecording()
                
                # Advance time
                mock_millis.advance(1000)
                assert recorder.getRecordingTime() == 1000
                
                # Stop recording
                recorder.stopRecording()
                assert not recorder.isRecording()


def test_recorder_max_duration():
    """Test recording duration limit."""
    from src.Recorder import Recorder
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        with patch('pinMode'):
            with patch('analogRead', return_value=0):
                recorder = Recorder()
                
                recorder.startRecording()
                
                # Advance to max duration
                mock_millis.advance(5000)
                
                # Should still be recording (5 seconds is under 10 second limit)
                assert recorder.isRecording()
                
                # Advance beyond max duration
                mock_millis.advance(6000)
                
                # Should have stopped due to max duration
                assert not recorder.isRecording()


def test_recorder_button_state():
    """Test button state detection."""
    from src.Recorder import Recorder
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        with patch('pinMode'):
            with patch('digitalRead', return_value=0):
                recorder = Recorder()
                
                # Button not pressed (assuming active low)
                assert not recorder.isButtonPressed()
                
                # Button pressed
                with patch('digitalRead', return_value=1):
                    assert recorder.isButtonPressed()


def test_recorder_reset():
    """Test resetting recorder state."""
    from src.Recorder import Recorder
    
    mock_millis = MockMillis()
    
    with patch('millis', mock_millis):
        with patch('pinMode'):
            with patch('analogRead', return_value=0):
                recorder = Recorder()
                
                recorder.startRecording()
                mock_millis.advance(1000)
                recorder.stopRecording()
                
                assert recorder.getRecordingTime() > 0
                
                recorder.reset()
                
                assert recorder.getRecordingTime() == 0
                assert not recorder.isRecording()

"""Test TextStateManager class algorithms."""

import sys
sys.path.insert(0, 'tests')

from embedded_mocks import ArduinoMock, millis_mock


class TextStateManager:
    """Python reimplementation of TextStateManager for testing."""
    
    class DisplayState:
        IDLE = "IDLE"
        RECORDING = "RECORDING"
        THINKING = "THINKING"
        RESPONSE = "RESPONSE"
        ERROR = "ERROR"
    
    def __init__(self):
        self.currentState = self.DisplayState.IDLE
        self.lastUpdateTime = 0
        self.periodCount = 0
        self.maxPeriods = 10
        self.responseStartTime = 0
        self.responseDisplayDuration = 5000  # 5 seconds
        self.lastGeneratedText = ""
        self.responseText = ""
    
    def update(self, currentTime):
        """Update text based on current state and time."""
        if self.currentState == self.DisplayState.RECORDING:
            self._updateRecordingText(currentTime)
        elif self.currentState == self.DisplayState.THINKING:
            self._updateThinkingText(currentTime)
        elif self.currentState == self.DisplayState.RESPONSE:
            self._updateResponseText(currentTime)
    
    def setState(self, newState, response=""):
        """Set new state and reset timers."""
        self.currentState = newState
        current_time = millis_mock.get()
        
        if newState == self.DisplayState.RECORDING:
            self.lastUpdateTime = current_time - 1000  # Trigger first update immediately
            self.periodCount = self.maxPeriods
        elif newState == self.DisplayState.THINKING:
            self.lastUpdateTime = current_time - 500  # Trigger first update immediately
            self.periodCount = 0
        elif newState == self.DisplayState.RESPONSE:
            self.lastUpdateTime = current_time
            self.responseText = response
            self.responseStartTime = current_time - 1  # Ensure duration check works
        else:
            self.lastUpdateTime = current_time
            self.periodCount = 0
    
    def getState(self):
        """Get current state."""
        return self.currentState
    
    def getCurrentText(self):
        """Get current text based on state."""
        if self.currentState == self.DisplayState.IDLE:
            return "Magic\nGPT8\n\nShake me"
        elif self.currentState == self.DisplayState.ERROR:
            return "Wifi: X"
        elif self.currentState == self.DisplayState.RESPONSE:
            return self.responseText
        else:
            return self.lastGeneratedText
    
    def _updateRecordingText(self, currentTime):
        """Update recording state text."""
        if currentTime - self.lastUpdateTime >= 1000:
            self.lastUpdateTime = currentTime
            self.periodCount = max(0, self.periodCount - 1)
            
            if self.periodCount <= 2:
                self.lastGeneratedText = "Thinking"
            else:
                text = "Speak Now"
                for i in range(self.periodCount):
                    text += " ."
                self.lastGeneratedText = text
    
    def _updateThinkingText(self, currentTime):
        """Update thinking state text."""
        if currentTime - self.lastUpdateTime >= 500:
            self.lastUpdateTime = currentTime
            self.periodCount = (self.periodCount + 1) % 4
            
            text = "Thinking"
            for i in range(self.periodCount):
                text += "."
            self.lastGeneratedText = text
    
    def _updateResponseText(self, currentTime):
        """Update response state text."""
        if currentTime - self.responseStartTime >= self.responseDisplayDuration:
            self.setState(self.DisplayState.IDLE)


def test_initial_state():
    """Test that initial state is IDLE."""
    manager = TextStateManager()
    assert manager.getState() == TextStateManager.DisplayState.IDLE


def test_idle_text():
    """Test idle state text."""
    manager = TextStateManager()
    text = manager.getCurrentText()
    assert "Magic" in text
    assert "GPT8" in text
    assert "Shake me" in text


def test_recording_state():
    """Test recording state text generation."""
    manager = TextStateManager()
    manager.setState(TextStateManager.DisplayState.RECORDING)
    
    # After 1 second, period count should decrease
    millis_mock.current_time = 1000
    manager.update(1000)
    
    text = manager.getCurrentText()
    assert "Speak Now" in text
    assert "." in text


def test_recording_state_periods():
    """Test that period count decreases over time in recording state."""
    manager = TextStateManager()
    manager.setState(TextStateManager.DisplayState.RECORDING)
    
    # Initial period count should be maxPeriods (10)
    assert manager.periodCount == 10
    
    # After 8 seconds (8 updates), period count should be 2
    millis_mock.current_time = 8000
    for i in range(8):
        manager.update((i + 1) * 1000)
    
    assert manager.periodCount == 2
    text = manager.getCurrentText()
    assert text == "Thinking"


def test_thinking_state():
    """Test thinking state text with periods."""
    manager = TextStateManager()
    manager.setState(TextStateManager.DisplayState.THINKING)
    
    # After 500ms, should have 1 period
    millis_mock.current_time = 500
    manager.update(500)
    
    text = manager.getCurrentText()
    assert "Thinking." in text


def test_thinking_state_period_cycle():
    """Test that thinking state cycles through 0-3 periods."""
    manager = TextStateManager()
    manager.setState(TextStateManager.DisplayState.THINKING)
    
    # Test period cycle: 0 -> 1 -> 2 -> 3 -> 0
    millis_mock.current_time = 0
    manager.update(0)
    assert manager.periodCount == 1
    
    millis_mock.current_time = 500
    manager.update(500)
    assert manager.periodCount == 2
    
    millis_mock.current_time = 1000
    manager.update(1000)
    assert manager.periodCount == 3
    
    millis_mock.current_time = 1500
    manager.update(1500)
    assert manager.periodCount == 0


def test_response_state_duration():
    """Test response state auto-transition after duration."""
    manager = TextStateManager()
    manager.setState(TextStateManager.DisplayState.RESPONSE, "Yes")
    
    assert manager.currentState == TextStateManager.DisplayState.RESPONSE
    assert manager.responseText == "Yes"
    
    # After 5000ms, should transition back to IDLE
    millis_mock.current_time = 5000
    manager.update(5000)
    
    assert manager.getState() == TextStateManager.DisplayState.IDLE


def test_error_state():
    """Test error state text."""
    manager = TextStateManager()
    manager.setState(TextStateManager.DisplayState.ERROR)
    
    text = manager.getCurrentText()
    assert text == "Wifi: X"


def test_value_mapping():
    """Test that value mapping works correctly."""
    assert ArduinoMock.map(512, 0, 1023, 0, 100) == 50
    assert ArduinoMock.map(0, 0, 1023, 0, 100) == 0
    assert ArduinoMock.map(1023, 0, 1023, 0, 100) == 100
    assert ArduinoMock.map(256, 0, 1023, 0, 100) == 25


def test_constrain():
    """Test that constrain works correctly."""
    assert ArduinoMock.constrain(50, 0, 100) == 50
    assert ArduinoMock.constrain(-10, 0, 100) == 0
    assert ArduinoMock.constrain(150, 0, 100) == 100

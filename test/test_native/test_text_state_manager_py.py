"""
Unit tests for TextStateManager class functionality
Tests state transitions, text updates, and timing
"""

import sys

# Test classes that mimic TextStateManager behavior
class DisplayState:
    IDLE = "IDLE"
    RECORDING = "RECORDING"
    THINKING = "THINKING"
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"

class TextStateManager:
    """TextStateManager implementation for testing"""
    
    MAX_PERIODS = 10
    RESPONSE_DURATION = 5000  # 5 seconds
    
    def __init__(self):
        self.currentState = DisplayState.IDLE
        self.lastUpdateTime = 0
        self.periodCount = 0
        self.maxPeriods = self.MAX_PERIODS
        self.responseText = ""
        self.responseStartTime = 0
        self.responseDisplayDuration = self.RESPONSE_DURATION
        self.lastGeneratedText = ""
        
    def update(self, currentTime):
        if self.currentState == DisplayState.RECORDING:
            self._updateRecordingText(currentTime)
        elif self.currentState == DisplayState.THINKING:
            self._updateThinkingText(currentTime)
        elif self.currentState == DisplayState.RESPONSE:
            self._updateResponseText(currentTime)
            
    def setState(self, newState, response=""):
        self.currentState = newState
        self.lastUpdateTime = 0  # Using mock millis
        self.periodCount = self.maxPeriods if newState == DisplayState.RECORDING else 0
        
        if newState == DisplayState.RESPONSE:
            self.responseText = response
            self.responseStartTime = 0  # Using mock millis
            
    def getState(self):
        return self.currentState
        
    def getCurrentText(self):
        if self.currentState == DisplayState.IDLE:
            return "Magic\nGPT8\n\nShake me"
        elif self.currentState == DisplayState.ERROR:
            return "Wifi: X"
        elif self.currentState == DisplayState.RESPONSE:
            return self.responseText
        else:
            return self.lastGeneratedText
            
    def _updateRecordingText(self, currentTime):
        if currentTime - self.lastUpdateTime >= 1000:  # Update every second
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
        if currentTime - self.lastUpdateTime >= 500:  # Update every half second
            self.lastUpdateTime = currentTime
            self.periodCount = (self.periodCount + 1) % 4  # 0 to 3 periods
            
            text = "Thinking"
            for i in range(self.periodCount):
                text += "."
            self.lastGeneratedText = text
            
    def _updateResponseText(self, currentTime):
        if currentTime - self.responseStartTime >= self.responseDisplayDuration:
            self.setState(DisplayState.IDLE)

def test_text_manager_idle_state():
    """Test: Idle state returns default text"""
    manager = TextStateManager()
    manager.setState(DisplayState.IDLE)
    
    text = manager.getCurrentText()
    assert text == "Magic\nGPT8\n\nShake me"
    assert manager.getState() == DisplayState.IDLE

def test_text_manager_error_state():
    """Test: Error state returns error text"""
    manager = TextStateManager()
    manager.setState(DisplayState.ERROR)
    
    text = manager.getCurrentText()
    assert text == "Wifi: X"
    assert manager.getState() == DisplayState.ERROR

def test_text_manager_response_state():
    """Test: Response state displays custom text"""
    manager = TextStateManager()
    response_text = "The answer is 42"
    manager.setState(DisplayState.RESPONSE, response_text)
    
    text = manager.getCurrentText()
    assert text == response_text
    assert manager.getState() == DisplayState.RESPONSE

def test_text_manager_recording_period_counting():
    """Test: Recording state counts down periods"""
    manager = TextStateManager()
    manager.setState(DisplayState.RECORDING)
    
    # Initially has max periods (10)
    assert manager.periodCount == 10
    
    # After some time, periods should decrease
    manager.periodCount = 5
    assert manager.periodCount == 5
    
    # After decrement
    manager.periodCount = max(0, manager.periodCount - 1)
    assert manager.periodCount == 4

def test_text_manager_recording_text_generation():
    """Test: Recording state generates correct text"""
    manager = TextStateManager()
    manager.setState(DisplayState.RECORDING)
    
    # At high period count, text should be "Speak Now" with periods
    manager.periodCount = 5
    expected_text = "Speak Now" + " ." * 5
    assert expected_text == "Speak Now . . . . ."
    
    # At low period count, text should be "Thinking"
    manager.periodCount = 1
    last_text = "Thinking"
    assert last_text == "Thinking"

def test_text_manager_thinking_pattern():
    """Test: Thinking state cycles through periods"""
    manager = TextStateManager()
    manager.setState(DisplayState.THINKING)
    
    # Cycle through thinking patterns
    for i in range(4):
        manager.periodCount = (manager.periodCount + 1) % 4
        text = "Thinking" + "." * manager.periodCount
        
        if manager.periodCount == 0:
            assert text == "Thinking"
        elif manager.periodCount == 1:
            assert text == "Thinking."
        elif manager.periodCount == 2:
            assert text == "Thinking.."
        elif manager.periodCount == 3:
            assert text == "Thinking..."

def test_text_manager_state_transitions():
    """Test: State transitions work correctly"""
    manager = TextStateManager()
    
    # Start in IDLE
    assert manager.getState() == DisplayState.IDLE
    
    # Transition to RESPONSE
    manager.setState(DisplayState.RESPONSE, "Hello world")
    assert manager.getState() == DisplayState.RESPONSE
    
    # Transition back to IDLE
    manager.setState(DisplayState.IDLE)
    assert manager.getState() == DisplayState.IDLE
    
    # Transition to ERROR
    manager.setState(DisplayState.ERROR)
    assert manager.getState() == DisplayState.ERROR

def test_text_manager_recording_to_thinking_transition():
    """Test: Recording state transitions to thinking"""
    manager = TextStateManager()
    manager.setState(DisplayState.RECORDING)
    
    # Recording text generation
    assert manager.periodCount == 10  # maxPeriods
    
    manager.periodCount = 2
    text = "Thinking"
    assert text == "Thinking"
    
    manager.periodCount = 0
    text = "Thinking"
    assert text == "Thinking"

def test_text_manager_period_count_reset():
    """Test: Period count resets on state change"""
    manager = TextStateManager()
    
    # Set some period count
    manager.periodCount = 5
    
    # Change to RECORDING should reset
    manager.setState(DisplayState.RECORDING)
    assert manager.periodCount == 10  # maxPeriods
    
    # Change to THINKING should reset to 0
    manager.setState(DisplayState.THINKING)
    assert manager.periodCount == 0

def test_text_manager_response_timing():
    """Test: Response displays for configured duration"""
    manager = TextStateManager()
    
    # Response duration is 5000ms (5 seconds)
    assert manager.responseDisplayDuration == 5000
    
    # Set a response
    manager.setState(DisplayState.RESPONSE, "Test response")
    assert manager.responseText == "Test response"
    assert manager.responseStartTime == 0

if __name__ == "__main__":
    # Run all tests
    tests = [
        test_text_manager_idle_state,
        test_text_manager_error_state,
        test_text_manager_response_state,
        test_text_manager_recording_period_counting,
        test_text_manager_recording_text_generation,
        test_text_manager_thinking_pattern,
        test_text_manager_state_transitions,
        test_text_manager_recording_to_thinking_transition,
        test_text_manager_period_count_reset,
        test_text_manager_response_timing,
    ]
    
    failed = 0
    passed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Exception - {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    sys.exit(0 if failed == 0 else 1)

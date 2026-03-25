#include <unity.h>
#include <string>
#include <vector>
#include <map>

// Test TextStateManager functionality
class TestTextStateManager {
public:
    enum DisplayState {
        IDLE = 0,
        RECORDING,
        THINKING,
        RESPONSE,
        ERROR
    };
    
    struct TextEntry {
        std::string text;
        DisplayState state;
        unsigned long startTime;
    };
    
private:
    DisplayState currentState;
    std::string currentText;
    unsigned long lastUpdateTime;
    std::vector<TextEntry> history;
    const unsigned long RESPONSE_DISPLAY_DURATION = 7000;
    
public:
    TestTextStateManager() : currentState(IDLE), currentText(""), 
        lastUpdateTime(0) {}
    
    void begin() {
        currentState = IDLE;
        currentText = "Ready";
        lastUpdateTime = millisMock();
        history.clear();
    }
    
    void setState(DisplayState state, const std::string& text = "") {
        // Record state change
        if (!text.empty()) {
            TextEntry entry;
            entry.state = state;
            entry.text = text;
            entry.startTime = millisMock();
            history.push_back(entry);
        }
        
        currentState = state;
        if (!text.empty()) {
            currentText = text;
        }
        lastUpdateTime = millisMock();
    }
    
    void update(unsigned long currentTime) {
        // Handle auto-reset from RESPONSE state
        if (currentState == RESPONSE) {
            if (currentTime - lastUpdateTime >= RESPONSE_DISPLAY_DURATION) {
                currentState = IDLE;
                currentText = "Ready";
            }
        }
        
        // Update text based on state
        switch (currentState) {
            case IDLE:
                if (currentText.empty()) currentText = "Ready";
                break;
            case RECORDING:
                if (currentText.empty()) currentText = "Speak...";
                break;
            case THINKING:
                if (currentText.empty()) currentText = "Thinking...";
                break;
            case RESPONSE:
                if (currentText.empty()) currentText = "Answer";
                break;
            case ERROR:
                if (currentText.empty()) currentText = "Error";
                break;
        }
    }
    
    std::string getCurrentText() {
        return currentText;
    }
    
    DisplayState getState() {
        return currentState;
    }
    
    static unsigned long millisMock() {
        static unsigned long mockTime = 0;
        return mockTime++;
    }
    
    static void setMillisMock(unsigned long time) {
        mockTime = time;
    }
    
    size_t getHistorySize() {
        return history.size();
    }
};

// TextStateManager mock for testing
TestTextStateManager textManager;

void setUp(void) {
    textManager.begin();
    TestTextStateManager::setMillisMock(0);
}

void tearDown(void) {}

void test_text_manager_initialization(void) {
    TEST_ASSERT_EQUAL_STRING("Ready", textManager.getCurrentText().c_str());
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::IDLE, textManager.getState());
}

void test_text_manager_idle_state(void) {
    textManager.setState(TestTextStateManager::IDLE, "Idle message");
    TEST_ASSERT_EQUAL_STRING("Idle message", textManager.getCurrentText().c_str());
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::IDLE, textManager.getState());
}

void test_text_manager_recording_state(void) {
    textManager.setState(TestTextStateManager::RECORDING, "Speak...");
    TEST_ASSERT_EQUAL_STRING("Speak...", textManager.getCurrentText().c_str());
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::RECORDING, textManager.getState());
}

void test_text_manager_thinking_state(void) {
    textManager.setState(TestTextStateManager::THINKING, "Thinking...");
    TEST_ASSERT_EQUAL_STRING("Thinking...", textManager.getCurrentText().c_str());
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::THINKING, textManager.getState());
}

void test_text_manager_response_state(void) {
    textManager.setState(TestTextStateManager::RESPONSE, "It is certain");
    TEST_ASSERT_EQUAL_STRING("It is certain", textManager.getCurrentText().c_str());
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::RESPONSE, textManager.getState());
}

void test_text_manager_error_state(void) {
    textManager.setState(TestTextStateManager::ERROR, "Error occurred");
    TEST_ASSERT_EQUAL_STRING("Error occurred", textManager.getCurrentText().c_str());
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::ERROR, textManager.getState());
}

void test_text_manager_auto_reset_response(void) {
    textManager.setState(TestTextStateManager::RESPONSE, "Test response");
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::RESPONSE, textManager.getState());
    
    // Advance time past response duration
    TestTextStateManager::setMillisMock(7001);
    textManager.update(TestTextStateManager::millisMock());
    
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::IDLE, textManager.getState());
}

void test_text_manager_state_history(void) {
    textManager.setState(TestTextStateManager::IDLE, "Start");
    textManager.setState(TestTextStateManager::RECORDING, "Recording");
    textManager.setState(TestTextStateManager::THINKING, "Thinking");
    
    TEST_ASSERT_EQUAL_UINT(3, textManager.getHistorySize());
}

void test_text_manager_state_transitions(void) {
    // Normal flow: IDLE -> RECORDING -> THINKING -> RESPONSE -> IDLE
    textManager.setState(TestTextStateManager::IDLE, "Ready");
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::IDLE, textManager.getState());
    
    textManager.setState(TestTextStateManager::RECORDING, "Speak");
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::RECORDING, textManager.getState());
    
    textManager.setState(TestTextStateManager::THINKING, "Thinking");
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::THINKING, textManager.getState());
    
    textManager.setState(TestTextStateManager::RESPONSE, "Answer");
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::RESPONSE, textManager.getState());
    
    // After duration, should reset to IDLE
    TestTextStateManager::setMillisMock(7001);
    textManager.update(TestTextStateManager::millisMock());
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::IDLE, textManager.getState());
}

void test_text_manager_default_texts(void) {
    textManager.setState(TestTextStateManager::IDLE, "");
    TEST_ASSERT_EQUAL_STRING("Ready", textManager.getCurrentText().c_str());
    
    textManager.setState(TestTextStateManager::RECORDING, "");
    TEST_ASSERT_EQUAL_STRING("Speak...", textManager.getCurrentText().c_str());
    
    textManager.setState(TestTextStateManager::THINKING, "");
    TEST_ASSERT_EQUAL_STRING("Thinking...", textManager.getCurrentText().c_str());
}

void test_text_manager_response_duration(void) {
    textManager.setState(TestTextStateManager::RESPONSE, "Test", 1000);
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::RESPONSE, textManager.getState());
    
    // Before duration expires
    TestTextStateManager::setMillisMock(1000 + 5000);
    textManager.update(TestTextStateManager::millisMock());
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::RESPONSE, textManager.getState());
    
    // After duration expires
    TestTextStateManager::setMillisMock(1000 + 7001);
    textManager.update(TestTextStateManager::millisMock());
    TEST_ASSERT_EQUAL_UINT(TestTextStateManager::IDLE, textManager.getState());
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_text_manager_initialization);
    RUN_TEST(test_text_manager_idle_state);
    RUN_TEST(test_text_manager_recording_state);
    RUN_TEST(test_text_manager_thinking_state);
    RUN_TEST(test_text_manager_response_state);
    RUN_TEST(test_text_manager_error_state);
    RUN_TEST(test_text_manager_auto_reset_response);
    RUN_TEST(test_text_manager_state_history);
    RUN_TEST(test_text_manager_state_transitions);
    RUN_TEST(test_text_manager_default_texts);
    RUN_TEST(test_text_manager_response_duration);
    
    return UNITY_END();
}

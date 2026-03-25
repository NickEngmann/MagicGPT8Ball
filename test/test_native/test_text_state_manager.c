#include <unity.h>
#include "TextStateManager.h"

// Test text state manager
TextStateManager textManager;

void setUp(void) {
    textManager.setState(TextStateManager::DisplayState::IDLE);
}

void tearDown(void) {}

// Test initialization
void test_text_manager_initialization(void) {
    TextStateManager tm;
    tm.setState(TextStateManager::DisplayState::IDLE);
    TEST_ASSERT_TRUE(true);
}

// Test idle state
void test_text_manager_idle_state(void) {
    textManager.setState(TextStateManager::DisplayState::IDLE);
    TEST_ASSERT_EQUAL_INT(TextStateManager::DisplayState::IDLE, textManager.getState());
}

// Test response state
void test_text_manager_response_state(void) {
    textManager.setState(TextStateManager::DisplayState::RESPONSE, "It is certain");
    TEST_ASSERT_EQUAL_INT(TextStateManager::DisplayState::RESPONSE, textManager.getState());
}

// Test recording state
void test_text_manager_recording_state(void) {
    textManager.setState(TextStateManager::DisplayState::RECORDING);
    TEST_ASSERT_EQUAL_INT(TextStateManager::DisplayState::RECORDING, textManager.getState());
}

// Test thinking state
void test_text_manager_thinking_state(void) {
    textManager.setState(TextStateManager::DisplayState::THINKING);
    TEST_ASSERT_EQUAL_INT(TextStateManager::DisplayState::THINKING, textManager.getState());
}

// Test error state
void test_text_manager_error_state(void) {
    textManager.setState(TextStateManager::DisplayState::ERROR);
    TEST_ASSERT_EQUAL_INT(TextStateManager::DisplayState::ERROR, textManager.getState());
}

// Test state transitions
void test_text_manager_state_transitions(void) {
    textManager.setState(TextStateManager::DisplayState::IDLE);
    TEST_ASSERT_EQUAL_INT(TextStateManager::DisplayState::IDLE, textManager.getState());
    
    textManager.setState(TextStateManager::DisplayState::RECORDING);
    TEST_ASSERT_EQUAL_INT(TextStateManager::DisplayState::RECORDING, textManager.getState());
    
    textManager.setState(TextStateManager::DisplayState::THINKING);
    TEST_ASSERT_EQUAL_INT(TextStateManager::DisplayState::THINKING, textManager.getState());
    
    textManager.setState(TextStateManager::DisplayState::RESPONSE, "Maybe");
    TEST_ASSERT_EQUAL_INT(TextStateManager::DisplayState::RESPONSE, textManager.getState());
    
    textManager.setState(TextStateManager::DisplayState::IDLE);
    TEST_ASSERT_EQUAL_INT(TextStateManager::DisplayState::IDLE, textManager.getState());
}

// Test text update
void test_text_manager_text_update(void) {
    textManager.setState(TextStateManager::DisplayState::IDLE);
    textManager.update(0);
    
    std::string currentText = textManager.getCurrentText();
    TEST_ASSERT_TRUE(currentText.length() > 0);
}

// Test long text truncation
void test_text_manager_long_text(void) {
    std::string longText = "This is a very long response that should be truncated when displayed on the Magic 8 Ball screen";
    textManager.setState(TextStateManager::DisplayState::RESPONSE, longText);
    textManager.update(0);
    
    std::string currentText = textManager.getCurrentText();
    // Text should be truncated to fit display
    TEST_ASSERT_TRUE(currentText.length() <= 30);
}

// Test multiple response states
void test_text_manager_multiple_responses(void) {
    textManager.setState(TextStateManager::DisplayState::RESPONSE, "Yes");
    TEST_ASSERT_EQUAL_STRING("Yes", textManager.getCurrentText().c_str());
    
    textManager.setState(TextStateManager::DisplayState::RESPONSE, "No");
    TEST_ASSERT_EQUAL_STRING("No", textManager.getCurrentText().c_str());
    
    textManager.setState(TextStateManager::DisplayState::RESPONSE, "Maybe");
    TEST_ASSERT_EQUAL_STRING("Maybe", textManager.getCurrentText().c_str());
}

int main(void) {
    UNITY_BEGIN();

    RUN_TEST(test_text_manager_initialization);
    RUN_TEST(test_text_manager_idle_state);
    RUN_TEST(test_text_manager_response_state);
    RUN_TEST(test_text_manager_recording_state);
    RUN_TEST(test_text_manager_thinking_state);
    RUN_TEST(test_text_manager_error_state);
    RUN_TEST(test_text_manager_state_transitions);
    RUN_TEST(test_text_manager_text_update);
    RUN_TEST(test_text_manager_long_text);
    RUN_TEST(test_text_manager_multiple_responses);

    return UNITY_END();
}
